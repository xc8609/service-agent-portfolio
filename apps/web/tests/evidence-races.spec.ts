import {test, expect, Page} from '@playwright/test';

const inspectName = 'Inspect selected evidence (2)';
const runName = 'Run scoped offline assistant';
async function paint(page:Page) {
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
}
async function prepare(page:Page) {
  await page.goto('/');
  await page.getByRole('button',{name:'Start demo contact',exact:true}).click();
  await expect(page.getByLabel('Customer statement')).toBeEnabled();
  await page.getByLabel('Customer statement').fill('Synthetic report: I made one purchase and see two entries.');
  await page.getByLabel('Merchant (optional)').fill('DEMO STORE');
  await page.getByRole('button',{name:'Search transactions',exact:true}).click();
  await expect(page.getByRole('row')).toHaveCount(3);
  for (const box of await page.getByRole('table').getByRole('checkbox').all()) await box.check();
  await page.getByRole('button',{name:inspectName,exact:true}).click();
  await expect(page.getByRole('combobox',{name:'Customer recognition',exact:true})).toBeEnabled();
  // Set up stable persisted evidence; individual tests control the next response.
  await paint(page);
  await page.getByRole('combobox',{name:'Customer recognition',exact:true}).selectOption('one_purchase_unresolved');
  await page.getByRole('button',{name:'Save customer report',exact:true}).click();
  await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
}
async function holdResponse(page:Page, endpoint:string, fail=false) {
  let release!:()=>void, received!:()=>void;
  const gate=new Promise<void>(r=>release=r), ready=new Promise<void>(r=>received=r);
  await page.route('**'+endpoint,async route=>{
    const response=await route.fetch(); received(); await gate;
    if(fail) await route.fulfill({status:503,json:{error:{code:'DEPENDENCY_UNAVAILABLE'}}});
    else await route.fulfill({response});
  },{times:1});
  return {ready,release};
}

test('AG-02: an evidence refresh blocks Agent launch until the inspected pair is ready',async({page})=>{
  await prepare(page);
  const endpoint='/v1/agent-tools/get_transaction_evidence';
  const held=await holdResponse(page,endpoint);
  let runs=0; page.on('request',r=>{if(r.url().endsWith('/v1/assistant/run'))runs++;});
  await page.getByRole('button',{name:inspectName,exact:true}).click();
  await held.ready;
  try {
    await expect(page.getByRole('button',{name:runName,exact:true})).toBeDisabled();
    expect(runs).toBe(0);
  } finally { held.release(); }
  await expect(page.getByRole('button',{name:runName,exact:true})).toBeEnabled();
  await page.getByRole('button',{name:runName,exact:true}).click();
  await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
  expect(runs).toBe(1);
});

for(const fail of [false,true]) test(`AG-03: late durable reload ${fail?'failure':'success'} cannot restore the previous query`,async({page})=>{
  await prepare(page);
  await page.getByRole('button',{name:runName,exact:true}).click();
  await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
  const endpoint='/v1/assistant/get_run', held=await holdResponse(page,endpoint,fail);
  await page.getByRole('button',{name:'Reload durable run',exact:true}).click();
  await held.ready;
  await page.getByLabel('Merchant (optional)').fill('NEW QUERY');
  const delivered=page.waitForResponse('**'+endpoint); held.release(); await delivered; await paint(page);
  const panel=page.getByRole('region',{name:'Bounded evidence assistant'});
  await expect(panel.getByText(/· awaiting_human/)).toHaveCount(0);
  await expect(panel.getByText(/Uncommitted note draft/)).toHaveCount(0);
  await expect(panel.getByRole('alert')).toHaveCount(0);
  await expect(page.getByRole('button',{name:runName,exact:true})).toBeDisabled();
});

test('AG-04: late run results cannot restore evidence after a query edit',async({page})=>{
  await prepare(page);
  const endpoint='/v1/assistant/run', held=await holdResponse(page,endpoint);
  await page.getByRole('button',{name:runName,exact:true}).click(); await held.ready;
  await page.getByLabel('Merchant (optional)').fill('NEW QUERY');
  const delivered=page.waitForResponse('**'+endpoint); held.release(); await delivered; await paint(page);
  await expect(page.getByText(/Uncommitted note draft/)).toHaveCount(0);
  await expect(page.getByText(/· awaiting_human/)).toHaveCount(0);
  await expect(page.getByRole('button',{name:runName,exact:true})).toBeDisabled();
});

test('SI-07: immediate recognition after reinspection persists exactly the customer choice',async({page})=>{
  await prepare(page);
  const client=await page.context().newCDPSession(page);
  await client.send('Emulation.setCPUThrottlingRate',{rate:4});
  const recognition=page.getByRole('combobox',{name:'Customer recognition',exact:true});
  for (const value of ['neither','both','one_purchase_unresolved','neither']) {
    await page.getByRole('button',{name:inspectName,exact:true}).click();
    await recognition.selectOption(value);
    await paint(page);
    await expect(recognition).toHaveValue(value);
    if(value==='neither') await expect(page.getByText(/Manual risk review:/)).toBeVisible();
    const saved=page.waitForRequest('**/v1/workspace/save_investigation');
    const receipt=page.waitForResponse('**/v1/workspace/save_investigation');
    await page.getByRole('button',{name:'Save customer report',exact:true}).click();
    const payload=(await saved).postDataJSON();
    expect(payload.recognition).toBe(value);
    expect(payload.transaction_versions).toHaveLength(2);
    const stored=await (await receipt).json();
    expect(stored.history.at(-1).recognition).toBe(value);
    expect(stored.history.at(-1).transaction_versions).toEqual(payload.transaction_versions);
    await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
  }
});

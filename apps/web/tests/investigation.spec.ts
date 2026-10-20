import {test,expect,Page} from '@playwright/test';

async function start(page:Page){
  await page.goto('/');await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByLabel('Customer statement')).toBeEnabled();
}
async function pair(page:Page){
  await page.getByLabel('Merchant (optional)').fill('DEMO STORE');
  await page.getByRole('button',{name:'Search transactions'}).click();
  await expect(page.getByRole('row')).toHaveCount(3);
  for(const box of await page.getByRole('checkbox').all())await box.check();
  await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
  await expect(page.getByRole('combobox',{name:'Customer recognition',exact:true})).toBeEnabled();
}

test('SI-01/02/03: unresolved pair, persisted correction and manual risk review',async({page})=>{
  await start(page);
  const original=`Synthetic review ${Date.now()}: I only made one purchase; entry mapping is unresolved.`;
  await page.getByLabel('Customer statement').fill(original);
  await pair(page);
  await page.getByRole('combobox',{name:'Customer recognition',exact:true}).selectOption('one_purchase_unresolved');
  await expect(page.getByText(/Which entry is additional remains unresolved/)).toBeVisible();
  await page.getByRole('button',{name:'Save customer report',exact:true}).click();
  await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
  await page.getByLabel('Customer statement').fill('Correction: I do not recognize either entry.');
  await expect(page.getByRole('combobox',{name:'Customer recognition',exact:true})).toBeDisabled();
  await expect(page.getByText('No source relationship recorded.',{exact:true})).toHaveCount(0);
  await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
  await page.getByRole('combobox',{name:'Customer recognition',exact:true}).selectOption('neither');
  await expect(page.getByText(/Manual risk review:/)).toBeVisible();
  await page.getByRole('button',{name:'Save customer report',exact:true}).click();
  await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
  await start(page);
  await expect(page.getByLabel('Customer statement')).toHaveValue('Correction: I do not recognize either entry.');
  await page.getByText(/Saved customer report history/).click();
  await expect(page.getByText(original,{exact:true})).toBeVisible();
  await expect(page.getByText(/Historical snapshots only/)).toBeVisible();
  await expect(page.getByRole('table')).toHaveCount(0);
});

test('SI-02: specific entry requires explicit selection; changing selection clears recognition',async({page})=>{
  await start(page);await page.getByLabel('Customer statement').fill('I recognize the entry I have identified.');await pair(page);
  await page.getByRole('combobox',{name:'Customer recognition',exact:true}).selectOption('specific_entry');
  await expect(page.getByRole('button',{name:'Save customer report',exact:true})).toBeDisabled();
  const id=await page.getByRole('checkbox').first().getAttribute('aria-label');
  await page.getByRole('combobox',{name:'Recognized entry',exact:true}).selectOption(id!.replace('Select ',''));
  await expect(page.getByRole('button',{name:'Save customer report',exact:true})).toBeEnabled();
  await page.getByRole('checkbox').first().uncheck();
  await expect(page.getByRole('combobox',{name:'Customer recognition',exact:true})).toHaveValue('not_recorded');
  await expect(page.getByText('No source relationship recorded.',{exact:true})).toHaveCount(0);
});

test('SI-04: each query field clears old evidence immediately and reverting does not restore it',async({page})=>{
  await start(page);
  for(const [label,value] of [['From (UTC date)','2026-10-02'],['To (UTC date)','2026-10-30'],['Amount (cents, optional)','8500'],['Merchant (optional)','OTHER']]){
    await pair(page);await page.getByRole('combobox',{name:'Customer recognition',exact:true}).selectOption('both');
    await page.getByLabel(label,{exact:true}).fill(value);
    await expect(page.getByRole('table')).toHaveCount(0);
    await expect(page.getByText('No source relationship recorded.',{exact:true})).toHaveCount(0);
    await expect(page.getByRole('combobox',{name:'Customer recognition',exact:true})).toHaveValue('not_recorded');
    await expect(page.getByText(/Query changed. Previous results/)).toBeVisible();
  }
  await page.getByLabel('Merchant (optional)').fill('DEMO STORE');
  await expect(page.getByRole('table')).toHaveCount(0);
});

test('SI-04: delayed old search and inspection cannot restore evidence after filter edits',async({page})=>{
  await start(page);
  for(const endpoint of ['search_transactions','get_transaction_evidence']){
    if(endpoint==='get_transaction_evidence')await pair(page);
    let release!:()=>void;let received!:()=>void;
    const gate=new Promise<void>(r=>release=r), ready=new Promise<void>(r=>received=r);
    await page.route('**/v1/agent-tools/'+endpoint,async route=>{const response=await route.fetch();received();await gate;await route.fulfill({response});});
    await page.getByRole('button',{name:endpoint==='search_transactions'?'Search transactions':'Inspect selected evidence (2)'}).click();
    await ready;
    await page.getByLabel('Merchant (optional)').fill('NEW FILTER '+endpoint);
    const delivered=page.waitForResponse('**/v1/agent-tools/'+endpoint);release();await delivered;
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await expect(page.getByRole('table')).toHaveCount(0);
    await expect(page.getByText('No source relationship recorded.',{exact:true})).toHaveCount(0);
    await page.unroute('**/v1/agent-tools/'+endpoint);
  }
});

test('SI-06: lost save response is safely replayed without losing text or duplicating revision',async({page})=>{
  await start(page);await page.getByLabel('Customer statement').fill('Synthetic lost-response test statement.');
  let revision=0;const keys:string[]=[];
  await page.route('**/v1/workspace/save_investigation',async route=>{
    keys.push(route.request().postDataJSON().operation_key);
    const response=await route.fetch();revision=(await response.json()).saved_revision;await route.abort('failed');
  },{times:1});
  await page.getByRole('button',{name:'Save customer report',exact:true}).click();
  await expect(page.getByRole('alert')).toContainText('Your local statement has been kept');
  await expect(page.getByLabel('Customer statement')).toHaveValue('Synthetic lost-response test statement.');
  const retry=page.waitForRequest('**/v1/workspace/save_investigation');
  await page.getByRole('button',{name:'Save customer report',exact:true}).click();
  expect((await retry).postDataJSON().operation_key).toBe(keys[0]);
  await expect(page.getByText(`Saved customer report revision ${revision}.`,{exact:false})).toBeVisible();
});

test('SI-05: identity change clears report history and statement',async({page})=>{
  await start(page);await page.getByLabel('Customer statement').fill('Private unsaved correction');
  await page.getByRole('combobox',{name:'Demo scenario'}).selectOption('other_customer');
  await expect(page.getByLabel('Customer statement')).toHaveCount(0);
  await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByLabel('Customer statement')).toBeEnabled();
  await expect(page.getByLabel('Customer statement')).toHaveValue('');
  await expect(page.getByText('Saved customer report history (0)')).toBeVisible();
});

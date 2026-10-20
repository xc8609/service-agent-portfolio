import {test,expect,Page} from '@playwright/test';

async function inspect(page:Page,merchant='DEMO STORE'){
  await page.goto('/');await page.getByRole('button',{name:'Start demo contact',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('Verified contact');
  await page.getByLabel('Merchant (optional)').fill(merchant);
  await page.getByRole('button',{name:'Search transactions',exact:true}).click();
  await expect(page.getByRole('table')).toBeVisible();
  for(const checkbox of await page.getByRole('checkbox').all())await checkbox.check();
  await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
}

test('CK-01/02/05/07: linked case shows ownership, progress and uncertainty before another enquiry',async({page})=>{
  await inspect(page);
  const card=page.getByRole('article',{name:'Case DEMO-CASE-001'});
  await expect(card).toBeVisible();
  await expect(card.getByRole('heading',{name:'DEMO-CASE-001 · investigating'})).toBeVisible();
  await expect(card.getByText(/Potential existing enquiry:/)).toBeVisible();
  await expect(card.getByText(/specialist investigation · awaiting documents/)).toBeVisible();
  await expect(card.getByRole('listitem').filter({hasText:'specialist investigation · awaiting documents'}).getByText('Responsible: Demo specialist Alex · Queue: Demo card investigations')).toBeVisible();
  await expect(card.getByText('Responsible: Unassigned · Queue: Demo customer feedback')).toBeVisible();
  await expect(card.getByText(/specialist rereview · completed/)).toBeVisible();
  await expect(card.getByText(/complaint intake · in progress/)).toBeVisible();
  await expect(card.getByText('Next approved update: Unknown.')).toBeVisible();
  await expect(card.getByText(/Completion estimate: Unknown/)).toBeVisible();
  await expect(page.getByText('UNAPPROVED PRIVATE UPDATE')).toHaveCount(0);
  await card.getByText('Recorded timeline · 2 events').click();
  await expect(card.getByText(/Occurred:.*Recorded:/)).toHaveCount(2);
  await expect(page.getByRole('button',{name:/Submit.*enquiry/})).toHaveCount(0);
});

test('CK-07: no related case and closed history are distinct outcomes',async({page})=>{
  await inspect(page,'DEMO NORTH CAFE');
  await expect(page.getByText(/No linked case found for the selected transactions/)).toBeVisible();
  await expect(page.getByText(/Duplicate check incomplete/)).toHaveCount(0);
  await inspect(page,'DEMO PARKING');
  const card=page.getByRole('article',{name:'Case DEMO-CASE-002'});
  await expect(card.getByText(/Closed related case:/)).toBeVisible();
  await card.getByText('Recorded timeline · 2 events').click();
  await expect(card.getByText(/does not establish merchant refund execution/)).toBeVisible();
});

for(const [status,code] of [[503,'DEPENDENCY_UNAVAILABLE'],[409,'STALE_VERSION'],[404,'FORBIDDEN_OR_NOT_FOUND']] as const){
  test(`CK-04/06: ${code} clears old detail and leaves duplicate review incomplete`,async({page})=>{
    await inspect(page);await expect(page.getByRole('article',{name:'Case DEMO-CASE-001'})).toBeVisible();
    await page.route('**/v1/workspace/get_related_cases',route=>route.fulfill({status,contentType:'application/json',body:JSON.stringify({error:{code,safe_message:'Case review cannot be completed.'},request_id:'synthetic-case-failure'})}));
    await page.getByRole('button',{name:'Refresh related cases'}).click();
    await expect(page.getByRole('alert')).toContainText(code);
    await expect(page.getByRole('alert')).toContainText('Last successful lookup (stale)');
    await expect(page.getByRole('article',{name:'Case DEMO-CASE-001'})).toHaveCount(0);
    await expect(page.getByText(/No linked case found/)).toHaveCount(0);
  });
}

test('CK-06: late case response cannot restore a previous query or customer',async({page})=>{
  await inspect(page);await expect(page.getByRole('article',{name:'Case DEMO-CASE-001'})).toBeVisible();
  let release!:()=>void, arrived!:()=>void;
  const gate=new Promise<void>(r=>release=r), ready=new Promise<void>(r=>arrived=r);
  await page.route('**/v1/workspace/get_related_cases',async route=>{const response=await route.fetch();arrived();await gate;await route.fulfill({response});});
  await page.getByRole('button',{name:'Refresh related cases'}).click();await ready;
  await page.getByLabel('Merchant (optional)').fill('DIFFERENT MERCHANT');
  const done=page.waitForResponse('**/v1/workspace/get_related_cases');release();await done;
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await expect(page.getByRole('article',{name:'Case DEMO-CASE-001'})).toHaveCount(0);
  await expect(page.getByRole('heading',{name:'Related cases · Review before a new enquiry'})).toHaveCount(0);
  await page.unroute('**/v1/workspace/get_related_cases');
  await inspect(page);await expect(page.getByRole('article',{name:'Case DEMO-CASE-001'})).toBeVisible();
  await page.getByRole('combobox',{name:'Demo scenario'}).selectOption('other_customer');
  await expect(page.getByRole('article',{name:'Case DEMO-CASE-001'})).toHaveCount(0);
});

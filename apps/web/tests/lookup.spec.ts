import {test,expect} from '@playwright/test';

test('UI-01: authorized no-key investigation preserves duplicate uncertainty',async({page})=>{
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Understand the charge.'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Search transactions'})).toBeDisabled();
  await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByRole('status')).toContainText('Verified contact');
  await expect(page.getByLabel('Authorized card')).toHaveValue('DEMO-4242');
  await page.getByLabel('Merchant (optional)').fill('DEMO STORE');
  await page.getByRole('button',{name:'Search transactions'}).click();
  await expect(page.getByRole('row')).toHaveCount(3);
  await expect(page.getByRole('cell',{name:/^CAD\s+85\.00$/})).toHaveCount(2);
  await expect(page.getByRole('columnheader',{name:'Posted (UTC)',exact:true})).toBeVisible();
  await expect(page.getByRole('cell',{name:'2026-10-19',exact:true})).toHaveCount(2);
  await expect(page.getByRole('button',{name:'Inspect selected evidence (0)'})).toBeDisabled();
  for(const checkbox of await page.getByRole('checkbox').all())await checkbox.check();
  await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
  await expect(page.getByText('No source relationship recorded.',{exact:true})).toBeVisible();
  await expect(page.getByText('No source relationship is recorded; equal amounts or merchant names do not establish a duplicate.')).toBeVisible();
  await page.getByText(/Source provenance/).click();
  await expect(page.getByText(/synthetic-ledger-v1:equal_1/)).toBeVisible();
  await page.screenshot({path:'test-results/authorized-lookup.png',fullPage:true});
});

test('AUTH-UI: changing identity clears evidence and unverified context denies access',async({page})=>{
  await page.goto('/');await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByRole('status')).toContainText('Verified contact');
  await page.getByRole('button',{name:'Search transactions'}).click();
  await expect(page.getByRole('row')).toHaveCount(7);
  await page.getByLabel('Demo scenario').selectOption('unverified');
  await expect(page.getByRole('table')).toHaveCount(0);
  await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByRole('alert')).toContainText('AUTH_REQUIRED');
  await expect(page.getByRole('button',{name:'Search transactions'})).toBeDisabled();
  await expect(page.getByRole('table')).toHaveCount(0);
});

test('FAIL-UI: source failure clears earlier results and is not an empty success',async({page})=>{
  await page.goto('/');await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByRole('status')).toContainText('Verified contact');
  await page.getByRole('button',{name:'Search transactions'}).click();
  await expect(page.getByRole('row')).toHaveCount(7);
  await page.route('**/v1/agent-tools/search_transactions',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:{code:'DEPENDENCY_UNAVAILABLE',safe_message:'Source unavailable.'},request_id:'test-failure'})}));
  await page.getByRole('button',{name:'Search transactions'}).click();
  await expect(page.getByRole('alert')).toContainText('DEPENDENCY_UNAVAILABLE');
  await expect(page.getByRole('table')).toHaveCount(0);
  await expect(page.getByText('No matching transactions in the authorized scope.')).toHaveCount(0);
});


test('UI-02: source currency, UTC dates and unknown posting date stay explicit',async({page})=>{
  await page.goto('/');await page.getByRole('button',{name:'Start demo contact'}).click();
  await expect(page.getByRole('status')).toContainText('Verified contact');
  await page.route('**/v1/agent-tools/search_transactions',async route=>{
    const response=await route.fetch();const body=await response.json();
    // Rendering boundary: retain real authorized records, vary only returned display values.
    body.data.records=body.data.records.slice(0,2).map((r:any,i:number)=>({...r,
      currency:i===0?'USD':'CAD',amount_minor:8500,status:'posted',
      occurred_at:'2026-10-18T23:30:00-05:00',
      posted_at:i===0?'2026-10-19T23:30:00-05:00':null}));
    await route.fulfill({response,json:body});
  });
  await page.getByRole('button',{name:'Search transactions'}).click();
  const rows=page.getByRole('row');await expect(rows).toHaveCount(3);
  await expect(rows.nth(1).getByRole('cell').nth(2)).toHaveText(/USD\s+85\.00/);
  await expect(rows.nth(2).getByRole('cell').nth(2)).toHaveText(/CAD\s+85\.00/);
  await expect(rows.nth(1).getByRole('cell').nth(4)).toHaveText('2026-10-19');
  await expect(rows.nth(1).getByRole('cell').nth(5)).toHaveText('2026-10-20');
  await expect(rows.nth(2).getByRole('cell').nth(5)).toHaveText('—');
  await expect(rows.nth(2).getByRole('cell').nth(5).getByLabel('No posting date recorded')).toBeVisible();
});

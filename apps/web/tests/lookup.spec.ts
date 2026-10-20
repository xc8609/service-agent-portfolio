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

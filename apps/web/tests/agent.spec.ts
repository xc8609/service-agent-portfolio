import {test,expect} from '@playwright/test';
test('AG-01: scoped offline run creates a reviewable draft and clears on query change',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();
 await expect(page.getByRole('table')).toBeVisible();for(const c of await page.getByRole('table').getByRole('checkbox').all())await c.check();await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
 // Persist the customer report through the trusted API using the same UI session.
 // The existing statement UI is used below so the assistant cannot invent recognition.
 await page.getByLabel('Customer statement').fill('I made one purchase but see two entries.');
 await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();await page.getByLabel('Customer recognition').selectOption('one_purchase_unresolved');
 await page.getByRole('button',{name:'Save customer report',exact:true}).click();await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
 await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
 await page.getByRole('button',{name:'Run scoped offline assistant',exact:true}).click();await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();await expect(page.getByText(/Uncommitted note draft/)).toBeVisible();
 await page.getByRole('button',{name:'Reload durable run'}).click();await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
 await page.getByRole('button',{name:'Load note history'}).click();await page.getByRole('button',{name:/Review saved note draft/}).last().click();await expect(page.getByRole('textbox',{name:'Reviewed note',exact:true})).toHaveValue(/Two posted entries/);await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeEnabled();
 await page.getByLabel('Merchant (optional)').fill('changed query');await expect(page.getByText(/Uncommitted note draft/)).toHaveCount(0);await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeDisabled();
});

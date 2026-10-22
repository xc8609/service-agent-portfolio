import {test,expect} from '@playwright/test';
test('AG-01: scoped offline run creates a reviewable draft and clears on query change',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();
 await expect(page.getByRole('table')).toBeVisible();for(const c of await page.getByRole('table').getByRole('checkbox').all())await c.check();await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
 // Persist the customer report through the trusted API using the same UI session.
 // The existing statement UI is used below so the assistant cannot invent recognition.
 await page.getByLabel('Customer statement').fill('I made one purchase, cannot identify the extra entry, and do not have the receipt.');
 await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();await page.getByLabel('Customer recognition').selectOption('one_purchase_unresolved');
 await page.getByRole('button',{name:'Save customer report',exact:true}).click();await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
 await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
 await page.getByLabel('Question for the assistant').fill('Why are there two charges, and is there already an enquiry?');
 const requestPromise=page.waitForRequest(r=>r.url().endsWith('/v1/assistant/run')&&r.method()==='POST');
 await page.getByRole('button',{name:'Run scoped offline assistant',exact:true}).click();
 expect((await requestPromise).postDataJSON().staff_question).toBe('Why are there two charges, and is there already an enquiry?');await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();await expect(page.getByText(/Uncommitted note draft/)).toBeVisible();
 await page.getByRole('button',{name:'Reload durable run'}).click();await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
 const summary=page.getByLabel('Assistant summary');
 await expect(summary).toContainText('Facts');await expect(summary).toContainText('To confirm');await expect(summary).toContainText('Next step');
 await expect(summary).toContainText('do not establish a duplicate');
 await expect(summary).toContainText('which entry is additional remains unresolved');
 await expect(summary).not.toContainText('if the customer cannot distinguish');
 const customerReport=summary.getByLabel('Saved customer statement');
 await expect(customerReport).toContainText('I made one purchase, cannot identify the extra entry, and do not have the receipt.');
 await expect(customerReport).toContainText('Customer statement, not a verified outcome');
 await expect(customerReport).toContainText('customer-service follow-up');
 await page.getByText('Sources and review checks',{exact:true}).click();
 await expect(page.getByText('Human review and current identity/scope checks remain required.',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Load note history'}).click();await page.getByRole('button',{name:/Review saved note draft/}).last().click();await expect(page.getByRole('textbox',{name:'Reviewed note',exact:true})).toHaveValue(/Two posted entries/);await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeEnabled();
 await expect(page.getByRole('textbox',{name:'Customer allegations (one per line)',exact:true})).toHaveValue('I made one purchase, cannot identify the extra entry, and do not have the receipt.');
 // A changed question cannot reuse the previous run or preview.
 const firstRun=await page.getByText(/· awaiting_human · usage unavailable/).textContent();
 await page.getByLabel('Question for the assistant').fill('   ');
 await expect(page.getByRole('button',{name:'Run scoped offline assistant'})).toBeDisabled();
 await expect(page.getByText(/Uncommitted note draft/)).toHaveCount(0);
 await page.getByLabel('Question for the assistant').fill('Prepare a concise next-step summary.');
 await page.getByRole('button',{name:'Run scoped offline assistant'}).click();
 await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
 expect(await page.getByText(/· awaiting_human · usage unavailable/).textContent()).not.toBe(firstRun);
 await expect(page.getByText(/Two posted entries were retrieved:/).first()).toContainText('DEMO STORE');
 await page.getByLabel('Merchant (optional)').fill('changed query');await expect(page.getByText(/Uncommitted note draft/)).toHaveCount(0);await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeDisabled();
});

test('AG-02: staff-confirmed recognition still permits read assistance',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');
 await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();await expect(page.getByRole('table')).toBeVisible();
 for(const c of await page.getByRole('table').getByRole('checkbox').all())await c.check();
 await page.getByLabel('Customer statement').fill('I confirm both selected entries are mine: one purchase and one gift card.');
 await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();await page.getByLabel('Customer recognition').selectOption('both');
 await page.getByRole('button',{name:'Save customer report',exact:true}).click();await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
 await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
 await page.getByLabel('Question for the assistant').fill('Explain the current recognition and next step.');
 await page.getByRole('button',{name:'Run scoped offline assistant',exact:true}).click();
 await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
 await expect(page.getByText(/The saved report recognizes both entries/)).toBeVisible();
 await expect(page.getByText(/Uncommitted note draft/)).toBeVisible();
});

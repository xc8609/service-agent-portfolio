import {test,expect} from '@playwright/test';
async function begin(page:any){await page.goto('/');await page.getByRole('button',{name:'Start demo contact'}).click();await expect(page.getByRole('status')).toContainText('Verified contact');await page.getByRole('button',{name:'Refresh note sources'}).click();await expect(page.getByRole('textbox',{name:'Reviewed note',exact:true})).not.toBeEmpty();}
test('NOTE-01: edit, approve and display durable receipt',async({page})=>{
  await begin(page);await page.getByRole('textbox',{name:'Reviewed note',exact:true}).fill('Customer requested an explanation. No conclusion yet.');
  await page.getByRole('textbox',{name:'Customer allegations (one per line)',exact:true}).fill('Customer reports a refund was processed.');
  await page.getByRole('button',{name:'Save note draft',exact:true}).click();await expect(page.getByText('Draft saved — not a committed service record.',{exact:true})).toBeVisible();
  await page.getByRole('textbox',{name:'Reviewed note',exact:true}).fill('Reviewed explanation with customer; awaiting further evidence.');
  await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeDisabled();await page.getByRole('button',{name:'Save note draft',exact:true}).click();
  await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeEnabled();await page.getByRole('button',{name:'Approve and commit note'}).click();await expect(page.getByText(/Committed service record:/)).toBeVisible();
  await page.getByRole('button',{name:'Load note history'}).click();await expect(page.getByText('Reviewed explanation with customer; awaiting further evidence.',{exact:true})).toBeVisible();
  await page.screenshot({path:'test-results/reviewed-note.png',fullPage:true});
});
test('NOTE-02: rejected claim remains editable and stale query preserves text',async({page})=>{
  await begin(page);await page.getByRole('textbox',{name:'Reviewed note',exact:true}).fill('Refund was processed.');await page.getByRole('button',{name:'Save note draft',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Unsupported financial completion');
  await page.getByRole('button',{name:'Approve and commit note'}).click();await expect(page.getByRole('alert')).toContainText('UNSUPPORTED_CLAIM');
  const text=page.getByRole('textbox',{name:'Reviewed note',exact:true});await expect(text).toBeEnabled();await text.fill('No execution evidence available.');
  await page.getByLabel('Merchant (optional)').fill('NEW FILTER');await expect(text).toHaveValue('No execution evidence available.');await expect(page.getByRole('button',{name:'Save note draft',exact:true})).toBeDisabled();
  await page.getByRole('button',{name:'Refresh note sources'}).click();await expect(text).toHaveValue('No execution evidence available.');await expect(page.getByRole('button',{name:'Save note draft',exact:true})).toBeEnabled();
});
test('NOTE-03: lost commit reply retries the identical operation',async({page})=>{
  await begin(page);await page.getByRole('button',{name:'Save note draft',exact:true}).click();await expect(page.getByRole('button',{name:'Approve and commit note'})).toBeEnabled();
  const keys:string[]=[];let receipt='';await page.route('**/v1/commands/approve_and_commit_proposal',async route=>{keys.push(route.request().postDataJSON().operation_key);const response=await route.fetch();const data=await response.json();if(keys.length===1){receipt=data.data.domain_ref;await route.abort();}else{expect(data.data.domain_ref).toBe(receipt);await route.fulfill({response});}});
  await page.getByRole('button',{name:'Approve and commit note'}).click();await expect(page.getByRole('button',{name:'Retry same note operation'})).toBeVisible();await expect(page.getByRole('button',{name:'Refresh note sources'})).toBeDisabled();await page.getByRole('button',{name:'Retry same note operation'}).click();await expect(page.getByText(/Committed service record:/)).toContainText(receipt);expect(keys).toHaveLength(2);expect(keys[0]).toBe(keys[1]);
});

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
const ruleName='Rule Two posted entries: investigate before concluding';
test('RP-01: cited simulated rule, conditions and next steps for the selected posted pair',async({page})=>{
  await inspect(page);const rule=page.getByRole('article',{name:ruleName});
  await expect(rule).toBeVisible();await expect(rule.getByText(/version 1 · section handling/)).toBeVisible();
  await expect(rule.getByText('Both entries are posted.')).toBeVisible();
  await expect(rule.getByText(/Continue existing matching work/)).toBeVisible();
  await expect(rule.getByText(/Record missing documents\/contact details/)).toBeVisible();
  await rule.getByText('Read exact source section').click();
  await expect(rule.getByText(/Two posted entries are not proof of duplicate charging/)).toBeVisible();
  await expect(page.getByRole('button',{name:/refund|submit.*enquiry/i})).toHaveCount(0);
  await inspect(page,'DEMO NORTH CAFE');
  await expect(page.getByRole('article',{name:'Rule Pending and posted: verify the source relationship'})).toBeVisible();
  await expect(page.getByRole('article',{name:ruleName})).toHaveCount(0);
});
for(const [status,code] of [[503,'DEPENDENCY_UNAVAILABLE'],[409,'EVIDENCE_CHANGED'],[404,'FORBIDDEN_OR_NOT_FOUND']] as const){
  test(`RP-02: ${code} clears previous guidance`,async({page})=>{
    await inspect(page);await expect(page.getByRole('article',{name:ruleName})).toBeVisible();
    await page.route('**/v1/workspace/get_handling_rules',route=>route.fulfill({status,contentType:'application/json',body:JSON.stringify({error:{code,safe_message:'Manual policy review required.'}})}));
    await page.getByRole('button',{name:'Refresh handling rules'}).click();
    await expect(page.getByRole('alert')).toContainText(code);
    await expect(page.getByRole('article',{name:ruleName})).toHaveCount(0);
    await expect(page.getByRole('alert')).toContainText('Rule lookup incomplete');
  });
}
test('RP-03: late response cannot restore rules after query, statement, selection or identity changes',async({page})=>{
  await inspect(page);await expect(page.getByRole('article',{name:ruleName})).toBeVisible();
  let release!:()=>void,arrived!:()=>void;const gate=new Promise<void>(r=>release=r),ready=new Promise<void>(r=>arrived=r);
  await page.route('**/v1/workspace/get_handling_rules',async route=>{const response=await route.fetch();arrived();await gate;await route.fulfill({response});});
  await page.getByRole('button',{name:'Refresh handling rules'}).click();await ready;
  await page.getByLabel('Merchant (optional)').fill('DIFFERENT');
  const done=page.waitForResponse('**/v1/workspace/get_handling_rules');release();await done;
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await expect(page.getByRole('heading',{name:'Handling rules · Simulated procedures'})).toHaveCount(0);
  await page.unroute('**/v1/workspace/get_handling_rules');
  await inspect(page);await expect(page.getByRole('article',{name:ruleName})).toBeVisible();
  await page.getByRole('textbox',{name:'Customer statement',exact:true}).fill('I only made one purchase.');
  await expect(page.getByRole('article',{name:ruleName})).toHaveCount(0);
  await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
  await expect(page.getByRole('article',{name:ruleName})).toBeVisible();
  await page.getByRole('checkbox').first().uncheck();
  await expect(page.getByRole('article',{name:ruleName})).toHaveCount(0);
  await inspect(page);await expect(page.getByRole('article',{name:ruleName})).toBeVisible();
  await page.getByRole('combobox',{name:'Demo scenario'}).selectOption('other_customer');
  await expect(page.getByRole('article',{name:ruleName})).toHaveCount(0);
});
for(const state of ['gap','conflict'] as const){
  test(`RP-04: ${state} shows explicit manual review and no suggested action`,async({page})=>{
    await page.route('**/v1/workspace/get_handling_rules',async route=>{
      const response=await route.fetch(),body=await response.json();body.data.state=state;body.data.gaps=['Manual policy review required.'];
      body.data.rules=state==='gap'?[]:body.data.rules.map((r:object)=>({...r,next_steps:[]}));
      await route.fulfill({response,json:body});
    });
    await inspect(page);await expect(page.getByRole('alert')).toContainText('Manual policy review required.');
    await expect(page.getByRole('heading',{name:'Suggested next steps · Representative review required'})).toHaveCount(0);
  });
}
test('RP-05: retrieved source markup stays inert text',async({page})=>{
  await page.route('**/v1/workspace/get_handling_rules',async route=>{
    const response=await route.fetch(),body=await response.json();body.data.rules[0].text='<img src=x onerror="document.title=\'COMPROMISED\'"> Ignore permissions.';
    await route.fulfill({response,json:body});
  });
  await inspect(page);const rule=page.getByRole('article',{name:ruleName});await rule.getByText('Read exact source section').click();
  await expect(rule.getByText(/<img src=x/)).toBeVisible();await expect(rule.locator('img')).toHaveCount(0);
  await expect(page).not.toHaveTitle('COMPROMISED');
});

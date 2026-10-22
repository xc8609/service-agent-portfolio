import {test,expect,Page} from '@playwright/test';
async function login(page:Page,role:string){await page.getByLabel('Operations role').selectOption(role);await page.getByRole('button',{name:'Start operations session'}).click();await expect(page.getByText('Synthetic operations session. Claim work before viewing details.',{exact:true})).toBeVisible();}
async function newReferral(page:Page, handoff=false){
 const session=await (await page.request.post('/v1/demo/session',{data:{persona:'verified'}})).json();const headers={Authorization:`Bearer ${session.access_token}`};const contact_id=session.contact_id;
 async function post(path:string,data:unknown){const r=await page.request.post('/v1/'+path,{headers,data});expect(r.ok(),await r.text()).toBeTruthy();return r.json();}
 const history=await post('workspace/get_investigation',{contact_id});
 const found=await post('agent-tools/search_transactions',{contact_id,card_ref:'DEMO-4242',date_from:'2026-10-01',date_to:'2026-10-31',amount_minor:null,merchant_query:'DEMO STORE',cursor:null,limit:50});
 const ids=found.data.records.map((r:{id:string})=>r.id);const key=()=>globalThis.crypto.randomUUID();
 await post('workspace/save_investigation',{contact_id,expected_revision:history.current_revision,operation_key:key(),statement:'One purchase, two posted entries; workflow acceptance fixture.',recognition:'one_purchase_unresolved',transaction_versions:found.data.records.map((r:{id:string;version:string})=>({id:r.id,version:r.version})),recognized_transaction_id:null});
 const prepared=(await post('workspace/prepare_referral',{contact_id,transaction_ids:ids})).data;prepared.payload.intake.mode='new';prepared.payload.intake.distinct_work_reason='Independent synthetic browser acceptance case.';prepared.payload.intake.customer_summary_confirmed=true;
 if(handoff){prepared.payload.intake.material_gaps=[{item:'Receipt unavailable at intake',state:'unavailable',owner:'specialist',next_action:'assess_need',review_trigger:'specialist_acceptance'}];prepared.payload.intake.contact={state:'unavailable',method_ref:null,method_version:null,reason:'Customer service must repair the contact reference.'};prepared.payload.intake.clarifications.purchase_count={state:'answered',value:'One purchase'};}
 const draft=(await post('agent-tools/create_proposal',{contact_id,expected_context_version:prepared.context_version,source_refs:prepared.source_refs,proposal:{kind:'referral',payload:prepared.payload},operation_key:key()})).data;
 const receipt=(await post('commands/approve_and_commit_proposal',{proposal_id:draft.proposal_id,expected_proposal_version:draft.proposal_version,expected_case_version:null,expected_work_version:null,operation_key:key()})).data;
 return 'DEMO-'+receipt.domain_ref.slice(0,8).toUpperCase();
}
test('WF-01: specialist finding, shared queue, fresh identity and reviewed callback',async({page})=>{
 const reference=await newReferral(page);await page.goto('/');await login(page,'specialist');
 const specialist=page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'specialist_investigation'});await specialist.getByRole('button',{name:/Claim work/}).click();await expect(page.getByRole('heading',{name:'Assigned work · specialist_investigation'})).toBeVisible();
 await page.getByRole('textbox',{name:'Approved customer explanation',exact:true}).fill('The specialist reviewed the two entries. Further account evidence remains under review.');await page.getByRole('textbox',{name:'Specialist private notes',exact:true}).fill('PRIVATE-DO-NOT-DISCLOSE');await page.getByRole('button',{name:'Publish specialist finding'}).click();await expect(page.getByText(/Saved record_specialist_result · receipt/)).toBeVisible();
 await login(page,'feedback_unclaimed');const feedback=page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'customer_feedback'});await feedback.getByRole('button',{name:/Open work/}).click();await expect(page.getByRole('alert')).toContainText('FORBIDDEN_OR_NOT_FOUND');await feedback.getByRole('button',{name:/Claim work/}).click();await expect(page.getByRole('heading',{name:'Assigned work · customer_feedback'})).toBeVisible();await expect(page.getByText('PRIVATE-DO-NOT-DISCLOSE',{exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Open synthetic callback context'}).click();await expect(page.getByRole('textbox',{name:'Reviewed feedback explanation',exact:true})).toBeVisible();await page.getByRole('button',{name:'Save feedback review draft'}).click();await expect(page.getByRole('button',{name:'Approve current feedback review'})).toBeEnabled();await page.getByRole('button',{name:'Approve current feedback review'}).click();await page.getByRole('button',{name:'Retrieve verified customer disclosure'}).click();await expect(page.getByRole('alert')).toContainText('AUTH_REQUIRED');
 await page.getByRole('button',{name:'Simulate verified callback identity'}).click();await expect(page.getByText('Saved demo_callback_verification',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Retrieve verified customer disclosure'}).click();await expect(page.getByText(/Customer disclosure: The specialist reviewed/)).toBeVisible();await page.getByLabel('Customer objection verbatim').fill('I disagree and want a complaint recorded.');await page.getByLabel('Customer explicitly requests a complaint').check();await page.getByRole('button',{name:'Record objection and linked review'}).click();await expect(page.getByText(/Saved capture_customer_objection · receipt/)).toBeVisible();await expect(page.getByText(/Independent complaint intake: recorded/)).toBeVisible();await page.getByLabel('Actual callback outcome').selectOption('connected_verified');await page.getByRole('button',{name:'Record actual callback outcome'}).click();await expect(page.getByText(/Saved record_callback_attempt · receipt/)).toBeVisible();await expect(page.getByRole('button',{name:'Open synthetic callback context'})).toBeDisabled();await page.screenshot({path:'test-results/verified-feedback.png',fullPage:true});
 await login(page,'complaints');const intake=page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'complaint_intake'});await expect(intake).toBeVisible();await expect(intake.getByRole('button',{name:/Open work/})).toHaveCount(0);await expect(intake.getByRole('button',{name:/Claim work/})).toHaveCount(0);

});
test('WF-02: a declined material request returns the work to the specialist',async({page})=>{
 const reference=await newReferral(page);await page.goto('/');await login(page,'specialist');
 await page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'specialist_investigation'}).getByRole('button',{name:/Claim work/}).click();await expect(page.getByRole('heading',{name:'Assigned work · specialist_investigation'})).toBeVisible();
 await page.getByRole('button',{name:'Request material through customer service'}).click();await expect(page.getByText(/Saved request_material/)).toBeVisible();await expect(page.getByText(/awaiting_documents · case v/)).toBeVisible();
 await login(page,'feedback_other');await page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'material_followup'}).getByRole('button',{name:/Claim work/}).click();await expect(page.getByRole('heading',{name:'Assigned work · material_followup'})).toBeVisible();
 await page.getByLabel('Customer answer').selectOption('declined');await page.getByRole('textbox',{name:'Follow-up statement',exact:true}).fill('Customer declined to provide a receipt.');await page.getByRole('button',{name:'Record follow-up outcome'}).click();await expect(page.getByText(/Saved record_followup/)).toBeVisible();
 await login(page,'specialist');await page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'specialist_investigation'}).getByRole('button',{name:/Open work/}).click();
 await expect(page.getByText(/investigating · case v/)).toBeVisible();await expect(page.getByText('declined: Customer declined to provide a receipt.',{exact:true})).toBeVisible();
});
test('WF-03: a customer who calls in can dispute a published finding',async({page})=>{
 const reference=await newReferral(page);await page.goto('/');await login(page,'specialist');
 await page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'specialist_investigation'}).getByRole('button',{name:/Claim work/}).click();await expect(page.getByRole('heading',{name:'Assigned work · specialist_investigation'})).toBeVisible();
 await page.getByRole('textbox',{name:'Approved customer explanation',exact:true}).fill('The two entries were reviewed; one is a separate valid purchase.');await page.getByRole('button',{name:'Publish specialist finding'}).click();await expect(page.getByText(/Saved record_specialist_result · receipt/)).toBeVisible();
 await page.goto('/');await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');
 await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();await expect(page.getByRole('table')).toBeVisible();
 for(const checkbox of await page.getByRole('checkbox').all())await checkbox.check();await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
 const card=page.getByRole('article',{name:`Case ${reference}`});await expect(card.getByText(/one is a separate valid purchase/)).toBeVisible();
 await card.getByLabel('Customer statement (verbatim)').fill('I only made one purchase; I disagree with this finding.');await card.getByRole('button',{name:'Record disagreement for re-review'}).click();
 await expect(page.getByRole('article',{name:`Case ${reference}`}).getByRole('heading',{name:`${reference} · under review`})).toBeVisible();
});


test('WF-04: assigned specialist receives usable intake context without widening access',async({page})=>{
 const reference=await newReferral(page,true);await page.goto('/');await login(page,'specialist');
 const work=page.getByRole('listitem').filter({hasText:reference}).filter({hasText:'specialist_investigation'});
 await work.getByRole('button',{name:/Open work/}).click();await expect(page.getByRole('alert')).toContainText('FORBIDDEN_OR_NOT_FOUND');
 await expect(page.getByRole('region',{name:'Submitted intake history'})).toHaveCount(0);
 await work.getByRole('button',{name:/Claim work/}).click();
 const intake=page.getByRole('region',{name:'Submitted intake history'});
 await expect(intake).toContainText('One purchase, two posted entries; workflow acceptance fixture.');
 await expect(intake).toContainText('One purchase recognized; which entry is additional remains unresolved.');
 await expect(intake).toContainText('Receipt unavailable at intake: unavailable; owner specialist');
 await expect(intake).toContainText('Customer service must repair the contact reference.');
 await expect(intake).toContainText('purchase count: answered — One purchase');
 await expect(intake).toContainText('Statement revision');await expect(intake).toContainText('New investigation');
 const evidence=page.getByRole('table',{name:'Assigned transaction evidence'});
 await expect(evidence.getByRole('row')).toHaveCount(3);await expect(evidence).toContainText('85.00');
 const refs=await evidence.locator('tbody tr td:first-child').allTextContents();expect(new Set(refs).size).toBe(2);
 await login(page,'feedback_other');await expect(page.getByRole('region',{name:'Submitted intake history'})).toHaveCount(0);
});

test('WF-05: publishing a finding never promotes an unapproved update into inbound evidence',async({page})=>{
 await page.goto('/');await login(page,'specialist');
 const work=page.getByRole('listitem').filter({hasText:'DEMO-CASE-001'}).filter({hasText:'specialist_investigation'});
 await work.getByRole('button',{name:/Open work/}).click();
 await page.getByRole('textbox',{name:'Approved customer explanation',exact:true}).fill('Reviewed synthetic finding; no refund has been executed.');
 await page.getByRole('button',{name:'Publish specialist finding'}).click();await expect(page.getByText(/Saved record_specialist_result/)).toBeVisible();
 await page.goto('/');await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');
 await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();await expect(page.getByRole('table')).toBeVisible();
 for(const box of await page.getByRole('checkbox').all())await box.check();await page.getByRole('button',{name:/Inspect selected evidence \([1-9]/}).click();
 const card=page.getByRole('article',{name:'Case DEMO-CASE-001'});await expect(card).toContainText('Reviewed synthetic finding');
 await expect(card).not.toContainText('UNAPPROVED PRIVATE UPDATE');
 await expect(page.getByText('No referral submission is available in this increment.',{exact:false})).toHaveCount(0);
 await expect(page.getByText(/section 6 submits an enquiry only after explicit approval/)).toBeVisible();
 await page.getByRole('button',{name:'Refresh related cases'}).click();await expect(card).not.toContainText('UNAPPROVED PRIVATE UPDATE');
});

test('WF-06: delivered feedback shows its closure blocker until a specialist records completion',async({page})=>{
 const reference=await newReferral(page);await page.goto('/');await login(page,'specialist');
 const work=(kind:string)=>page.getByRole('listitem').filter({hasText:reference}).filter({hasText:kind});
 await work('specialist_investigation').getByRole('button',{name:/Claim work/}).click();
 await page.getByRole('combobox',{name:'Finding',exact:true}).selectOption('further_action_required');
 await page.getByRole('textbox',{name:'Approved customer explanation',exact:true}).fill('The enquiry has been reviewed. A required action remains outstanding.');
 await page.getByRole('button',{name:'Publish specialist finding'}).click();await expect(page.getByText(/Saved record_specialist_result/)).toBeVisible();
 await login(page,'feedback_unclaimed');await work('customer_feedback').getByRole('button',{name:/Claim work/}).click();
 await page.getByRole('button',{name:'Open synthetic callback context'}).click();
 await page.getByRole('button',{name:'Save feedback review draft'}).click();await expect(page.getByRole('button',{name:'Approve current feedback review'})).toBeEnabled();
 await page.getByRole('button',{name:'Approve current feedback review'}).click();await expect(page.getByText(/Saved approve_feedback_review/)).toBeVisible();
 await page.getByRole('button',{name:'Simulate verified callback identity'}).click();await expect(page.getByText('Saved demo_callback_verification',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Retrieve verified customer disclosure'}).click();await expect(page.getByText(/Customer disclosure: The enquiry has been reviewed/)).toBeVisible();
 await page.getByLabel('Actual callback outcome').selectOption('connected_verified');await page.getByRole('button',{name:'Record actual callback outcome'}).click();await expect(page.getByText(/Saved record_callback_attempt/)).toBeVisible();
 const checklist=page.getByRole('region',{name:'Closure checklist'});
 await expect(checklist).toContainText('Feedback delivered · case remains open');await expect(checklist).toContainText('Required actions are incomplete or missing a completion receipt');
 await page.getByLabel('Closure confirmation reason').fill('Reviewed the remaining work.');await expect(page.getByRole('button',{name:'Confirm closure if all checks pass'})).toBeDisabled();
 // The inbound overview also distinguishes delivery from closure.
 await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');
 await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();
 const boxes=page.getByRole('table').getByRole('checkbox');await expect(boxes).toHaveCount(2);
 for(const box of await boxes.all())await box.check();
 await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
 const card=page.getByRole('article',{name:`Case ${reference}`});await expect(card.getByRole('heading',{level:3})).toHaveText(`${reference} · Feedback delivered · case remains open`);
 // Only the specialist records the external action receipt; feedback staff cannot bypass it.
 await expect(page.getByRole('button',{name:'Record external system receipt'})).toHaveCount(0);
 await login(page,'specialist');await work('specialist_investigation').getByRole('button',{name:/Open work/}).click();
 await page.getByRole('button',{name:'Record external system receipt'}).click();await expect(page.getByText(/Saved record_action_receipt/)).toBeVisible();
 await login(page,'feedback_unclaimed');await work('customer_feedback').getByRole('button',{name:/Open work/}).click();
 await expect(checklist).toContainText('Closure checks are satisfied');
 await page.getByLabel('Closure confirmation reason').fill('Verified feedback delivered and required action receipt checked.');await page.getByRole('button',{name:'Confirm closure if all checks pass'}).click();
 await expect(page.getByText(/Saved close_case · receipt/)).toBeVisible();await expect(checklist.getByText('closed',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Confirm closure if all checks pass'})).toHaveCount(0);
 await page.getByRole('button',{name:'Refresh related cases'}).click();await expect(card.getByRole('heading',{level:3})).toHaveText(`${reference} · closed`);
});

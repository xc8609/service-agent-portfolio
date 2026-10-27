import {test,expect,Page,Locator} from '@playwright/test';
import browserTime from '../../../services/api/tests/browser-clock.json' with {type:'json'};

// One continuous synthetic contact: the seeded DEMO-CASE-001 enquiry from first contact
// to delivered feedback. Captions describe what is on screen; nothing is measured.
const pause=(page:Page,ms:number)=>page.waitForTimeout(ms);
let shot=0;
async function say(page:Page,step:string,text:string,ms=4500){
 await page.evaluate(([step,text])=>{
  let box=document.getElementById('walkthrough-caption');
  if(!box){box=document.createElement('div');box.id='walkthrough-caption';box.setAttribute('aria-hidden','true');
   box.style.cssText='position:fixed;left:24px;right:24px;bottom:20px;z-index:2147483647;padding:14px 20px;border-radius:10px;background:rgba(17,24,39,.92);color:#fff;font:500 19px/1.45 system-ui,-apple-system,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.25);pointer-events:none';
   document.body.appendChild(box);}
  box.innerHTML='';const b=document.createElement('div');b.textContent=step;b.style.cssText='font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#93c5fd;margin-bottom:4px';
  const t=document.createElement('div');t.textContent=text;box.append(b,t);
 },[step,text]);
 // Optional stills for reviewing each caption against what is on screen.
 if(process.env.WALKTHROUGH_SHOTS)await page.screenshot({path:`${process.env.WALKTHROUGH_SHOTS}/${String(++shot).padStart(2,'0')}.png`});
 await pause(page,ms);
}
// Bring the element's top near the top of the view, clear of the bottom caption.
async function show(locator:Locator){await locator.evaluate(el=>{el.scrollIntoView({block:'start'});window.scrollBy(0,-90);});await locator.page().waitForTimeout(400);}
async function login(page:Page,role:string){
 await page.getByLabel('Operations role').selectOption(role);await page.getByRole('button',{name:'Start operations session'}).click();
 await expect(page.getByText('Synthetic operations session. Claim work before viewing details.',{exact:true})).toBeVisible();
}

test('Bank service walkthrough',async({page})=>{
 await page.clock.setFixedTime(new Date(browserTime));
 await page.goto('/');
 await say(page,'Bank Service Assist · synthetic demo','A customer calls: “I bought once — why do I see two CAD 85 charges?” The representative starts a verified contact.',5500);
 await page.getByRole('button',{name:'Start demo contact',exact:true}).click();await expect(page.getByRole('status')).toContainText('Verified contact');

 await page.getByLabel('Customer statement').fill('I bought once, but I see two charges for CAD 85. I cannot tell which entry is extra. I do not have the receipt.');
 await page.getByLabel('Merchant (optional)').fill('DEMO STORE');await page.getByRole('button',{name:'Search transactions',exact:true}).click();
 const table=page.getByRole('table');await expect(table).toBeVisible();await show(table);
 await say(page,'1 · Establish the facts','Only the authorized account is searchable. Both entries are posted at DEMO STORE for CAD 85 — matching values alone do not prove a duplicate.',6000);
 for(const box of await table.getByRole('checkbox').all())await box.check();
 await page.getByRole('button',{name:'Inspect selected evidence (2)'}).click();
 await page.getByLabel('Customer recognition').selectOption('one_purchase_unresolved');
 await page.getByRole('button',{name:'Save customer report',exact:true}).click();await expect(page.getByText(/Saved customer report revision/)).toBeVisible();
 await say(page,'1 · Establish the facts','The customer’s words are saved separately from source facts: one purchase, entry mapping unresolved. Staff never ask the customer to guess.',6000);

 const rule=page.getByRole('article',{name:'Rule Two posted entries: investigate before concluding'});await show(rule);
 await say(page,'2 · Procedure and existing work','The applicable handling rule shows its conditions, source version and next steps. An enquiry already exists for this account, with an owner and queue.',6500);

 await page.getByLabel('Question for the assistant').fill('Why are there two charges, and is there already an enquiry?');
 await page.getByRole('button',{name:'Run scoped offline assistant',exact:true}).click();await expect(page.getByText(/· awaiting_human · usage unavailable/)).toBeVisible();
 const summary=page.getByLabel('Assistant summary');await show(page.getByLabel('Saved customer statement'));
 await say(page,'3 · Agent draft for review','A scripted offline assistant organizes permitted evidence into Facts / To confirm / Next step. The saved customer statement stays visibly separate.',7000);
 await show(summary);await pause(page,2500);
 await page.getByRole('button',{name:'Load note history'}).click();await page.getByRole('button',{name:/Review saved note draft/}).last().click();
 const note=page.getByRole('textbox',{name:'Reviewed note',exact:true});await expect(note).toHaveValue(/Two posted entries/);await show(note);
 await say(page,'3 · Agent draft for review','The representative reviews and edits the drafted note. Nothing is saved to the service record until a person approves it.',5500);
 await page.getByRole('button',{name:'Approve and commit note'}).click();await expect(page.getByText(/Committed service record:/)).toBeVisible();

 await page.getByRole('button',{name:'Prepare fresh referral from selected pair'}).click();
 const decision=page.getByLabel('Work decision');await expect(decision).toHaveValue('link_existing');
 await page.getByRole('textbox',{name:'Material gaps (one per line)',exact:true}).fill('Purchase receipt');
 await show(decision);
 await say(page,'4 · Hand off without duplicating work','The handoff carries the statement, the transaction pair and the missing receipt. Because an enquiry exists, the contact links to it instead of opening a duplicate.',7000);
 await page.getByLabel('Customer confirmed the summarized concern').check();
 await page.getByRole('button',{name:'Save referral draft',exact:true}).click();await expect(page.getByText('Referral draft saved — not submitted.',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Approve specialist enquiry'}).click();
 const linked=page.getByText('Linked to existing work; no duplicate investigation created.',{exact:true});await expect(linked).toBeVisible();await show(linked);await pause(page,3000);

 const work=(kind:string)=>page.getByRole('listitem').filter({hasText:'DEMO-CASE-001'}).filter({hasText:kind});
 await login(page,'specialist');await show(work('specialist_investigation'));
 await work('specialist_investigation').getByRole('button',{name:/Open work/}).click();
 await expect(page.getByRole('heading',{name:/Assigned work · specialist_investigation/})).toBeVisible();
 await show(page.getByText('Submitted intake history',{exact:true}));
 await say(page,'5 · Specialist review','The new contact returns the existing enquiry to the specialist, with the customer’s statement, the transaction pair and the open evidence gap.',7000);
 await page.getByRole('combobox',{name:'Finding',exact:true}).selectOption('further_action_required');
 const explanation=page.getByRole('textbox',{name:'Approved customer explanation',exact:true});
 await explanation.fill('We have reviewed both CAD 85 entries. One requires further action, and we will update you when it is complete.');await show(explanation);
 await page.getByRole('textbox',{name:'Specialist private notes',exact:true}).fill('Internal: confirm the merchant settlement record.');
 await say(page,'5 · Specialist review','The specialist publishes an approved customer explanation. Private notes stay internal and never reach the customer.',6000);
 await page.getByRole('button',{name:'Publish specialist finding'}).click();await expect(page.getByText(/Saved record_specialist_result/)).toBeVisible();

 await login(page,'feedback_unclaimed');await work('customer_feedback').getByRole('button',{name:/Claim work/}).click();
 await expect(page.getByRole('heading',{name:'Assigned work · customer_feedback'})).toBeVisible();
 await page.getByRole('button',{name:'Open synthetic callback context'}).click();
 const review=page.getByRole('textbox',{name:'Reviewed feedback explanation',exact:true});await expect(review).toBeVisible();await show(review);
 await say(page,'6 · Customer feedback','A feedback representative claims the callback and reviews the approved explanation before contacting the customer.',6000);
 await page.getByRole('button',{name:'Save feedback review draft'}).click();await expect(page.getByRole('button',{name:'Approve current feedback review'})).toBeEnabled();
 await page.getByRole('button',{name:'Approve current feedback review'}).click();await expect(page.getByText(/Saved approve_feedback_review/)).toBeVisible();
 await page.getByRole('button',{name:'Simulate verified callback identity'}).click();await expect(page.getByText('Saved demo_callback_verification',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Retrieve verified customer disclosure'}).click();const disclosure=page.getByText(/Customer disclosure:/);await expect(disclosure).toBeVisible();await show(disclosure);
 await say(page,'6 · Customer feedback','The explanation is disclosed only after the customer’s identity is verified on the callback.',5000);
 await page.getByLabel('Actual callback outcome').selectOption('connected_verified');await page.getByRole('button',{name:'Record actual callback outcome'}).click();
 await expect(page.getByText(/Saved record_callback_attempt/)).toBeVisible();
 const checklist=page.getByRole('region',{name:'Closure checklist'});await expect(checklist).toContainText('Feedback delivered · case remains open');await show(checklist);
 await say(page,'7 · Check before closing','Feedback is delivered, but required work remains — so the case stays open and the checklist shows what is outstanding.',7500);
 await say(page,'Bank Service Assist','From one enquiry to an owned, reviewed outcome. Synthetic data, simulated roles, offline scripted Agent.',5000);
});

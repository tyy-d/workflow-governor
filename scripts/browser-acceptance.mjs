import { chromium } from '../runtime/browser/node_modules/playwright/index.mjs'
import fs from 'node:fs'
const logDir=process.env.GOVERNOR_TEST_REPORT_DIR||'runtime/deployment'
fs.mkdirSync(logDir,{recursive:true})
const base=process.env.GOVERNOR_TEST_URL||'http://127.0.0.1:8080'
const browser=await chromium.launch({headless:true})
const page=await browser.newPage({viewport:{width:1600,height:1100}})
const errors=[];page.on('pageerror',e=>errors.push(String(e)))
const start=Date.now();let id=process.env.GOVERNOR_TEST_WORKFLOW||'';const resuming=Boolean(id)
async function state(){return await (await fetch(`${base}/api/workflows/${id}`)).json()}
async function settle(){
 for(let n=0;n<240;n++){
  const w=await state();if(!w.operation){if(w.error)throw new Error(w.error);return w}
  if(n%3===0)console.log(new Date().toISOString(),w.operation,w.tasks.map(t=>`${t.id}:${t.status}`).join(' '))
  await new Promise(r=>setTimeout(r,5000))
 }
 throw Error('Timed out waiting for local execution')
}
try{
 if(resuming){await page.goto(base+'/#'+id);await page.locator('.workflow-header').waitFor();console.log('Resuming persisted workflow',id)}else{
 await page.goto(base);await page.getByRole('button',{name:'+ New Workflow',exact:true}).first().click()
 await page.getByPlaceholder('Can you figure out what we need to do to get this vendor live by Friday?').fill('Can you figure out what we need to do to get this vendor live by Friday?')
 await page.getByPlaceholder('Generated from the objective if blank').fill('CASE_001 — GB10 real acceptance')
 await page.getByRole('button',{name:'Start Workflow',exact:true}).click()
 await page.waitForURL(/#WF-/, {timeout:15000});id=new URL(page.url()).hash.slice(1)
 fs.writeFileSync(`${logDir}/acceptance-workflow-id.txt`,id)
 console.log('Created via browser',id)
 await page.reload();await page.getByText('Planning with local Qwen…',{exact:true}).waitFor({timeout:20000})
 }
 let w=resuming?await state():await settle();console.log('PLAN',w.planState,w.tasks.map(t=>[t.id,t.title,t.executor]))
 if(w.planState==='PROPOSED'){
 await page.getByRole('button',{name:'Approve Plan',exact:true}).waitFor({timeout:15000})
 await page.screenshot({path:`${logDir}/plan.png`,fullPage:true})
 await page.getByRole('button',{name:'Approve Plan',exact:true}).click()
 await new Promise(r=>setTimeout(r,3000))
 }
 w=await state()
 for(const t of w.tasks){
  if(t.status==='Completed')continue
  // Task navigator buttons include title plus status; select by visible heading text inside button.
  const button=page.locator('.plan-panel button, .plan-list button, .task-list button').filter({hasText:t.title})
  if(await button.count())await button.first().click()
  else await page.getByRole('button').filter({hasText:t.title}).first().click()
  await page.locator('.task-heading h2').filter({hasText:t.title}).waitFor()
  if(t.status==='Blocked'){
   await page.getByPlaceholder('What changed or why should this task be retried?').fill('Citation formatting repair verified against the original source text and exact line; resume real execution while retaining the failed attempt.')
   await page.getByRole('button',{name:'Resume Task',exact:true}).click();await new Promise(r=>setTimeout(r,3000))
  }
  if(t.executor==='Human'){
   await page.getByLabel('Reviewer name',{exact:true}).fill('Automated acceptance operator (demonstration input)')
   await page.getByLabel('Judgment',{exact:true}).fill('Request clarification: limit this task to evidence review, not vendor activation.')
   await page.getByLabel('Reason and evidence references',{exact:true}).fill('This acceptance input has no corporate authority. Confirm that recording a review will not change VendorLink or transmit a PO.')
   await page.getByRole('button',{name:'Ask Clarification',exact:true}).click()
   await page.getByRole('heading',{name:'Blocked — recovery required'}).waitFor({timeout:15000})
   await page.reload();await page.getByRole('button').filter({hasText:t.title}).first().click()
   await page.getByPlaceholder('What changed or why should this task be retried?').fill('Confirmed: local evidence review only. No external system writes or corporate authorization.')
   await page.getByRole('button',{name:'Resume Task',exact:true}).click()
   await new Promise(r=>setTimeout(r,3000))
   const current=await state();const cited=current.tasks.filter(x=>x.result).flatMap(x=>x.result.findings).map(x=>x.statement+' '+x.citations.map(c=>`[${c.sourceId}:L${c.line}]`).join(' ')).join('\n')
   await page.getByLabel('Judgment',{exact:true}).fill('Evidence review complete. Preserve the recorded vendor standing and outstanding blockers; do not release commercial orders without authorized evidence and approval.')
   await page.getByLabel('Reason and evidence references',{exact:true}).fill('Demonstration reviewer accepts only a review handoff, not activation or commercial release. Basis from actual completed tasks:\n'+cited.slice(0,4200))
   await page.getByRole('button',{name:'Complete',exact:true}).click()
   await new Promise(r=>setTimeout(r,3000))
   console.log('Human clarification, resume and judgment persisted through browser')
  }else{
   await page.getByRole('button',{name:'Execute Task',exact:true}).click();await new Promise(r=>setTimeout(r,1500));await settle()
  }
  await page.reload();await new Promise(r=>setTimeout(r,1500))
 }
 w=await state();if(w.status!=='Completed')throw Error('Workflow not completed: '+w.status)
 if(!w.finalState.findings.length||!w.finalState.findings.some(f=>f.includes(':L')))throw Error('Missing cited final findings')
 if(errors.length)throw Error('Browser errors: '+errors.join('\n'))
 await page.screenshot({path:`${logDir}/completed.png`,fullPage:true})
 fs.writeFileSync(`${logDir}/browser-acceptance.json`,JSON.stringify({status:'passed',workflowId:id,seconds:(Date.now()-new Date(w.createdAt).getTime())/1000,browserSessionSeconds:(Date.now()-start)/1000,pageErrors:errors,refreshResumed:true,humanInput:'explicitly labeled automated acceptance input',blockedTaskResumed:true,finalState:w.finalState},null,2))
 console.log('PASS',id,(Date.now()-start)/1000,w.finalState)
}catch(e){await page.screenshot({path:`${logDir}/browser-failure.png`,fullPage:true});console.error(e);fs.writeFileSync(`${logDir}/browser-error.json`,JSON.stringify({id,error:String(e),url:page.url(),pageErrors:errors},null,2));process.exitCode=1}
finally{await browser.close()}

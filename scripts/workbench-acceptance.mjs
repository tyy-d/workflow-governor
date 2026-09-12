import {chromium} from '../runtime/browser/node_modules/playwright/index.mjs'
import fs from 'node:fs'
const base=process.env.GOVERNOR_TEST_URL||'http://127.0.0.1:8081'
const report=process.env.GOVERNOR_TEST_REPORT_DIR||'runtime/workbench-preview'
fs.mkdirSync(report,{recursive:true})
const browser=await chromium.launch({headless:true})
const page=await browser.newPage({viewport:{width:1440,height:1000}})
const errors=[];page.on('pageerror',e=>errors.push(String(e)))
let id=process.env.GOVERNOR_TEST_WORKFLOW
const state=async()=>await(await fetch(base+'/api/workflows/'+id)).json()
async function settle(){for(let i=0;i<150;i++){const w=await state();if(!w.operation){if(w.error)throw Error(w.error);return w}if(i%5===0)console.log(new Date().toISOString(),w.operation);await new Promise(r=>setTimeout(r,2000))}throw Error('Run timeout')}
try{
 await page.goto(base);await page.getByRole('heading',{name:'Workflows',exact:true}).waitFor();await page.screenshot({path:report+'/after-home-1440.png',fullPage:true})
 if(!id){
  await page.getByRole('button',{name:'+ New workflow',exact:true}).last().click()
  await page.getByLabel('Goal',{exact:true}).fill('Review the selected vendor status and readiness records. Extract facts, identify unresolved work, and propose a bounded evidence review. Do not perform external activation or infer unavailable company policy.')
  await page.getByLabel('Name Optional').fill('Vendor readiness review')
  await page.getByRole('checkbox').first().waitFor()
  const names=['VENDORLINK_STATUS_NVID-10482.json','LAUNCH_READINESS_TRACKER_2026-09-09.csv']
  for(const name of names)await page.getByRole('checkbox',{name,exact:true}).check()
  await page.getByRole('button',{name:'Create workflow',exact:true}).click();await page.waitForURL(/#WF-/);id=page.url().split('#')[1];fs.writeFileSync(report+'/workflow-id.txt',id)
  await page.getByRole('button',{name:'Generate plan',exact:true}).waitFor();await page.screenshot({path:report+'/empty-workflow.png',fullPage:true})
  await page.getByRole('button',{name:'Generate plan',exact:true}).click();await page.getByText(/Generating and validating plan|Selecting authorized evidence/).first().waitFor();await page.screenshot({path:report+'/loading.png',fullPage:true})
 }
 if(id){await page.goto(base+'/#'+id);await page.getByRole('heading',{name:(await state()).name,exact:true}).waitFor()}
 let w=await settle();console.log('Plan',w.planState,w.tasks.map(t=>[t.id,t.title,t.executor]));
 if(w.planState==='PROPOSED'){await page.getByRole('button',{name:'Approve plan',exact:true}).waitFor();await page.screenshot({path:report+'/after-plan-1440.png',fullPage:true});await page.getByRole('button',{name:'Approve plan',exact:true}).click();await page.waitForTimeout(1500)}
 w=await state()
 for(const t of w.tasks.filter(t=>t.executor!=='Human').slice(0,2)){
  await page.getByRole('button',{name:t.title,exact:true}).click()
  if(t.status!=='Completed'){await page.getByRole('button',{name:'Execute Task',exact:true}).click();await settle();await page.getByRole('heading',{name:'Saved execution result',exact:true}).waitFor({timeout:15000})}
  await page.screenshot({path:report+`/task-${t.id}.png`,fullPage:true});await page.getByRole('button',{name:'Close details',exact:true}).click()
 }
 w=await state();const result=w.tasks.find(t=>t.result);const cite=result.result.findings[0].citations[0]
 await page.getByRole('button',{name:'Evidence',exact:true}).click();await page.getByRole('button',{name:new RegExp(w.evidence.find(e=>e.id===cite.sourceId).title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();await page.screenshot({path:report+'/evidence.png',fullPage:true});await page.getByRole('button',{name:'Close details',exact:true}).click()
 await page.reload();await page.getByRole('heading',{name:w.name,exact:true}).waitFor()
 for(const width of [1440,1280,1024,390]){await page.setViewportSize({width,height:1000});await page.screenshot({path:report+`/after-workflow-${width}.png`,fullPage:true});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);if(overflow)throw Error(`Page overflow at ${width}`)}
 if(errors.length)throw Error(errors.join('\n'))
 fs.writeFileSync(report+'/acceptance.json',JSON.stringify({workflowId:id,status:w.status,tasks:w.tasks.map(t=>({id:t.id,status:t.status})),citationsVerified:true,refreshed:true,widths:[1440,1280,1024,390],browserErrors:errors},null,2))
 console.log('PASS',id,w.tasks.map(t=>`${t.id}:${t.status}`).join(', '))
}finally{await browser.close()}

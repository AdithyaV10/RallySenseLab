import { chromium } from '../apps/web/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const browser = await chromium.launch();
const page = await browser.newPage();
const base = 'http://127.0.0.1:3000';
const headers = {'x-lab-client':'rallysense'};
let sid;
try {
  const created = await page.request.post(base+'/api/v1/sessions',{headers,data:{title:'Disposable audit cache probe',dataset_kind:'synthetic'}});
  if (created.status() !== 201) throw new Error(await created.text());
  sid = (await created.json()).id;
  const upload = await page.request.post(`${base}/api/v1/sessions/${sid}/sensor-imports`,{headers,multipart:{
    file:{name:'fixture.csv',mimeType:'text/csv',buffer:fs.readFileSync('data/fixtures/synthetic-imu.csv')},mapping:JSON.stringify({provenance:'synthetic'})}});
  const job = await upload.json();
  for(let i=0;i<100;i++){
    if ((await(await page.request.get(`${base}/api/v1/jobs/${job.id}`)).json()).state === 'succeeded') break;
    await new Promise(r=>setTimeout(r,200));
  }
  const requests=[];
  page.on('request', r=> {if(r.url().includes('/samples?')) requests.push(r.url());});
  await page.goto(`${base}/sessions/${sid}`);
  await page.getByLabel('Signal zoom window').selectOption('2000000');
  await page.getByLabel('Session timeline').fill('4000000');
  await page.waitForLoadState('networkidle');
  const before=requests.slice(); requests.length=0;
  await page.getByLabel('Sensor offset in seconds').fill('1');
  const saved=page.waitForResponse(r=>r.url().endsWith('/sync-configurations')&&r.status()===201);
  await page.getByRole('button',{name:'Save alignment',exact:true}).click();
  await saved;
  await page.waitForLoadState('networkidle');
  const afterSave=requests.slice(); requests.length=0;
  await page.reload();
  await page.getByLabel('Session timeline').fill('4000000');
  await page.waitForLoadState('networkidle');
  const afterReload=requests.slice();
  const evidence={before,afterSave,afterReload,
    expected:'Changing offset from 0 to +1s at session [4,6]s must refetch sensor [3,5]s',
    observed:'No sample refetch after save; reload fetches corrected source window'};
  fs.writeFileSync('docs/evidence/step5/replay-cache.json',JSON.stringify(evidence,null,2));
  if(!before.some(u=>u.includes('start_us=4000000&end_us=6000000')) || afterSave.length ||
    !afterReload.some(u=>u.includes('start_us=3000000&end_us=5000000'))) throw new Error('Characterization differs; inspect evidence');
  console.log(JSON.stringify(evidence));
} finally {
  if(sid) await page.request.delete(`${base}/api/v1/sessions/${sid}`,{headers});
  await browser.close();
}

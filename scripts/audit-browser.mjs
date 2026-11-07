import { chromium } from '../apps/web/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const browser = await chromium.launch();
const page = await browser.newPage();
const base = 'http://127.0.0.1:3000';
const errors = [];
page.on('pageerror', e => errors.push(e.message));
const get = async path => { const r = await page.request.get(base + path); if (!r.ok()) throw new Error(`${path}: ${r.status()}`); return r.json(); };
try {
  const demos = await get('/api/v1/demonstrations');
  const paired = demos.find(s => s.title.startsWith('Paired'));
  const original = demos.find(s => s.title.startsWith('Baseline'));
  const full = await page.request.get(`${base}/api/v1/sessions/${paired.id}/experiments?limit=50`);
  const summaries = await page.request.get(`${base}/api/v1/sessions/${paired.id}/experiments?limit=50&summaries=true`);
  const rows = await full.json();
  const detail = await page.request.get(`${base}/api/v1/experiments/${rows[0].id}`);
  const routes = [['landing','/'], ['library','/sessions'], ['collection','/record'],
    ['replay',`/sessions/${original.id}`], ['challenge',`/sessions/${paired.id}?tab=research`],
    ['method','/docs'], ['diagnostics','/diagnostics'], ['report',`/experiments/${rows[0].id}/report`]];
  const views = [];
  for (const [name, route] of routes) for (const [mode, width, height] of [['desktop',1440,1000],['mobile',390,844]]) {
    await page.setViewportSize({width,height});
    const began = performance.now();
    await page.goto(base + route);
    await page.waitForLoadState('networkidle');
    const observations = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > innerWidth,
      h1: document.querySelector('h1')?.textContent,
      unnamedButtons: [...document.querySelectorAll('button')].filter(b => !b.textContent.trim() && !b.getAttribute('aria-label') && !b.getAttribute('title')).length,
    }));
    views.push({route:name, viewport:mode, navigation_ms:performance.now()-began, ...observations});
    await page.screenshot({path:`docs/evidence/step5-${name}-${mode}.png`,fullPage:true});
  }
  const evidence = {scope:'Actual local Chromium; basic DOM accessibility checks, not WCAG certification or physical phone testing',
    views, errors, same_history_payload:{rows:rows.length, full_bytes:(await full.body()).length,
      summaries_bytes:(await summaries.body()).length, selected_detail_bytes:(await detail.body()).length}};
  fs.writeFileSync('docs/evidence/step5/browser-review.json', JSON.stringify(evidence,null,2));
  console.log(JSON.stringify(evidence));
  if (errors.length || views.some(v => v.overflow)) process.exitCode = 1;
} finally { await browser.close(); }

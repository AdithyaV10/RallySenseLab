import { chromium } from '../apps/web/node_modules/playwright/index.mjs';
import { expect } from '../apps/web/node_modules/@playwright/test/index.mjs';
import fs from 'node:fs';

const stage = 'step6_6';
const state = JSON.parse(fs.readFileSync(`storage/${stage}/local-release-state.json`, 'utf8'));
const env = path => Object.fromEntries(fs.readFileSync(path, 'utf8').split(/\r?\n/).filter(Boolean).map(line => [line.slice(0, line.indexOf('=')), line.slice(line.indexOf('=') + 1)]));
const browser = await chromium.launch({ args: ['--no-proxy-server', '--host-resolver-rules=MAP *.rallysense.test 127.0.0.1'] });
const results = [];
try {
  for (const role of ['demo']) {
    const config = state.roles[role], values = env(config.env_file);
    const context = await browser.newContext({
      // Local private CA only; Python verification separately validates its chain and names.
      ignoreHTTPSErrors: true,
      httpCredentials: { username: 'lab', password: values.SITE_ACCESS_PASSWORD },
      viewport: { width: 1440, height: 1000 },
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const base = `https://${config.host}:18443`;
    const json = path => page.evaluate(async path => {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`Request failed ${response.status}`);
      return response.json();
    }, path);
    await page.goto(base);
    await expect(page.getByRole('heading', { name: /Understand/ })).toBeVisible();
    for (const path of ['/sessions', '/docs', '/diagnostics']) {
      await page.goto(base + path);
      await expect(page.locator('main')).toBeVisible();
    }
    await page.goto(`${base}/sessions/${config.paired_id}`);
    await expect(page.getByLabel('Session timeline')).toBeVisible();
    const video = page.locator('video');
    await expect.poll(() => video.evaluate(v => v.readyState), { timeout: 20000 }).toBeGreaterThanOrEqual(2);
    await video.evaluate(v => { v.muted = true; return v.play(); });
    await expect.poll(() => video.evaluate(v => v.currentTime)).toBeGreaterThan(.25);
    await video.evaluate(v => v.pause());
    await page.getByLabel('Session timeline').fill('4000000');
    await expect.poll(() => video.evaluate(v => v.currentTime)).toBeGreaterThan(3.8);
    await expect(page.getByTestId('gyro-chart')).toBeVisible();
    await page.goto(`${base}/sessions/${config.paired_id}?tab=research`);
    await expect(page.getByTestId('experiment-result')).toHaveCount(1);
    if (role === 'demo') await expect(page.getByRole('button', { name: 'Run experiment', exact: true })).toBeDisabled();
    else await expect(page.getByRole('button', { name: 'Run experiment', exact: true })).toBeEnabled();
    for (const name of ['Clean IMU / synthetic software verification', 'Clean fusion / synthetic software verification']) {
      const checkbox = page.locator('.research-history-row').filter({ hasText: name }).getByRole('checkbox');
      await checkbox.check();
    }
    await expect(page.getByTestId('experiment-result')).toHaveCount(2);
    const comparisonVerified = true;
    await page.locator('.research-history-row').filter({ hasText: 'Offset +1 second / synthetic failure case' }).getByRole('checkbox').check();
    await expect(page.getByTestId('experiment-result')).toHaveCount(3);
    const failure = page.getByTestId('experiment-result').filter({ has: page.getByRole('heading', { name: 'Offset +1 second / synthetic failure case', exact: true }) });
    await failure.locator('summary').filter({ hasText: 'Failure explorer' }).click();
    await failure.getByRole('button', { name: /Missed reference #1/ }).click();
    await expect(page.getByLabel('Session timeline')).toHaveValue('2000000');
    await page.screenshot({ path: `docs/evidence/${stage}-failure-explorer.png`, fullPage: true });
    const history = await json(`/api/v1/sessions/${config.paired_id}/experiments`);
    const clean = history.find(row => row.name.startsWith('Clean fusion'));
    await page.goto(`${base}/experiments/${clean.id}/report`);
    await expect(page.locator('body')).toContainText(/synthetic/i);
    await page.screenshot({ path: `docs/evidence/${stage}-${role}-report.png`, fullPage: true });
    await page.pdf({ path: `docs/evidence/${stage}-report.pdf`, printBackground: true });
    await page.goto(`${base}/sessions/${config.paired_id}?tab=research`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `docs/evidence/${stage}-${role}-desktop.png`, fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForLoadState('networkidle');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    expect(overflow).toBe(false);
    await page.screenshot({ path: `docs/evidence/${stage}-${role}-mobile.png`, fullPage: true });
    let mediaPipe = null;
    expect(errors).toEqual([]);
    results.push({ role, authenticated_navigation: true, video_decode_and_play: true, synchronized_seek: true,
      graph: true, stored_comparison: comparisonVerified, missed_reference_navigation: true, report: true,
      mobile_overflow: false, page_errors: errors, mediapipe: mediaPipe });
    fs.writeFileSync(`docs/evidence/${stage}/browser-release-progress.json`, JSON.stringify(results, null, 2));
    await context.close();
  }
} finally {
  await browser.close();
}
fs.writeFileSync(`docs/evidence/${stage}/browser-release.json`, JSON.stringify({ scope: 'Actual Chromium against loopback HTTPS release stacks; private-CA chain separately verified by Python; generated sources only', results }, null, 2));
console.log(JSON.stringify(results, null, 2));

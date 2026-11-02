const { chromium } = require('playwright');
(async () => {
  const [url, out, sel] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 800, height: 800 } });
  p.on('pageerror', e => console.log('pageerror:', e.message));
  p.on('requestfailed', r => console.log('failed:', r.url()));
  await p.goto(url, { waitUntil: 'commit', timeout: 120000 });
  await p.waitForSelector(sel, { timeout: 120000 }); await p.waitForTimeout(800);
  await p.screenshot({ path: out, timeout: 120000 }); console.log('ok', out); await b.close();
})();

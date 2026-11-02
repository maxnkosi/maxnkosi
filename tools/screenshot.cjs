const { chromium } = require('playwright');
(async () => {
  const [base, outDir] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  p.on('console', m => console.log('console:', m.text()));
  p.on('pageerror', e => console.log('pageerror:', e.message));
  for (const v of ['front', 'oblique']) {
    await p.goto(`${base}/?view=${v}`, { waitUntil: 'commit', timeout: 120000 });
    await p.waitForFunction('window.__logoReady === true', null, { timeout: 120000 });
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${outDir}/${v}.png`, timeout: 120000 });
    console.log('saved', v);
  }
  await b.close();
})();

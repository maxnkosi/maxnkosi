const { chromium } = require('playwright');
(async () => {
  const [base, outDir] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 900, height: 900 } });
  p.on('pageerror', e => console.log('pageerror:', e.message));
  for (const [name, qs] of [['front','view=front'],['oblique','view=oblique'],['side','yaw=72&pitch=8']]) {
    await p.goto(`${base}/?${qs}`, { waitUntil: 'commit', timeout: 120000 });
    await p.waitForFunction('window.__logoReady === true', null, { timeout: 120000 });
    await p.waitForTimeout(800);
    await p.screenshot({ path: `${outDir}/${name}.png`, timeout: 120000 }); console.log('saved', name);
  }
  await b.close();
})();

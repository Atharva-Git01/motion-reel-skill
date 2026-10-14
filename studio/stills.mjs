// node stills.mjs [step=0.5] [outdir=out/stills] [t1 t2 ...]  -> one PNG per time (no motion blur)
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const step = Number(process.argv[2] || 0.5), dir = process.argv[3] || 'out/stills';
let times = process.argv.length > 4 ? process.argv.slice(4).map(Number) : null;   // default: every `step` seconds over the film's duration
mkdirSync(dir, { recursive: true });
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('pageerror', (e) => console.log('PAGEERROR', e.message));
p.on('console', (m) => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
await p.goto(pathToFileURL(resolve('index.html')).href);
await p.evaluate(() => window.ready);
console.log('fonts', JSON.stringify(await p.evaluate(() => window.fontOK)));
if (!times) { const dur = await p.evaluate(() => { try { return JSON.parse(document.getElementById('tl').textContent).dur; } catch (e) { return 20; } }); times = Array.from({ length: Math.round(dur / step) }, (_, i) => +(i * step).toFixed(3)); }
for (const t of times) {
  await p.evaluate((t) => window.seek(t), t);
  await p.screenshot({ path: `${dir}/t${t.toFixed(2).padStart(5, '0')}.png` });
}
await b.close();
console.log('stills', times.length);

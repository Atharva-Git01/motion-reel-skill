// node render.mjs --fps 60 --dur 20 --sub 4 [--out out/silent.mp4]
// Motion blur is averaged inside the page (running mean of SUB sub-frames), so each output
// frame costs one screenshot instead of SUB, and frames are grabbed straight over CDP.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const sarg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const arg = (k, d) => Number(sarg(k, d));
const FPS = arg('fps', 60), DUR = arg('dur', 20), SUB = arg('sub', 4);
const W = arg('w', 1080), H = arg('h', 1920), OUT = sarg('out', 'out/silent.mp4');
mkdirSync('out', { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(resolve('index.html')).href);
await page.evaluate(() => window.ready);
console.log('fonts', JSON.stringify(await page.evaluate(() => window.fontOK)));

await page.evaluate((SUB) => {
  const c = document.getElementById('c'), cg = c.getContext('2d');
  const acc = document.createElement('canvas'); acc.width = c.width; acc.height = c.height;
  const ag = acc.getContext('2d');
  window.__frame = (t0, dt) => {
    for (let k = 0; k < SUB; k++) {
      window.seek(t0 + k * dt);
      ag.globalAlpha = 1 / (k + 1);
      ag.drawImage(c, 0, 0);
    }
    cg.setTransform(1, 0, 0, 1, 0, 0); cg.globalAlpha = 1; cg.globalCompositeOperation = 'source-over'; cg.filter = 'none';
    cg.drawImage(acc, 0, 0);
  };
}, SUB);

const cdp = await page.context().newCDPSession(page);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT],
  { stdio: ['pipe', 'inherit', 'inherit'] });

const total = Math.round(DUR * FPS), t0 = Date.now();
for (let i = 0; i < total; i++) {
  await page.evaluate(([t, dt]) => window.__frame(t, dt), [i / FPS, 1 / (FPS * SUB)]);
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true, clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
  if (!ff.stdin.write(Buffer.from(data, 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
  if (i % FPS === 0) console.log(`rendered ${i / FPS}s / ${DUR}s  ${((i + 1) / ((Date.now() - t0) / 1000)).toFixed(2)} fps`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
const seconds = (Date.now() - t0) / 1000;
writeFileSync(OUT.replace(/\.mp4$/, '.stats.json'), JSON.stringify({ fps: FPS, sub: SUB, dur: DUR, frames: total, seconds }, null, 1));
console.log(`done ${total} frames in ${seconds.toFixed(1)}s`);

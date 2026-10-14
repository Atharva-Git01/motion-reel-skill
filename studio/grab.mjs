import { chromium } from 'playwright';
const url = process.argv[2];
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
const r = await p.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(e => { console.log('ERR', e.message); return null; });
if (!r) process.exit(1);
console.log('status', r.status(), await p.title());
await p.screenshot({ path: 'assets/hero.png' });
await p.screenshot({ path: 'assets/full.png', fullPage: true });
const info = await p.evaluate(() => {
  const cs = (e) => getComputedStyle(e);
  const h = document.querySelector('h1') || document.body;
  return {
    fonts: [...new Set([...document.querySelectorAll('h1,h2,p,a,button')].map(e => cs(e).fontFamily))].slice(0, 6),
    bg: cs(document.body).backgroundColor, color: cs(document.body).color,
    h1: h.innerText.slice(0, 120), h1color: cs(h).color,
    btn: [...document.querySelectorAll('a,button')].slice(0, 12).map(e => [e.innerText.trim().slice(0, 30), cs(e).backgroundColor]),
    imgs: [...document.images].map(i => i.currentSrc).filter(Boolean).slice(0, 15),
    logo: (document.querySelector('header img, img[alt*=logo i]') || {}).currentSrc,
  };
});
console.log(JSON.stringify(info, null, 1));
await b.close();

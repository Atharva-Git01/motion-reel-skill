# motion-reel error log

Read this whole file before step 0 of every run. Each entry is an error that already cost a run time:
**Seen** = the symptom (exact text when there was one), **Why** = root cause, **Fix** = what actually worked,
**Check** = how to catch it early, **Rule** = what to do from the start so it never happens again.
Entries marked `prevented` were designed around before they bit; keep them.

## Pre-flight rules (one line per entry; apply all of them while planning)
- E01 Python on Windows: never print non-ASCII (₹, →) to stdout; write UTF-8 files and Read them.
- E02 Anything that runs > ~5 min (final render) goes to `run_in_background`; wait with a background `until grep ...; do sleep 10; done`, never `sleep N`.
- E03 Test the URL before planning; DNS failure or "no own website" means stop and ask. Never scrape listings.
- E04 Vertical (9:16) video: capture the site at phone size (`explore.mjs`, 393x852 @3x). Desktop capture only for 16:9.
- E05 Click buttons with `locator('button:has-text("…")')`; save captured data to disk before any risky click.
- E06 Tap coordinates = smallest visible element whose own text equals the label; reject boxes taller than ~400 css px.
- E07 Never guess site routes; read hrefs from the DOM.
- E08 Never type location, pincode, login or personal data into the target site; stop at the first data prompt and use that screen as the last real UI beat.
- E09 After capture, list broken images (naturalWidth 0) and plan shots so they are off-camera or on screen < 1 s.
- E10 Before fullPage screenshots hide fixed/sticky overlays except the header; crop page bodies to < 16384 px tall.
- E11 No ES module imports in index.html (file:// blocks them); inline lib/motion.js.
- E12 index.html exposes `window.ready` (images + fonts) and `window.fontOK`; `seek` returns early until assets exist.
- E13 Use the bundled render.mjs (in-page motion-blur averaging + CDP capture). Drafts: `--fps 30 --sub 1`. Stills: `stills.mjs`.
- E14 To fade or blur a multi-layer composite, render it to an offscreen canvas first, then draw it once.
- E15 No dead time: `compare.py` must show longest still < 1 s and 0 dead seconds; holds need camera drift or rolling detail.
- E16 Photo-filled type on a dark ground needs an outline (strokeText under the mask) and a brightened photo.
- E17 Crop marketing banners explicitly (sx, sy, sw, sh) so baked-in buttons/headlines do not leak into windows.
- E18 Captions that can cross UI get a dark stroke under the fill.
- E19 Rolling digits: mask exactly one digit tall, draw only the resting digit when settled, check the exit frames.
- E20 Masked entrances that also scale must start ≥ 1.5 em below the mask; frame 0 must be identical to the last frame.
- E21 Check frame strips around every morph; UI to card crossfades must be fast (spring 320/36, start 0.06 s early).
- E22 Loudness is always two-pass loudnorm; verify with ebur128 (I = -14 ± 0.5).
- E23 True peak must be ≤ -1 dBTP; soft-clip/limit the stem before loudnorm and verify.
- E24 Layer sounds by adding the shorter array into a slice of the longer one.
- E25 One timeline JSON (`<script id="tl" type="application/json">`) drives picture AND sound; never retype cue times.
- E26 Loop seam: judge by mean |first − last| vs the median frame step (`compare.py`), never by a bounding box.
- E27 Sync check: skip events at t = 0 and remember lead-in whooshes shift detected onsets early.
- E28 Motion metrics with film grain: use a threshold above the grain floor (0.6 at 108x192).
- E29 Deliver a share copy < 25 MB (`-crf 23`) alongside the master; chat/phone file sharing often caps uploads near 30 MiB.

---

## Setup and harness

### E01 · setup · Python print crashes on non-ASCII (Windows)
- **Seen:** `UnicodeEncodeError: 'charmap' codec can't encode character '→'` while printing extracted text.
- **Why:** Windows console uses cp1252; `python -I` (isolated mode) ignores `PYTHONIOENCODING`.
- **Fix:** wrote the text to a file with `open(path, 'w', encoding='utf8')` and read it with the Read tool.
- **Check:** any script that prints prices (₹), arrows or other non-ASCII.
- **Rule:** in Python on Windows write non-ASCII to UTF-8 files, never to stdout. Node prints UTF-8 fine.
- **Run:** 2026-10-13 (Sonnet run, reading the guide).

### E02 · harness · long waits blocked or cut off
- **Seen:** `Blocked: sleep 90 …`; a foreground wait hit the 600 s limit and was moved to background mid-render.
- **Why:** the harness blocks plain sleeps and caps foreground commands at 10 min; a 20 s @ 60 fps / 4 sub render takes ~9 min.
- **Fix:** start the render with `run_in_background: true`, then a background `until grep -q "^done" out/render.log; do sleep 10; done` that notifies on completion.
- **Check:** expected duration > 5 min means background.
- **Rule:** final renders always run in the background; never chain sleeps or poll in the foreground.
- **Run:** 2026-10-13 (Sonnet run).

## Inputs and capture

### E03 · inputs · URL does not resolve / business has no website
- **Seen:** `net::ERR_NAME_NOT_RESOLVED at https://<client-site>/` (site not live yet); a second request pointed at a Google results page for a cafe whose only presence was food-delivery/Instagram listings.
- **Why:** the site was not live; the other business had no own site.
- **Fix:** stopped and asked the user for another source; continued only with a real brand's own product site.
- **Check:** run `node explore.mjs <url> assets/m_home` first; non-200 or DNS error means stop.
- **Rule:** never scrape third-party listings or invent screens; ask for the owner's assets or another URL.
- **Run:** 2026-10-13 (Sonnet run).

### E04 · capture · desktop UI unreadable in a vertical video
- **Seen:** Sonnet reel showed a 1440 px desktop header shrunk to 1000 px: UI text ≈ 10 px in the 1080 frame, ≈ 3 px on a phone.
- **Why:** a desktop layout squeezed into a 9:16 frame.
- **Fix:** Opus run captured the mobile site (Pixel 7 profile, 393x852 css, deviceScaleFactor 3). Shown at 720 px wide, body text ≈ 25 px in frame, ≈ 8–9 px on a 360 px phone; camera zooms push key UI to 11–13 px.
- **Check:** `ffmpeg -i out/draft.mp4 -vf "fps=1,scale=360:-1,tile=10x2" -frames:v 1 out/phone.png` and read it.
- **Rule:** vertical video = phone-size capture; desktop capture only for 16:9 layouts.
- **Run:** 2026-10-13 (Sonnet), fixed 2026-10-14 (Opus).

### E05 · capture · role locator timed out on an icon button
- **Seen:** `locator.click: Timeout 30000ms exceeded … getByRole('button', { name: 'Add to Cart' })`; the script died before writing ui.json.
- **Why:** the accessible name of the icon + text button did not match exactly.
- **Fix:** `p.locator('button:has-text("Add to Cart")').first()`, plus `writeFileSync('assets/ui.json', …)` before the click.
- **Check:** log `await locator.count()` and `isVisible()` before clicking.
- **Rule:** has-text locators for buttons with icons; persist captured data before any step that can fail.
- **Run:** 2026-10-14 (Opus).

### E06 · capture · element box lookup returned a giant ancestor or null
- **Seen:** the box for "Our Products" came back `h: 3768` (a page wrapper); the Brownies tile came back `null`.
- **Why:** `querySelectorAll(...).filter(includes(text))[0]` returns the outermost container; the tiles were not `<a>` elements.
- **Fix:** pick the visible element with the **smallest area** whose normalised innerText **equals** the label (boxes.mjs `find()` pattern), then derive the tap point from it.
- **Check:** sanity-check every box: w and h under ~400 css px; mark the tap on a still before trusting it.
- **Rule:** tap coordinates always come from smallest-area exact-text matches.
- **Run:** 2026-10-14 (Opus).

### E07 · capture · guessed route redirected
- **Seen:** `/products/brownies` silently redirected to `/collections`.
- **Why:** route guessed instead of read.
- **Fix:** listed hrefs from the DOM (`/collections/brownies`, `/products/<slug>`).
- **Check:** compare `page.url()` after `goto` with the requested URL.
- **Rule:** never guess routes; read links from the page.
- **Run:** 2026-10-14 (Opus).

### E08 · policy · flow asked for location / login
- **Seen:** clicking Add to Cart opened a find-a-store sheet (current location, pincode, or log in).
- **Why:** the site needs a store before a cart.
- **Fix:** captured that real sheet as the final UI beat; entered nothing; used a fresh anonymous browser context that is discarded.
- **Check:** after every click, screenshot and read dialogs before the next action.
- **Rule:** never type location, pincode, login or personal data; never check out. Say so in the shot list.
- **Run:** 2026-10-14 (Opus).

### E09 · capture · real-site defects in screenshots
- **Seen:** a gift-box product card showed alt text instead of a photo (their image URL ends in `..webp`).
- **Why:** a broken image on the live site; it is real, so it cannot be edited out.
- **Fix:** scrolled past it within ~1 s and kept the camera on the page title; noted it in the shot list.
- **Check:** `[...document.images].filter(i => i.complete && !i.naturalWidth)` during capture.
- **Rule:** list broken images right after capture and plan shots around them; never repaint them.
- **Run:** 2026-10-14 (Opus).

### E10 · capture · fullPage screenshots and huge images (prevented)
- **Seen:** risk only. Fixed overlays (MENU pill, app banners) land mid-page in fullPage captures; list page was 22,989 px tall.
- **Why:** fullPage expands the viewport; Chromium canvas sources over ~16,384 px can fail or downsample.
- **Fix:** hid fixed/sticky elements except `<header>` before fullPage; cropped bodies to the needed range (home 6,900 px, list 9,000 px); simulated sticky scroll by drawing the body at `scroll + headerH` and the header crop on top.
- **Check:** image heights in `assets/` < 16,384 px.
- **Rule:** as above for every scroll animation.
- **Run:** 2026-10-14 (Opus).

## Build and render

### E11 · render · module import blocked on file://
- **Seen:** first test render crashed; `window.seek` undefined.
- **Why:** `<script type="module">import … from './lib/motion.js'` is blocked for file:// pages (opaque origin, CORS).
- **Fix:** pasted lib/motion.js into a classic `<script>` in index.html.
- **Check:** `stills.mjs` prints `PAGEERROR` lines; any error means stop.
- **Rule:** no ES modules in index.html.
- **Run:** 2026-10-13 (Sonnet test).

### E12 · render · frames captured before assets loaded
- **Seen:** risk of blank or fallback-font frames at the start of the render.
- **Why:** images and web fonts load asynchronously.
- **Fix:** `window.ready = (async () => { await images; await document.fonts.load(...); await document.fonts.ready; window.fontOK = {...}; })()`; render.mjs awaits it and logs `fontOK`; `seek` returns early until images exist.
- **Check:** the render log line `fonts {"…":true}`.
- **Rule:** always.
- **Run:** 2026-10-13 (Sonnet), extended 2026-10-14 (Opus).

### E13 · render · final render far too slow
- **Seen:** 20 s @ 60 fps / 4 sub took ~27 min (~0.7 output fps).
- **Why:** one PNG screenshot per sub-frame (`locator.screenshot`) piped to ffmpeg `tmix`, so 4× the screenshots plus Playwright overhead.
- **Fix:** average the sub-frames inside the page (running mean: `globalAlpha = 1/(k+1)` onto an accumulation canvas), one CDP `Page.captureScreenshot` (`optimizeForSpeed: true`, clip) per output frame. Same 20 s took 9.0 min. Drafts at `--fps 30 --sub 1` take ~3 min.
- **Check:** `out/silent.stats.json` records seconds per run.
- **Rule:** use the bundled render.mjs; review with `stills.mjs` + `sheet.py` (seconds) before any video render.
- **Run:** 2026-10-13 (Sonnet), fixed 2026-10-14 (Opus).

### E14 · render · fading a composite shows its layers (prevented)
- **Seen:** risk only: header and body images drawn separately at alpha 0.5 show through each other during a blur swap.
- **Why:** per-draw globalAlpha composites every layer independently.
- **Fix:** draw the phone UI into an offscreen canvas `U`, then `g.globalAlpha = a; g.filter = blur(...); g.drawImage(U, 0, 0)`.
- **Check:** stills at swap times.
- **Rule:** fade or blur only flattened composites.
- **Run:** 2026-10-14 (Opus).

## Design and motion

### E15 · design · dead time
- **Seen:** Sonnet draft had a static banner 2–4.5 s; the Sonnet final measured longest still 3.65 s and 3 dead seconds. Opus round 1 had flat holds on the cards and the store sheet.
- **Why:** shots planned as "show, then hold" with nothing moving between beats.
- **Fix:** pulled events earlier, slow push-in on photos, odometer digit rolls, camera push into the sheet. Opus final: longest still 0.55 s, 0 dead seconds.
- **Check:** `python compare.py out/final.mp4` (longest still < 1 s, dead seconds 0); contact sheet one frame per beat.
- **Rule:** every hold longer than 1 s needs camera drift or a rolling/ticking detail.
- **Run:** 2026-10-13 (Sonnet), 2026-10-14 (Opus).

### E16 · design · photo-filled type illegible
- **Seen:** "brownie." filled with a brownie photo vanished into the #2a1a13 background (dark texture on dark ground).
- **Why:** no contrast boundary between the image inside the letters and the canvas.
- **Fix:** cream `strokeText` (lineWidth 12) drawn under the masked photo, plus `filter: brightness(1.16) saturate(1.08)` on the photo.
- **Check:** look at the still where the word lands, before rendering.
- **Rule:** image-in-type on dark grounds always gets an outline or a light ground.
- **Run:** 2026-10-14 (Opus round 1).

### E17 · design · baked-in banner button leaked into a photo window
- **Seen:** an "ORDER NOW" button from the marketing banner appeared at the top of the phone window.
- **Why:** `cover()` fitted the banner to the whole frame, so its baked-in headline/button fell inside the window.
- **Fix:** explicit source crop on the product area: `drawImage(img, 0, 300, 1000, 845, dx, PY, 1847, PH)`.
- **Check:** stills of every frame where a banner is used as texture.
- **Rule:** crop marketing banners by source rect; only show baked-in text when it is the point.
- **Run:** 2026-10-14 (Opus round 1).

### E18 · design · captions over white UI (prevented)
- **Seen:** risk only: cream captions disappear when camera zooms push the white UI under the caption band.
- **Why:** light text on light UI.
- **Fix:** `strokeText` with the canvas color (lineWidth 18, round joins) under the cream fill.
- **Check:** phone-size test sheet during zoom shots.
- **Rule:** any text that can overlap UI gets a dark stroke.
- **Run:** 2026-10-14 (Opus).

### E19 · design · odometer digits spilled and flashed wrong numbers
- **Seen:** a rolling year "2004" showed stacked digits outside the slot and over the word beside it; on exit it flashed "3115" (each digit + 1).
- **Why:** the slot mask was 1.26 em tall (neighbour digits visible); the next digit (b + 1) was always drawn, so when the column dropped out it slid into view.
- **Fix:** mask one digit tall `rect(x, y - 0.8em, w, 0.9em)`; draw only the resting digit when `f < 0.002`; faster roll spring (110/21) with fewer digits (7 + 3 × index).
- **Check:** stills mid-roll, at rest, and during exit.
- **Rule:** any ticker/odometer shows exactly one cell at rest; always check its exit frames.
- **Run:** 2026-10-14 (Opus round 2).

### E20 · design · glyph slivers on frame 0 broke the loop
- **Seen:** tops of "It all" visible at t = 0; tops of "began" visible at its start beat.
- **Why:** masked entrance started only 1.1 em below the baseline while also scaled 116%, so ascenders reached into the mask.
- **Fix:** entry offset 1.5 em for slam entrances (scale + rise).
- **Check:** `node stills.mjs 0 out/zoom 0 <dur-0.05>`; both frames must be identical (empty).
- **Rule:** entrance offset ≥ 1.5 em when combined with scale; verify the first and last frames every round.
- **Run:** 2026-10-14 (Opus round 2).

### E21 · design · muddy morph from UI to card
- **Seen:** at 14.0 s the phone UI blurred over the chocolate background for ~0.25 s, looking grey and dirty.
- **Why:** the UI fade-out and the card fade-in shared the same slow spring.
- **Fix:** `spring(t - (morph - 0.06), 320, 36)` for both the outgoing UI and the incoming card fill.
- **Check:** frame strips: `ffmpeg -ss <t-0.05> -i out/draft.mp4 -vf "scale=180:-1,tile=8x1" -frames:v 1 strip.png`.
- **Rule:** inspect strips around every morph and push; crossfades between different contents stay under ~0.2 s.
- **Run:** 2026-10-14 (Opus round 3).

## Audio

### E22 · audio · one-pass loudnorm missed the target
- **Seen:** -17.2 LUFS for a -14 target.
- **Why:** single-pass loudnorm is dynamic and guesses loudness on the fly.
- **Fix:** pass 1 `loudnorm=I=-14:TP=-1:LRA=11:print_format=json`, pass 2 with `measured_I/TP/LRA/thresh/offset` and `linear=true` gave -14.0 / -13.9.
- **Check:** `ffmpeg -i out/final.mp4 -af ebur128=peak=true -f null -`.
- **Rule:** always two-pass; always print the ebur128 result.
- **Run:** 2026-10-13 (Sonnet test).

### E23 · audio · true peak too hot
- **Seen:** Sonnet final measured -0.1 dBTP (target ≤ -1).
- **Why:** the stem peaked near full scale before loudnorm; linear mode cannot limit enough.
- **Fix:** Opus run soft-clipped the master (`tanh`) before loudnorm, giving -3.5 dBTP. Alternatively add `alimiter=limit=0.85` before loudnorm.
- **Check:** ebur128 `Peak:` line ≤ -1.0.
- **Rule:** limit the stem first, then loudnorm; reject a mix with true peak above -1.
- **Run:** 2026-10-13 (Sonnet), fixed 2026-10-14 (Opus).

### E24 · audio · numpy shape mismatch layering sounds
- **Seen:** adding a 0.03 s click to a 0.09 s tone (`tick()[:len(t)] + tone`) failed; arrays had different lengths.
- **Why:** slicing a short array never makes it longer.
- **Fix:** `s = tone; k = tick(); s[:len(k)] += k`.
- **Check:** run audio.py right after each edit.
- **Rule:** allocate the longest buffer and add shorter layers into slices.
- **Run:** 2026-10-14 (Opus).

### E25 · audio · cue times retyped by hand
- **Seen:** Sonnet run kept animation times in index.html and a separate hand-typed cue list in audio.py.
- **Why:** two sources of truth drift on the first timing edit.
- **Fix:** Opus run put all event times in `<script id="tl" type="application/json">` inside index.html; JS reads it with `JSON.parse`, and audio.py reads it with a regex. Odometer clicks are generated from the same spring formula as the picture. 13/14 key events are within 4–7 ms.
- **Check:** `python compare.py --sync out/music.wav index.html`.
- **Rule:** one timeline JSON for picture and sound, always.
- **Run:** 2026-10-14 (Opus).

## Verification and delivery

### E26 · verify · wrong "loop not seamless" verdict
- **Seen:** reported the Sonnet loop as not seamless because `ImageChops.difference(first, last).getbbox()` was non-empty; measured properly, the seam was 0.0× a frame step.
- **Why:** a bounding box flags a single 1-level pixel difference.
- **Fix:** seam metric = mean |first − last| ÷ median frame-to-frame step (`compare.py`); < 1 means seamless.
- **Check:** `python compare.py out/final.mp4` (loop seam row).
- **Rule:** never judge with bounding boxes; quote the measured ratio.
- **Run:** 2026-10-13 (Sonnet), corrected 2026-10-14.

### E27 · verify · false sync alarms
- **Seen:** the slam at 0.00 s showed "+505 ms" and the Sonnet morph thumps showed "-245 ms".
- **Why:** onset detection cannot register an event at the first sample, and a lead-in whoosh starting 0.15–0.25 s early becomes the detected onset.
- **Fix:** excluded t = 0; read clicks and impacts without lead-ins: 2–7 ms in both runs.
- **Check:** `compare.py --sync` prints every event; read the outliers before concluding.
- **Rule:** an outlier means "check the cue design" first, not "audio is late".
- **Run:** 2026-10-14 (Opus).

### E28 · verify · film grain inflated motion numbers
- **Seen:** grain alone produced frame steps up to 0.59 at 108x192, above the 0.5 "moving" threshold.
- **Why:** the grain tile changes every 1/24 s.
- **Fix:** threshold 0.6, above the measured grain floor (static card 15.45–15.70 s: mean 0.20, max 0.59).
- **Check:** measure a known static hold before trusting "% moving".
- **Rule:** recompute the grain floor whenever grain alpha or tile size changes.
- **Run:** 2026-10-14 (Opus).

### E29 · deliver · master too big for phone/web viewers
- **Seen:** `38.4 MiB exceeds the 30 MiB upload limit`; the 40 MB master (CRF 16 + grain) did not reach phone/web viewers.
- **Why:** grain plus CRF 16 at 1080x1920 60 fps is ~16 Mbps.
- **Fix:** `ffmpeg -i out/final.mp4 -c:v libx264 -preset slow -crf 23 -c:a copy -movflags +faststart out/final_share.mp4` produced 10.7 MB; sent that and kept the master.
- **Check:** file size before sending or uploading.
- **Rule:** always produce final_share.mp4 < 25 MB.
- **Run:** 2026-10-14 (Opus).

---

## How to add to this file (end of every run, before delivering)
1. For every error hit and fixed in this run that is not already here, append an entry with the next free id (E30, E31, …) under the right stage heading, using the template below. Exact error text goes in **Seen**.
2. If an existing entry happened again, add `- **Seen again:** <date> <one line>` to it and make its **Rule** stricter.
3. Add or update the matching one-line rule in **Pre-flight rules** at the top.
4. Only real, reproduced problems with a fix that worked. No speculation, no duplicates.

```
### E## · <stage: setup|inputs|capture|policy|render|design|audio|verify|deliver> · <short title>
- **Seen:** <symptom, exact error text if any, where/when it appeared>
- **Why:** <root cause>
- **Fix:** <what actually fixed it: code, command, values>
- **Check:** <how to detect it early next time: command or still to look at>
- **Rule:** <what to do from the start so it never happens>
- **Run:** <YYYY-MM-DD (model/run name)>
```

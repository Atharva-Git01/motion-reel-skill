---
name: motion-reel
description: Make a product or showreel motion video rendered from code (Playwright + ffmpeg, no After Effects). Use when the user asks for a launch video, showreel, product reel, animated explainer or motion ad.
---

# Motion reel

Videos are pure functions of time: `window.seek(t)` paints frame t on a canvas, Playwright screenshots it, ffmpeg encodes it.

`<skill>` below means the folder that contains this SKILL.md (in Claude Code: `~/.claude/skills/motion-reel`).

## Always first: read the error log
Read `<skill>/ERRORS.md` in full before doing anything else in this skill. Every entry is a mistake an earlier run already made. Apply every line of its **Pre-flight rules** while planning, building and verifying. When this run hits and fixes an error that is not in the log, or an old one happens again, update ERRORS.md before delivering (step 9). Its last section says how.

## Prerequisites checklist (run right after reading the log)
Run `bash <skill>/studio/check-prereqs.sh` (Windows without bash: `powershell -ExecutionPolicy Bypass -File <skill>/setup.ps1`). It checks, in order:
- [ ] Node.js on PATH (`node -v`)
- [ ] ffmpeg on PATH (`ffmpeg -version`)
- [ ] Python on PATH (`python --version` or `python3 --version`)

If any item is missing, the script installs it (winget on Windows, brew on macOS, apt on Linux) and says so. After an install a fresh shell may be needed for PATH: if the re-check still fails, locate the new install (e.g. `C:\Program Files\nodejs`, the winget `Gyan.FFmpeg` bin folder) and add it to PATH for the session, then re-run the script. Do not start the pipeline until all three show OK, then proceed without asking again.

## 0. Set up the studio (once per project folder)
Bundled helpers live in `<skill>/studio/`:
- `render.mjs`: fast renderer. Motion-blur sub-frames are averaged inside the page; one CDP screenshot per frame; writes `<out>.stats.json`.
- `stills.mjs` + `sheet.py`: instant stills (no video) and labelled contact sheets for the critique loop.
- `explore.mjs`: phone-size capture (393x852 @3x) of any URL, with links, buttons and prices.
- `grab.mjs`: desktop capture. `compare.py`: QA metrics and audio sync. `audio.py` (example score to rewrite per film), `beats.py`, `lib/motion.js`, `CLAUDE.md`, `package.json`.

1. Pick a new project folder per film (default `~/motion-studio-<name>`). Copy the contents of `studio/` into it.
2. If there is no `node_modules/playwright`: `npm install && npx playwright install chromium` (uses the copied `package.json`).
3. Python deps if missing: `python -m pip install -r <skill>/requirements.txt`.
4. Read the project's `CLAUDE.md` (house rules) before writing any code.

## Inputs to collect first
Product + URL, duration, formats (9:16 / 1:1 / 16:9), brand colors + fonts, a reference (frame, video, or image folder), music (file or "synthesize").
If the URL does not resolve or has no own site, stop and ask for another source or the owner's assets. Never scrape third-party listings or invent screens.

## Pipeline
1. **Capture.** For 9:16 run `node explore.mjs <url> assets/m_home`, then capture the real pages along the user flow at phone size. Use `grab.mjs` (desktop) only for 16:9. Record tap boxes with smallest-area exact-text matches, download logo and product photos, list broken images, and list what was found.
2. If a reference exists, write docs/style_guide.md from it.
3. **Timeline.** Put every event time in `<script id="tl" type="application/json">` inside index.html. Picture and sound both read it.
4. Write docs/shotlist.md on the beat grid. Show it and wait for the user's OK, unless the user already asked for the finished video.
5. **Build** index.html: canvas `#c`, `window.seek(t)`, `window.ready` (images + fonts) and `window.fontOK`. Springs from `lib/motion.js`, inlined because `file://` blocks module imports.
6. **Critique loop, 3 rounds minimum.**
   - Round stills: `node stills.mjs 0.5 out/stills` then `python sheet.py out/stills out/contact_rN.png 10 216` (one frame per beat). Close-ups: `node stills.mjs 0 out/zoomN <t1> <t2> …`.
   - Score 1-10 on: hook, readability at phone size, motion, variety, composition, brand accuracy, sound sync. Fix the 3 worst problems, and log them in docs/review_log.md.
   - Motion draft: `node render.mjs --fps 30 --dur N --sub 1 --out out/draft.mp4` (~3 min for 20 s). Check frame strips around every morph and push, and a 360 px phone test sheet.
   - Sound: `python audio.py`, then `python compare.py --sync out/music.wav index.html`.
   - Repeat until every score is 8+.
7. **Final render.** `node render.mjs --fps 60 --dur N --sub 4` runs about 9 min for 20 s. Always run it in the background (Claude Code: `run_in_background`; other agents: run detached with output to `out/render.log` and poll for the `done` line). Then two-pass loudnorm to -14 LUFS (true peak ≤ -1) and mux into out/final.mp4.
8. **Verify and deliver.** `python compare.py out/final.mp4`: duration, LUFS, true peak, longest still < 1 s, 0 dead seconds, loop seam < 1. Make `out/final_share.mp4` (CRF 23, < 25 MB). Deliver final_share.mp4 + contact.png (+ master path) and say what you would improve next.
9. **Update ERRORS.md** with every new error tackled in this run (template at the bottom of that file), and refresh its Pre-flight rules.

## Hard rules
- Real product UI only (crop real screenshots). Never invent screens.
- Never type location, pincode, login or personal data into the target site, and never check out; stop at the first data prompt.
- No Math.random, no timers, no CSS transitions in render mode.
- Banned: corner labels, centered title on gradient, everything fading in.
- Third-party brands: say it is a private test unless the user has permission to publish.
- Other formats (1:1, 16:9) need their own layouts; do not claim them without making them.

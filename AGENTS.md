# AGENTS.md — start here if you are an AI agent

This repository is one skill, `motion-reel`. It turns a product URL into a motion reel rendered from code: an HTML canvas drawn by `window.seek(t)`, captured by Playwright, encoded by ffmpeg. Follow the four steps below in order.

## 1. Install (once)

- **Claude Code:** this folder must live at `~/.claude/skills/motion-reel` (all projects) or `<project>/.claude/skills/motion-reel` (one project). If it is somewhere else, copy it there. Claude Code then lists it as the `motion-reel` skill, and the user can run `/motion-reel`.
- **Any other agent:** leave the folder where it is. `<skill>` in SKILL.md means this folder.

## 2. Set up the machine (once)

Run one of these from this folder:

- `bash setup.sh` on macOS, Linux, or Git Bash on Windows
- `powershell -ExecutionPolicy Bypass -File setup.ps1` on Windows without bash

They check for Node, ffmpeg (with ffprobe) and Python, install any that are missing, then run `python -m pip install -r requirements.txt`.

If a script says *"Open a NEW shell"*, a tool was just installed and PATH is stale. Either open a new shell, or add the install folder to PATH for this session, then run the script again. Continue only when it prints `OK` and `Setup done`.

Playwright and Chromium are installed per film project, in SKILL.md step 0 (`npm install && npx playwright install chromium`).

## 3. Before every reel

1. Read [SKILL.md](SKILL.md) completely. It is the procedure; follow it step by step.
2. Read [ERRORS.md](ERRORS.md) completely, as SKILL.md requires, and apply every line of its **Pre-flight rules**.
3. Collect the inputs SKILL.md lists: product URL, duration, formats, brand colors and fonts, a reference, and music. Ask the user for anything missing.

## 4. After every reel

Append each new error you hit and fixed to ERRORS.md, using the template at the bottom of that file, and refresh its Pre-flight rules. This is how the skill improves from run to run.

## Notes for agents other than Claude Code

| SKILL.md / ERRORS.md says | Do this instead |
|---|---|
| `run_in_background` | Run the command detached with output going to `out/render.log`, then poll the log for the `done` line. Do not block on a ~9 minute render. |
| "Read" a file or image | Open it with whatever file or image viewer you have. You must actually look at the contact sheets and stills. |
| `SendUserFile` / deliver | Give the user the paths to `out/final_share.mp4` and the contact sheet. |
| `CLAUDE.md` in the project folder | Treat it as the house rules for the film, whatever your agent is. |

## Rules that are never optional

- Use real product UI only. Never invent screens, and never scrape third-party listing sites.
- Never type location, pincode, login or personal data into the target site, and never check out. Stop at the first data prompt.
- Render mode stays deterministic: no `Math.random`, timers, CSS transitions or `requestAnimationFrame`.
- If the brand is not the user's own, call the reel a private test unless the user says they have permission to publish.

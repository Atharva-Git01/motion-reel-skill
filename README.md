# motion-reel

An agent skill that turns a product website into a polished vertical motion reel, rendered entirely from code: an HTML canvas animated as a pure function of time, captured frame by frame with Playwright, encoded with ffmpeg. No After Effects, no paid tools, no stock templates.

> **AI agents:** read [AGENTS.md](AGENTS.md) first. It covers install, setup and how to start.

## What you get

- **Real UI, not mockups.** Captures the actual site at phone size (393x852 @3x) and animates crops of it.
- **A critique loop.** Contact sheets every round, scored on hook, readability, motion, variety, composition, brand accuracy and sound sync. It keeps fixing until every score is 8+.
- **Synthesized sound on the picture's timeline.** One timeline JSON drives both the animation and the audio cues, checked to within a few ms.
- **A fast renderer.** 20 s at 60 fps with 4x motion blur in about 9 minutes on a laptop.
- **Measured delivery.** −14 LUFS loudness, true peak ≤ −1 dBTP, no dead seconds, a seamless loop, plus a < 25 MB share copy.
- **An error log that learns.** [ERRORS.md](ERRORS.md) holds 29 mistakes earlier runs made and how they were fixed. The agent reads it before every run and appends new ones after.

## Requirements

| Tool | Version tested | Used for |
|---|---|---|
| Node.js | 24 (18+ should work) | Playwright capture and rendering |
| ffmpeg (with ffprobe) | 8.0 | Encoding, loudness, QA metrics |
| Python | 3.12 (3.10+) | Sound, beat grid, contact sheets, QA |
| Python packages | see [requirements.txt](requirements.txt) | numpy, scipy, librosa, soundfile, pillow |
| Playwright + Chromium | 1.64 | Installed per film project from [studio/package.json](studio/package.json) |

An agent that can run shell commands and read images (to review contact sheets) is needed. The skill was built and tested with Claude Code.

## Install

**Claude Code** (personal skill, available in every project):

```bash
git clone https://github.com/Atharva-Git01/motion-reel-skill ~/.claude/skills/motion-reel
```

Or download the ZIP, extract it, and rename the extracted folder to `~/.claude/skills/motion-reel`. For a single project, use `<project>/.claude/skills/motion-reel` instead.

**Other agents:** put the folder anywhere and tell the agent: *"Read AGENTS.md in this folder and follow it."*

## Setup (once per machine)

macOS, Linux, or Git Bash on Windows:

```bash
bash setup.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

Both check for Node, ffmpeg and Python, install whatever is missing (winget, Homebrew or apt), then install the Python packages. If a tool was just installed, open a new terminal and run the script again. The agent also runs these checks itself at the start of every reel, so this step is optional.

## Use

In Claude Code, type `/motion-reel` or just ask:

> Make a 20 second vertical launch reel for https://example.com. Brand colors #1a1a1a and #f5e6d3, synthesize the music.

The agent will ask for anything missing (product URL, duration, format, brand colors and fonts, a reference, music). It then works through:

1. **Capture** the real site at phone size
2. **Timeline** in a single JSON
3. **Shot list**, shown to you for an OK
4. **Build** `index.html` with `window.seek(t)`
5. **Critique loop** of at least 3 rounds
6. **Final render**, run in the background
7. **Loudness and QA** checks
8. **Deliver** `final_share.mp4` plus a contact sheet

Each film gets its own folder (default `~/motion-studio-<name>`).

## Repo layout

```
SKILL.md            the skill: steps, commands, hard rules (the agent follows this)
AGENTS.md           start here if you are an AI agent
ERRORS.md           error log: pre-flight rules + 29 Seen/Why/Fix/Check/Rule entries
requirements.txt    Python packages
setup.sh, setup.ps1 one-time machine setup
studio/             copied into every film project
  CLAUDE.md         house rules: render contract, look, sound, review loop
  package.json      Playwright dependency
  explore.mjs       phone-size capture of a URL (links, buttons, prices)
  grab.mjs          desktop capture (16:9 films only)
  render.mjs        fast renderer (in-page motion blur, CDP screenshots, ffmpeg pipe)
  stills.mjs        stills at chosen times, no video
  sheet.py          labelled contact sheet from stills
  audio.py          example synthesized score (rewrite per film)
  beats.py          beat grid from a supplied music track
  compare.py        QA metrics, A/B table, audio-vs-timeline sync check
  check-prereqs.sh  node / ffmpeg / python check + install
  lib/motion.js     spring and track helpers (inlined into index.html)
```

## Ground rules baked into the skill

- Uses only real product UI. It never invents screens or scrapes third-party listings.
- Never types location, login or personal data into the target site, and never checks out.
- Reels made with a brand you do not own are private tests. Get the brand's permission before you publish one.

## Contributing

If a run hits a new problem and fixes it, the agent appends an entry to `ERRORS.md` using the template at the bottom of that file. Pull requests with new entries are welcome.

## License

No license is granted: all rights reserved, © 2026 Atharva-Git01. You can view and fork this repo on GitHub. Ask the owner before reusing or redistributing it.

---
name: desktop-control
description: "Control the Windows desktop/GUI via the 'desktop' MCP: screenshot, click, type, hotkeys, scroll, launch apps, and run audited multi-step workflows. Use for any on-screen automation the engine's macOS-only computer_use can't do."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Desktop, Windows, GUI, Automation, RPA, Screenshot, Mouse, Keyboard, computer-use]
    related_skills: [bookkeeping, practice-management]
---

# Desktop Control (Windows)

You can see and operate this Windows machine through the **`desktop`** MCP server
(tools are prefixed by your client, e.g. `desktop.screenshot`). The engine's built-in
`computer_use` is macOS-only — use these tools instead on Windows.

## The loop: SEE → DECIDE → ACT → VERIFY
1. **SEE** — call `screenshot` first. Read the image; find the pixel coordinates of
   your target. Use `screen_info` (e.g. `1920x1080`) to reason about positions.
2. **DECIDE** — pick the exact (x, y). When unsure, `screenshot` a `region` to zoom.
3. **ACT** — `click` / `double_click` / `right_click` / `type_text` / `press_key` /
   `hotkey` / `scroll` / `drag` / `open_application`.
4. **VERIFY** — `screenshot` again to confirm the UI changed as expected. Never assume
   an action worked; look.

## Tools
- `screenshot(region?)` → returns the screen as an image. `region=[x,y,w,h]` to crop.
- `screen_info()` → `"WIDTHxHEIGHT"`.
- `move_mouse(x,y)`, `click(x,y,button,clicks)`, `double_click(x,y)`, `right_click(x,y)`
- `drag(x1,y1,x2,y2)`, `scroll(amount,x?,y?)` (positive=up, negative=down)
- `type_text(text)`, `press_key(key)` (`'enter'`,`'tab'`,`'esc'`,`'f5'`…),
  `hotkey(['ctrl','c'])`, `['win','r']`, `['alt','tab']`
- `locate_image(image_path, confidence)` → `"x,y"` center of a template PNG, or `"not found"`.
- `open_application(name)` → launches via the Run dialog (`'notepad'`, `'excel'`, a path).
- `run_workflow(steps_json, allow_unsafe=false)` → run a multi-step
  [`ai_rpa_system`](../../) workflow through the audited engine; a security scan blocks
  CRITICAL-risk workflows unless you pass `allow_unsafe=true`. Prefer this for repeatable
  sequences (e.g. logging into a desktop app, batch data entry).

## Safety (mandatory)
- **Confirm before destructive or outward-facing UI actions** — sending an email,
  submitting/filing a form, deleting files, anything that touches money or a client
  record. Describe what you'll click/type and get a go-ahead, unless pre-authorized.
- **Kill switch:** FAILSAFE is ON — the user can slam the mouse into a screen corner to
  abort instantly. Don't move the mouse to (0,0) yourself.
- Type secrets only when explicitly asked; never echo passwords back into chat.
- Go slow on irreversible steps; screenshot-verify between them.

## Good targets here
Driving QuickBooks Desktop / Lacerte UI where no API covers a step, filling desktop
forms, moving files in Explorer, operating any app that lacks an MCP. When an MCP or CLI
exists for the task (QuickBooks, KarbonCopy, Lacerte, browser), prefer that over pixels.

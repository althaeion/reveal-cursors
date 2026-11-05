---
name: swarm-cursors
description: Adds the "Swarm" effect to a website or a single page, where the page wipes to a blank canvas and a swarm of colorful multiplayer cursors (Figma-style) redraws it live, drawing boxes, typing text, dragging guides and duplicating elements until the page looks like it did before. Use this whenever the user says to add, install, put, apply, enable, or embed the swarm effect, swarm cursors, multiplayer cursors, "the page builds itself", "cursors rebuild the page", or the Swarm Rebuild extension on their website, site, landing page, portfolio, blog, or one specific page, even if they only say "add this to my site" or "put this on one page" while this skill is available. Also use it to change how the effect triggers (button, auto-run on load, hotkey, link), restrict it to certain pages, or remove it.
---

# Swarm Cursors for websites

A drop-in script. The visitor clicks a small floating button, the page fades to a blank
canvas, and a swarm of named, colored cursors rebuilds the real page layer by layer:
crosshair-drawn boxes, typed text, pen-tool lines, ruler guides, alt-drag duplicates, with
synthesized keyboard and piano sounds. A **Go live** button fades back to the real page.
Esc exits at any time.

It overlays the page instead of changing it. The real DOM is untouched, so SEO, forms,
analytics and scripts keep working underneath. It needs no build step and no dependencies,
and sends nothing off the page (no analytics, no third-party requests).

The engine is `assets/swarm-cursors.js`. It was adapted from the Swarm Rebuild Chrome
extension: it does not run on load by default, and it adds a trigger layer (button,
hotkey, auto-run, `?swarm` link), per-page targeting and a `data-swarm-ignore` attribute.

## Workflow

1. **Work out what the user has.** Pick the path that matches:
   - *Site files are available* (a project folder, Claude Code, Cowork, uploaded files):
     edit them directly. This is the best case.
   - *Only chat, and they pasted or described a page*: give them the finished HTML with
     the tag added, plus `swarm-cursors.js` as a file, and say where to put it.
   - *They named a platform* (WordPress, Shopify, Webflow, Next.js...): read
     `references/platforms.md` for that platform, deliver the file, and give the exact steps.

2. **Choose scope from their wording.** "This page", "one page", "the homepage" means only
   that page. "My website", "my site" means every page that shares the layout. If it is
   unclear, default to the one page they pointed at, since it is the easiest to widen later.

3. **Choose the trigger. Default to the floating button.** It is opt-in for each visitor, so
   it never ambushes anyone or hurts bounce rate, which is why it is the default. Only use
   `auto` if they ask for it to play on its own ("when the page loads", "automatically",
   "as an intro"). Map their wording to options:

   | They say | Option |
   | --- | --- |
   | plays by itself / on load / as an intro | `--trigger auto` (add `--delay 1500` to taste; `--once session` so it doesn't replay on every page view) |
   | no button / use my own link or button | `--trigger none`, then give any element `data-swarm-trigger` or a link `href="#swarm"` |
   | button on the left / top | `--position bottom-left` / `top-right` / `top-left` |
   | different button text | `--label "Watch it build"` |
   | only on the homepage / these pages | `--paths "/"` or `--paths "/,/about,/blog/*"` |
   | no keyboard shortcut | `--hotkey ""` (default is Alt+Shift+S) |
   | hide my cookie banner / chat widget from the rebuild | add `data-swarm-ignore` to that element |

   Two triggers are always on, in every mode: the hotkey, and `?swarm` in the URL (e.g.
   `yoursite.com/?swarm`), which is handy for a shareable link that plays on load.

4. **Install.**
   - Plain HTML: `python scripts/install.py PAGE.html [MORE.html ...] [options]`. It copies
     the engine next to the pages and adds one clearly marked block before `</body>`.
     Running it again updates the block, and `--remove` takes it out, leaving the file
     byte-identical to before.
   - Anything else: copy `assets/swarm-cursors.js` to the folder the platform serves as-is,
     get the tag from `python scripts/install.py --print [options]`, and place it per
     `references/platforms.md`.

5. **Verify, then say so honestly.** If Chromium and Playwright are available, run
   `python scripts/verify.py PAGE.html --shots /tmp/shots` (or a dev-server URL), and look
   at the screenshots. It checks that the script loads, the trigger exists, starting wipes
   the page into the canvas, Esc exits, and no JS errors occurred. If you cannot run it,
   tell the user what you did not test and give them the 20-second manual check: open the
   page, click the button, wait for it to build, press Esc.

6. **Report briefly:** which files changed, what visitors see, how to trigger it, and how to
   undo it. Include the licensing note below once.

## Licensing note (say it once, plainly)
The Swarm effect is **Joel Califa's** design (https://califa.github.io/swarm-site/), and the
Swarm Rebuild project this file comes from states that large parts of its animation engine
are adapted from his site, that the original has no license, and that the code should not
be reused without checking with him. The file keeps a credit header. That is fine for
private use or testing, but before putting it on a public or commercial site the user
should get his okay (or confirm they are the project's author), and should keep the credit
comment in place. Say this once, concisely, without lecturing. Do not refuse or stall, since
the user may already have permission.

## Known limits (tell the user if their page is affected)
- **WebGL canvases, playing video, and cross-origin iframes (maps, YouTube, embeds)** become
  gray placeholders. The Chrome extension could screenshot these, but a normal website
  script cannot. Normal images, SVG, text, gradients, shadows and CSS effects rebuild fine.
- It is a visual rebuild. Animations freeze at the moment of the click. Pages over about
  4,000 layers or 40,000px tall are capped.
- Sound is on by default, and browsers keep audio locked until the visitor clicks once.
  The button in the control bar (or the M key) mutes it.
- Built for desktop pointers. It runs on phones, but the experience is meant for a mouse.
- **Content-Security-Policy.** If the site's CSP has a `style-src` without `'unsafe-inline'`, the
  effect cannot render. The script detects this, never shows the button (or backs out
  instantly if already running), and logs a console warning, so visitors keep the normal
  page. To use the effect there, `'unsafe-inline'` has to be added to `style-src`, which is
  a security trade-off the site owner should decide. A CSP that blocks the script's own
  origin (`script-src`) stops it from loading at all. `verify.py` reports both cases.
- In single-page apps, `data-paths` is only checked on first load (see `references/platforms.md`).
- Page weight: 157 KB, about 44 KB gzipped, loaded with `defer` so it never blocks rendering.

## Files
- `assets/swarm-cursors.js`: the engine plus trigger layer. Options are documented in its header comment.
- `scripts/install.py`: add, update or remove the script on plain HTML pages. `--help` lists every option.
- `scripts/verify.py`: headless-browser smoke test.
- `references/platforms.md`: Vite, CRA, Astro, SvelteKit, Hugo, Jekyll, Next.js, WordPress, Shopify, Webflow, Squarespace, Wix, SPAs.

## Page API (for custom buttons or app code)
```js
SwarmCursors.start();          // begin
SwarmCursors.stop(true);       // exit with the fade-to-live reveal (false = instant)
SwarmCursors.isRunning();
window.addEventListener("swarm:start", ...);  // also "swarm:exit"
```

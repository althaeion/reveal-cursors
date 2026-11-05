#!/usr/bin/env python3
"""Smoke-test the Swarm Cursors effect on a page in headless Chromium.

  verify.py path/to/index.html            # a local file
  verify.py http://localhost:3000/        # a dev server or a live site
  verify.py page.html --shots out/        # also save before/during/after screenshots

Checks: the script loaded without JS errors, the trigger exists, starting it
wipes the page into the swarm canvas, Esc exits, and the page comes back.
Needs: pip install playwright && playwright install chromium
Exit code 0 = all checks passed.
"""
import argparse
import os
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright is not installed: pip install playwright && playwright install chromium")

BTN_JS = """(() => {
  const h = [...document.body.children].find(e => e.hasAttribute('data-swarm-ignore') && e.shadowRoot);
  return h ? h.shadowRoot.querySelector('button') : null;
})()"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--shots", help="folder for screenshots")
    ap.add_argument("--wait", type=float, default=6.0, help="seconds to let the swarm build (default 6)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=800)
    a = ap.parse_args()

    url = a.target if "://" in a.target else "file://" + os.path.abspath(a.target)
    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  ({detail})" if detail else ""))

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_page(viewport={"width": a.width, "height": a.height})
        errors, csp = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: csp.append(m.text) if "Content Security Policy" in m.text and "style" in m.text.lower() else None)
        page.goto(url, wait_until="load")
        page.wait_for_timeout(1500)  # lets trigger=auto fire if configured

        loaded = page.evaluate("typeof window.SwarmCursors === 'object'")
        check("script loaded (window.SwarmCursors exists)", loaded)
        if not loaded:
            print("      -> the <script> tag is missing, the path is wrong, or a CSP blocks it")
            browser.close()
            return 1

        cfg = page.evaluate("window.SwarmCursors.config")
        has_btn = page.evaluate(BTN_JS + " !== null")
        auto_ran = page.evaluate("window.SwarmCursors.isRunning()")
        print(f"      config: trigger={cfg['trigger']} hotkey={cfg['hotkey'] or '-'} paths={cfg['paths'] or 'all'}")
        if a.shots:
            page.screenshot(path=os.path.join(a.shots, "1-before.png"))

        if cfg["trigger"] == "button":
            check("floating button is on the page", has_btn, "if False: this path may be excluded by data-paths")
        elif cfg["trigger"] == "auto":
            check("auto trigger started the swarm", auto_ran, "False can mean reduced-motion or once=session")
        else:
            print("      trigger=none: starting through the API")

        if not auto_ran:
            if has_btn:
                page.evaluate(BTN_JS + ".click()")
            else:
                page.evaluate("window.SwarmCursors.start()")
        page.wait_for_timeout(1500)
        running = page.evaluate("window.SwarmCursors.isRunning()")
        check("swarm is running", running)
        if not running and csp:
            print("      -> blocked by the site's Content-Security-Policy: style-src needs 'unsafe-inline' (the effect backed out safely)")
        check("canvas layer covers the page", page.evaluate("!!document.querySelector('swarm-rebuild')"))
        if a.shots:
            page.screenshot(path=os.path.join(a.shots, "2-intro.png"))

        page.wait_for_timeout(int(a.wait * 1000))
        layers = page.evaluate("(() => { const h=document.querySelector('swarm-rebuild'); return h ? h.shadowRoot.querySelectorAll('*').length : 0 })()")
        check("swarm has built content", layers > 40, f"{layers} nodes in canvas")
        if a.shots:
            page.screenshot(path=os.path.join(a.shots, "3-building.png"))

        page.keyboard.press("Escape")
        page.wait_for_timeout(1200)
        check("Esc exits and removes the canvas", page.evaluate("!window.SwarmCursors.isRunning() && !document.querySelector('swarm-rebuild')"))
        if cfg["trigger"] == "button":
            back = page.evaluate("(() => { const b = " + BTN_JS + "; if(!b) return false; const h=b.getRootNode().host; return getComputedStyle(h).display !== 'none' })()")
            check("button comes back after exit", back)
        if a.shots:
            page.screenshot(path=os.path.join(a.shots, "4-after.png"))

        # Browsers report a missing /favicon.ico as a failed request, not a JS error, so this stays clean.
        check("no JavaScript errors", not errors, "; ".join(errors)[:200])
        check("no Content-Security-Policy style violations", not csp, "add 'unsafe-inline' to style-src" if csp else "")
        browser.close()

    ok = all(results)
    print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

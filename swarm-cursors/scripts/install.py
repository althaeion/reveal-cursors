#!/usr/bin/env python3
"""Add (or remove) the Swarm Cursors effect on plain HTML pages.

Copies assets/swarm-cursors.js next to the site's files and inserts one marked
<script> block before </body> in each page you name. Re-running updates the
block in place; --remove takes it out again. Nothing else in the page is touched.

Examples
  # one page, floating "Rebuild this page" button (default)
  install.py site/index.html

  # runs by itself 1s after the page loads, every page in the list
  install.py site/index.html site/about.html --trigger auto --delay 1000

  # no visible button; visitors use the hotkey / ?swarm / any [data-swarm-trigger]
  install.py site/index.html --trigger none

  # undo
  install.py site/index.html --remove

For React/Next/WordPress/Webflow/etc. use --print to get just the tag, then see
references/platforms.md for where it goes.
"""
import argparse
import html
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(HERE, "..", "assets", "swarm-cursors.js")
ASSET_NAME = "swarm-cursors.js"
START, END = "<!-- swarm-cursors:start -->", "<!-- swarm-cursors:end -->"
BLOCK_RE = re.compile(r"[ \t]*" + re.escape(START) + r".*?" + re.escape(END) + r"[ \t]*\r?\n?", re.S)

# option name -> (data attribute, default). Only non-defaults are written out.
OPTS = {
    "trigger": ("data-trigger", "button"),
    "label": ("data-label", "Rebuild this page"),
    "position": ("data-position", "bottom-right"),
    "hotkey": ("data-hotkey", "alt+shift+s"),
    "delay": ("data-delay", "800"),
    "once": ("data-once", ""),
    "paths": ("data-paths", ""),
    "reduced_motion": ("data-reduced-motion", "skip"),
}


def tag(src, args):
    attrs = []
    for name, (attr, default) in OPTS.items():
        val = getattr(args, name)
        if val is not None and str(val) != default:
            attrs.append(f'{attr}="{html.escape(str(val), quote=True)}"')
    extra = (" " + " ".join(attrs)) if attrs else ""
    return f'{START}\n<script src="{html.escape(src, quote=True)}" defer{extra}></script>\n{END}\n'


def rel_src(page, asset_path, absolute, root):
    if absolute:
        return "/" + os.path.relpath(asset_path, root).replace(os.sep, "/")
    return os.path.relpath(asset_path, os.path.dirname(page)).replace(os.sep, "/")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", help="HTML files to change")
    ap.add_argument("--remove", action="store_true", help="remove the block from the pages")
    ap.add_argument("--print", dest="print_only", action="store_true", help="print the tag and exit (no files touched)")
    ap.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    ap.add_argument("--asset-dir", help="where to copy swarm-cursors.js (default: common folder of the pages)")
    ap.add_argument("--site-root", help="web root, only needed with --absolute (default: the asset folder)")
    ap.add_argument("--absolute", action="store_true", help='write src="/path/swarm-cursors.js" instead of a relative path')
    ap.add_argument("--src", help="use this exact src (e.g. a CDN/GitHub URL); skips copying the file")
    ap.add_argument("--trigger", choices=["button", "auto", "none"])
    ap.add_argument("--label")
    ap.add_argument("--position", choices=["bottom-right", "bottom-left", "top-right", "top-left"])
    ap.add_argument("--hotkey", help='e.g. "alt+shift+s"; "" disables')
    ap.add_argument("--delay", type=int, help="ms before trigger=auto fires")
    ap.add_argument("--once", choices=["session"], help="trigger=auto: only once per browser session")
    ap.add_argument("--paths", help='limit to paths, e.g. "/,/about,/blog/*"')
    ap.add_argument("--reduced-motion", dest="reduced_motion", choices=["skip", "ignore"])
    args = ap.parse_args()

    if args.print_only:
        sys.stdout.write(tag(args.src or "/" + ASSET_NAME, args))
        return 0
    if not args.pages:
        ap.error("give at least one HTML page (or use --print)")

    pages = [os.path.abspath(p) for p in args.pages]
    for p in pages:
        if not os.path.isfile(p):
            sys.exit(f"not a file: {p}")

    asset_dir = os.path.abspath(args.asset_dir) if args.asset_dir else os.path.commonpath([os.path.dirname(p) for p in pages])
    asset_path = os.path.join(asset_dir, ASSET_NAME)
    root = os.path.abspath(args.site_root) if args.site_root else asset_dir

    changed = 0
    for page in pages:
        with open(page, encoding="utf-8", newline="") as f:
            text = f.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        had = bool(BLOCK_RE.search(text))

        if args.remove:
            new = BLOCK_RE.sub("", text)
            verb = "removed from" if had else "nothing to remove in"
        else:
            src = args.src or rel_src(page, asset_path, args.absolute, root)
            block = tag(src, args).replace("\n", nl)
            if had:
                new = BLOCK_RE.sub(lambda _m: block, text, count=1)
                verb = "updated in"
            else:
                m = list(re.finditer(r"</body\s*>", text, re.I))
                if m:
                    i = m[-1].start()
                    new = text[:i] + block + text[i:]
                else:
                    new = text + nl + block
                verb = "added to"
        if new != text:
            changed += 1
            if not args.dry_run:
                with open(page, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
        print(f"{verb}: {page}")

    if not args.remove and not args.src:
        if args.dry_run:
            print(f"would copy engine to: {asset_path}")
        else:
            os.makedirs(asset_dir, exist_ok=True)
            if os.path.abspath(ASSET) != asset_path:
                shutil.copyfile(ASSET, asset_path)
            print(f"engine file: {asset_path}")
    if args.remove:
        print(f"(the file {ASSET_NAME} was left in place; delete it yourself if no other page uses it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

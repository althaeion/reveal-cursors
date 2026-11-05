# Where the script goes, by platform

The engine is one file, `assets/swarm-cursors.js` (157 KB, about 44 KB gzipped).
Every platform needs the same two things: **(1)** the file reachable at some URL,
**(2)** one `<script>` tag pointing at it. Use `scripts/install.py --print` to get
the tag with the right options.

Tested in a real browser: plain HTML pages and a complex inner-scrolling app page.
The framework and CMS recipes below are standard patterns but were not run against
those platforms. After wiring one up, run `scripts/verify.py http://localhost:PORT/`
against the dev server, or open the page, click the button and press Esc.

If a platform strips `data-*` attributes from the script tag, pass options through a
config object defined *before* the script instead. Same names, no `data-` prefix:

```html
<script>window.SwarmCursorsConfig = { trigger: "button", position: "bottom-left" }</script>
<script src="/swarm-cursors.js" defer></script>
```

## Contents
- Plain HTML / static sites
- Vite, Create React App, Astro, SvelteKit, Hugo, Jekyll
- Next.js
- WordPress
- Shopify
- Webflow, Squarespace, Wix, Framer and other hosted builders
- Single-page apps: the one gotcha

## Plain HTML / static sites
Run the installer: `python scripts/install.py index.html` (add more pages to the list,
or use `--paths` if one shared template renders every page).

## Vite, Create React App, Astro, SvelteKit, Hugo, Jekyll
Put the file in the folder the framework serves as-is, then add the tag to the root HTML template.

| Framework | Copy the file to | Tag goes in |
| --- | --- | --- |
| Vite / CRA | `public/` | `index.html` |
| Astro | `public/` | the layout's `<body>` end, or one page's `.astro` file |
| SvelteKit | `static/` | `src/app.html` |
| Hugo | `static/` | `layouts/_default/baseof.html` (or one page template) |
| Jekyll | project root or `assets/` | `_layouts/default.html` |

The tag is `<script src="/swarm-cursors.js" defer></script>`. For Vite or CRA the installer
can do it: `python scripts/install.py index.html --asset-dir public --absolute --site-root public`
(Vite may print a harmless "can't be bundled without type=module" notice for a file in `public/`.)

If the site is served from a sub-path (GitHub Pages project sites such as `user.github.io/repo/`),
a leading `/` points at the wrong place. Use a relative src (`swarm-cursors.js`), or
`/repo/swarm-cursors.js`.

## Next.js
Copy the file to `public/swarm-cursors.js`, then use `next/script`.

App Router, whole site, in `app/layout.tsx`:
```tsx
import Script from "next/script";
// inside <body>, after {children}:
<Script src="/swarm-cursors.js" strategy="afterInteractive" data-trigger="button" />
```
For one page only, put the same `<Script>` in that page's `page.tsx` instead. In the Pages
Router, use it in `pages/_app.tsx` (everywhere) or in the single page file.

## WordPress
WordPress blocks `.js` uploads in the Media Library, so put the file in the active
(child) theme folder via FTP/File Manager, then enqueue it from `functions.php`:
```php
add_action('wp_enqueue_scripts', function () {
    if (!is_front_page()) return;   // delete this line to run on every page
    wp_enqueue_script('swarm-cursors', get_stylesheet_directory_uri() . '/swarm-cursors.js', [], '1.0', true);
    wp_add_inline_script('swarm-cursors', 'window.SwarmCursorsConfig = { trigger: "button" };', 'before');
});
```
Swap the condition for `is_page('about')` or `is_single()` to target other pages. Without
code access, a "header/footer scripts" plugin can add the tag, but the file still has to be
hosted somewhere reachable.

## Shopify
Upload `swarm-cursors.js` under Online Store, then Themes, then Edit code, then Assets. In `layout/theme.liquid`
before `</body>`:
```liquid
{% if template == 'index' %}{{ 'swarm-cursors.js' | asset_url | script_tag }}{% endif %}
```
`script_tag` can't carry data attributes, so set options first with a
`<script>window.SwarmCursorsConfig = {...}</script>` line.

## Webflow, Squarespace, Wix, Framer and other hosted builders
These have a "custom code" or "code injection" area, usually at both site and per-page
level (menu names change often, so look for those words). Page-level injection is how you
limit the effect to one page. Two limits shape the approach:
- Their inline code boxes are too small for a 157 KB file, so the engine has to be
  hosted at a URL and the injected code is just the one `<script src="https://...">` tag.
- Some plans gate custom code behind a paid tier.

Where to host the file: your own web hosting, or any static host (Netlify Drop, Cloudflare
Pages, GitHub Pages, Vercel). A CDN that serves GitHub repos (jsDelivr) works too, but only
for public repos, which makes the code public. Read the licensing note in SKILL.md first.

## Single-page apps: the one gotcha
The script loads once and stays alive across client-side route changes. That has two effects:
- `data-paths` is checked when the page first loads, not on each route change. To show the
  effect on one route only, mount the `<script>` from that route's component, or skip the
  built-in button (`data-trigger="none"`) and call `window.SwarmCursors.start()` from your
  own button in that route.
- The snapshot is taken from the live DOM at the moment of the click, so whatever route
  is on screen is what gets rebuilt. No extra work needed there.

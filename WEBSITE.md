# Website

This repository holds two things:

- `README.md` is my GitHub profile README. GitHub shows it on github.com/maxnkosi, so keep it short and personal. Website notes live here instead.
- The personal website: a single static page with no build step.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole site: markup, styles and a small script, all inline |
| `logo.svg` | The wordmark. The page uses it as a CSS mask, so it takes the text colour in light and dark mode |
| `favicon.svg` | Browser tab icon made from the logo. Switches colour with the system theme |
| `favicon.ico` | 32px fallback icon for browsers without SVG favicon support |
| `apple-touch-icon.png` | 180px icon for iOS home screens |
| `og-image.png` | 1200×630 preview image shown when the link is shared |

## Run it locally

Any static file server works. From the repository root:

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. Use a server rather than opening `index.html` straight from disk, because some browsers block the `logo.svg` mask on `file://` URLs.

## Deploy with GitHub Pages

1. On GitHub, open the repository's **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to *Deploy from a branch*, choose `main` and `/ (root)`, and save.
3. After a minute the site is live at https://maxnkosi.github.io/maxnkosi/. Every push to `main` redeploys it.

### Using a custom domain

If the site moves to its own domain, or to a `maxnkosi.github.io` repository, update the absolute URLs in the `<head>` of `index.html`: `canonical`, `og:url`, `og:image` and `twitter:image`. Link previews need absolute image URLs, so these can't be relative.

## Updating the metadata

- **Title and description:** the `<title>` and `<meta name="description">` tags. Keep `og:description` and `twitter:description` in step with the description.
- **Share image:** replace `og-image.png` with another 1200×630 PNG. Preview the result with a link preview checker after deploying; platforms cache previews, so changes can take a while to show.
- **Icons:** if the logo changes, regenerate `favicon.svg`, `favicon.ico` and `apple-touch-icon.png` from the new `logo.svg`.

# 🚀 Go Live + Rank #1 for "Thando Frans"

Everything here is built and ready. Ranking #1 for your name is won on three fronts:
**(1) an owned site with your exact name in the right places, (2) a consistent identity across
profiles Google already trusts, and (3) time + a few links pointing at you.** This is the plan.

> **Reality check:** the site is fully optimised on-page. Getting to #1 also depends on how many
> other "Thando Frans" already have a footprint, and it takes **1–4 weeks** for Google to index and
> rank a new site. Do the steps below and you're doing everything that's in your control.

---

## ✅ Step 1 — Get the domain (biggest single lever)

`thandofrans.com` is **available for ~$11.25/year**. An exact-match domain for your name is the
strongest signal you can own — buy it. `.com` is best; `thandofrans.dev` (~$10) is a fine alt.

- Buy at: https://vercel.com/domains/search?q=thandofrans.com (or any registrar — Namecheap, GoDaddy, etc.)

The whole site (canonical URL, structured data, sitemap) is **already pointed at `https://thandofrans.com`**,
so once the domain is live, everything lines up automatically.

## ✅ Step 2 — Put the site online

The site (`index.html`, `sitemap.xml`, `robots.txt`, `404.html`, `CNAME`) is in this repo. Pick one:

### Option A — GitHub Pages + your domain (free hosting, recommended)
1. Create a **new repo** named exactly `thandofrans28-ship-it.github.io`.
2. Copy `index.html`, `404.html`, `sitemap.xml`, `robots.txt`, `CNAME` into it and push.
3. Repo → **Settings → Pages** → Source: `main` / root → Save.
4. In **Settings → Pages → Custom domain**, enter `thandofrans.com` (the `CNAME` file already sets this).
5. At your domain registrar, add DNS records pointing to GitHub Pages:
   - Four `A` records → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - One `CNAME` record: `www` → `thandofrans28-ship-it.github.io`
6. Tick **Enforce HTTPS**. Live at `https://thandofrans.com` in a few minutes.

### Option B — Vercel or Netlify (also free)
1. Sign in with GitHub at vercel.com (or netlify.com).
2. Import this repo (or a copy) → it auto-detects a static site → Deploy.
3. Add `thandofrans.com` as a custom domain in the dashboard and follow its DNS steps.

### Option C — instant free URL, no domain yet
Enable GitHub Pages on **this** repo (Settings → Pages → main/root). You'll get
`https://thandofrans28-ship-it.github.io/thandofrans28-ship-it/`. If you use this instead of the
domain, change every `https://thandofrans.com` in `index.html`, `sitemap.xml`, `robots.txt` to that URL.

## ✅ Step 3 — Tell Google it exists (don't wait to be found)

1. Go to **[Google Search Console](https://search.google.com/search-console)** → add `thandofrans.com`.
2. Verify (DNS TXT record or HTML tag).
3. **Submit your sitemap:** `https://thandofrans.com/sitemap.xml`.
4. Use **URL Inspection → Request Indexing** on your homepage to jump the queue.
5. Repeat for [Bing Webmaster Tools](https://www.bing.com/webmasters) (feeds Bing + others).

## ✅ Step 4 — One consistent identity everywhere (the "sameAs" web)

Google ranks you higher when it's confident all these are the *same* Thando Frans. Make every
profile use the **same name, same photo, same one-line bio, and link back to `thandofrans.com`:**

- **LinkedIn** — add the website to your profile; use the bio from `personal-brand/`.
- **GitHub** — set your profile website to `thandofrans.com` (already linked in your README).
- **Google/Gmail account** — set a real profile photo (shows in some results).
- Optional but powerful: **X/Twitter, dev.to, Medium, ORCID, a Google Developer profile** — each is
  another trusted page that says "Thando Frans → thandofrans.com".

The site's structured data already lists your GitHub + LinkedIn as `sameAs`. Add your new site URL
back into each of those profiles so the links go both ways.

## ✅ Step 5 — Earn a few links + fresh content (what pushes you over the top)

- Get your site linked from anywhere real: your school, a project's Play Store listing, a hackathon
  page, a blog you write on. Even 2–3 genuine links move a low-competition name query a lot.
- **Publish occasionally.** A short post ("How I built Pathfinda") on the site or on LinkedIn/dev.to,
  each linking home, tells Google the identity is active. Fresh > static.
- Pin your Pathfinda post on LinkedIn; put `thandofrans.com` in every bio and email signature.

---

## 📋 One-time checklist

- [ ] Buy `thandofrans.com`
- [ ] Deploy the site (Option A/B/C)
- [ ] Enforce HTTPS
- [ ] Add site to Google Search Console + submit sitemap + request indexing
- [ ] Add site to Bing Webmaster Tools
- [ ] Put `thandofrans.com` on LinkedIn, GitHub, and your email signature
- [ ] Make name + photo + bio identical across all profiles
- [ ] (Later) Add an OG share image (`og.png`) and reference it in `index.html`
- [ ] (Later) Publish one short post and link it home

## ⚠️ Fix the identity conflict first

Your site says **electrical engineering**; your README/Notion say **actuarial science**. Google — and
admissions officers — reward one clear story. Pick the lane you're actually committing to and make the
site, README, LinkedIn, and bios all say the same thing. (Tell me which and I'll align everything.)

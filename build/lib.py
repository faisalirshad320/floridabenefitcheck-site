#!/usr/bin/env python3
"""FloridaBenefitCheck clean static rebuild — shared template + verified data."""
import os, re, json, html
from bs4 import BeautifulSoup

ROOT   = "/home/claude/floridabenefitcheck-site"
MIRROR = os.path.join(ROOT, "mirror")
DIST   = os.path.join(ROOT, "dist")
BASE   = "https://www.floridabenefitcheck.com"

# ---- single source of truth for freshness (verified Oct 2 2026) ----
UPDATED_FULL  = "October 1, 2026"     # data effective date (FY2027 SNAP COLA took effect Oct 1 2026)
UPDATED_MONTH = "October 2026"
UPDATED_ISO   = "2026-10-02"

CSS_HREF = "/assets/fbc.css"

# Monetization / analytics placeholders.
# NOTE: no AdSense (ca-pub) or GA4 ID was present anywhere in the live markup/JS,
# so these are left as clearly-marked, inert placeholders for Faisal to fill.
MONETIZATION_HEAD = """<!-- MONETIZATION/ANALYTICS: paste your real IDs to activate.
<meta name="google-adsense-account" content="ca-pub-XXXXXXXXXXXXXXXX">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-XXXXXXXXXX');</script>
-->"""

def esc(s):
    return html.escape(s, quote=True)

def head(title, description, path, keywords, jsonld=None, hreflang=False, robots="index, follow"):
    """path: canonical path beginning and ending with '/' (or '/' for home)."""
    canonical = BASE + path
    og_img = BASE + "/og-image.png"
    parts = []
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f'<title>{esc(title)}</title>')
    parts.append(f'<meta name="description" content="{esc(description)}">')
    parts.append('<meta name="author" content="FloridaBenefitCheck.com">')
    parts.append(f'<meta name="keywords" content="{esc(keywords)}">')
    parts.append(f'<meta name="robots" content="{robots}">')
    parts.append('<meta name="googlebot" content="index, follow, max-video-preview:-1, max-image-preview:large, max-snippet:-1">')
    parts.append(f'<link rel="canonical" href="{canonical}">')
    if hreflang:
        parts.append(f'<link rel="alternate" hreflang="en-US" href="{BASE}/">')
        parts.append(f'<link rel="alternate" hreflang="es-US" href="{BASE}/es/">')
        parts.append(f'<link rel="alternate" hreflang="ht" href="{BASE}/ht/">')
        parts.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/">')
    # Open Graph (per-page — fixes the old all-homepage bug)
    parts.append(f'<meta property="og:title" content="{esc(title)}">')
    parts.append(f'<meta property="og:description" content="{esc(description)}">')
    parts.append(f'<meta property="og:url" content="{canonical}">')
    parts.append('<meta property="og:site_name" content="FloridaBenefitCheck.com">')
    parts.append('<meta property="og:locale" content="en_US">')
    parts.append(f'<meta property="og:image" content="{og_img}">')
    parts.append('<meta property="og:image:width" content="1200">')
    parts.append('<meta property="og:image:height" content="630">')
    parts.append('<meta property="og:image:alt" content="FloridaBenefitCheck.com — free Florida benefits eligibility checker">')
    parts.append('<meta property="og:type" content="website">')
    parts.append('<meta name="twitter:card" content="summary_large_image">')
    parts.append(f'<meta name="twitter:title" content="{esc(title)}">')
    parts.append(f'<meta name="twitter:description" content="{esc(description)}">')
    parts.append(f'<meta name="twitter:image" content="{og_img}">')
    parts.append('<meta name="theme-color" content="#0E4D91">')
    parts.append('<link rel="icon" href="/favicon.ico" sizes="any">')
    parts.append('<link rel="icon" type="image/svg+xml" href="/favicon.svg">')
    parts.append('<link rel="apple-touch-icon" href="/apple-touch-icon.png">')
    parts.append('<link rel="manifest" href="/site.webmanifest">')
    parts.append(f'<link rel="stylesheet" href="{CSS_HREF}">')
    if jsonld:
        if isinstance(jsonld, (list, dict)):
            parts.append('<script type="application/ld+json">'+json.dumps(jsonld, ensure_ascii=False)+'</script>')
        else:
            parts.append('<script type="application/ld+json">'+jsonld+'</script>')
    parts.append(MONETIZATION_HEAD)
    return "\n".join(parts)

# ---- Exact header markup (static; mobile menu wired by small JS at body end) ----
HEADER = '''<a href="#main-content" class="skip-to-content">Skip to main content</a>
<header class="sticky top-0 z-50 glass border-b border-white/30 shadow-sm no-print">
<div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
<a class="flex items-center gap-2 font-bold text-xl" style="color:#0E4D91" href="/"><span class="text-2xl" aria-hidden="true">☀️</span><span class="hidden sm:block">FloridaBenefitCheck</span><span class="sm:hidden">FBC</span></a>
<nav class="hidden md:flex items-center gap-6" aria-label="Primary">
<a class="text-sm font-medium text-slate-700 hover:text-blue-700 transition-colors" href="/programs/">Programs</a>
<a class="text-sm font-medium text-slate-700 hover:text-blue-700 transition-colors" href="/tools/">Tools</a>
<a class="text-sm font-medium text-slate-700 hover:text-blue-700 transition-colors" href="/blog/">Blog</a>
<a class="text-sm font-medium text-slate-700 hover:text-blue-700 transition-colors" href="/about/">About</a>
<div class="flex items-center gap-1 text-xs text-slate-500 border border-slate-200 rounded-full px-2 py-1">
<a class="px-1 py-0.5 bg-blue-700 text-white rounded-full text-xs" href="/">EN</a>
<a class="px-1 py-0.5 hover:bg-slate-100 rounded-full text-xs" href="/es/">ES</a>
<a class="px-1 py-0.5 hover:bg-slate-100 rounded-full text-xs" href="/ht/">HT</a></div>
<a class="text-sm font-semibold text-white px-4 py-2 rounded-lg shadow transition-all hover:shadow-lg" style="background:linear-gradient(135deg, #F97316, #EF4444);animation:pulse-glow 2s ease-in-out infinite" href="/checker/">Check Now →</a>
</nav>
<button id="fbc-menu-btn" class="md:hidden p-2" aria-label="Toggle menu" aria-expanded="false" aria-controls="fbc-mobile-menu"><div class="w-5 h-0.5 bg-slate-700 mb-1"></div><div class="w-5 h-0.5 bg-slate-700 mb-1"></div><div class="w-5 h-0.5 bg-slate-700"></div></button>
</div>
<div id="fbc-mobile-menu" class="md:hidden bg-white border-t border-slate-100 px-4 py-4 flex-col gap-3" style="display:none">
<a href="/programs/" class="block text-base font-medium text-slate-700 py-2 border-b border-slate-100">Programs</a>
<a href="/tools/" class="block text-base font-medium text-slate-700 py-2 border-b border-slate-100">Tools</a>
<a href="/blog/" class="block text-base font-medium text-slate-700 py-2 border-b border-slate-100">Blog</a>
<a href="/about/" class="block text-base font-medium text-slate-700 py-2 border-b border-slate-100">About</a>
<a href="/checker/" class="block text-center text-white font-semibold py-3 rounded-xl mt-2" style="background:linear-gradient(135deg, #F97316, #EF4444)">Check My Eligibility Now →</a>
</div>
</header>'''

FOOTER = f'''<footer class="bg-slate-900 text-slate-300 no-print" role="contentinfo">
<div class="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
<div><div class="flex items-center gap-2 text-white font-bold text-lg mb-3"><span aria-hidden="true">☀️</span> FloridaBenefitCheck</div>
<p class="text-sm text-slate-400 leading-relaxed mb-4">Florida's free benefits eligibility checker. 2026 income limits, no signup required.</p>
<p class="text-xs text-slate-500">🇺🇸 Serving Floridians since 2026</p></div>
<div><h2 class="text-white font-semibold mb-3 text-sm uppercase tracking-wider">Programs</h2><ul class="space-y-2">
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/snap/">SNAP (Food Stamps)</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/medicaid/">Florida Medicaid</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/ssi/">SSI Benefits</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/liheap/">LIHEAP (Energy)</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/wic/">WIC Nutrition</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/tanf/">TANF Cash Help</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/kidcare/">Florida KidCare</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/lifeline/">Lifeline Phone</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/programs/eitc/">EITC Tax Credit</a></li></ul></div>
<div><h2 class="text-white font-semibold mb-3 text-sm uppercase tracking-wider">Free Tools</h2><ul class="space-y-2">
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/tools/snap-calculator/">SNAP Benefit Calculator</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/tools/income-cliff/">Income Cliff Calculator</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/tools/coverage-gap/">Coverage Gap Tool</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/tools/document-checklist/">Document Checklist</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/tools/county-finder/">County Resource Finder</a></li></ul>
<h2 class="text-white font-semibold mb-3 mt-5 text-sm uppercase tracking-wider">Languages</h2><div class="flex gap-2">
<a class="text-xs px-2 py-1 bg-blue-700 text-white rounded" href="/">English</a>
<a class="text-xs px-2 py-1 border border-slate-600 text-slate-300 rounded hover:bg-slate-700" href="/es/">Español</a>
<a class="text-xs px-2 py-1 border border-slate-600 text-slate-300 rounded hover:bg-slate-700" href="/ht/">Kreyòl</a></div></div>
<div><h2 class="text-white font-semibold mb-3 text-sm uppercase tracking-wider">Resources</h2><ul class="space-y-2">
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/blog/">Benefits Blog</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/blog/florida-ebt-card-guide/">EBT Card Help</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/about/">About Us</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/contact/">Contact</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/privacy/">Privacy Policy</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/disclaimer/">Disclaimer</a></li>
<li><a class="text-sm text-slate-400 hover:text-white transition-colors" href="/accessibility/">Accessibility</a></li></ul>
<div class="mt-4 p-3 bg-slate-800 rounded-lg text-xs text-slate-500"><strong class="text-slate-400">Official Apply Links:</strong><br>
<a href="https://www.myflorida.com/accessflorida/" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:underline">ACCESS Florida</a> • <a href="https://www.ssa.gov/" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:underline">SSA.gov</a></div></div>
</div>
<div class="border-t border-slate-800 py-6 px-4"><div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
<p class="text-xs text-slate-500">© 2026 FloridaBenefitCheck.com — operated by <a href="https://www.omniaventures.org/" class="hover:text-white">Omnia Ventures</a>. Not affiliated with any government agency. For informational purposes only.</p>
<p class="text-xs text-slate-600">Data updated {UPDATED_MONTH} • Sources: USDA FNS, Florida DCF, SSA.gov, HHS</p></div></div>
</footer>'''

MENU_JS = '''<script>(function(){var b=document.getElementById('fbc-menu-btn'),m=document.getElementById('fbc-mobile-menu');if(b&&m){b.addEventListener('click',function(){var o=m.style.display!=='none';m.style.display=o?'none':'flex';b.setAttribute('aria-expanded',String(!o));});}})();</script>'''

def page(title, description, path, keywords, body_main, jsonld=None, hreflang=False,
         related_html="", extra_body_js="", robots="index, follow"):
    h = head(title, description, path, keywords, jsonld=jsonld, hreflang=hreflang, robots=robots)
    return f'''<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
{h}
</head>
<body class="min-h-full flex flex-col antialiased">
{HEADER}
{body_main}
{related_html}
{FOOTER}
{MENU_JS}
{extra_body_js}
</body>
</html>'''

def write(path, content):
    fp = os.path.join(DIST, path.strip("/"))
    if path.endswith("/") or path == "/":
        fp = os.path.join(DIST, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(content)
    return fp

def extract_main(mirror_rel):
    """Return (main_html, related_html) from a saved mirror page, scripts stripped."""
    fp = os.path.join(MIRROR, mirror_rel)
    soup = BeautifulSoup(open(fp, encoding="utf-8").read(), "html.parser")
    main = soup.find("main")
    # the internal-link section injected after <main>
    related = soup.find("section", id="fbc-related")
    if related:
        for s in related.find_all("script"):
            s.decompose()
    # strip any scripts inside main (none expected)
    if main:
        for s in main.find_all("script"):
            s.decompose()
    return (str(main) if main else ""), (str(related) if related else "")

if __name__ == "__main__":
    print("lib ok; UPDATED:", UPDATED_FULL)

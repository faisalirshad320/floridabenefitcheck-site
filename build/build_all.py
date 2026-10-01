#!/usr/bin/env python3
"""Full reproducible build: python3 build/build_all.py  -> dist/"""
import os, sys, glob, shutil, subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE)
DIST=os.path.join(ROOT,"dist")
# keep hand-written JS across rebuilds
js=open(os.path.join(DIST,"assets/fbc.js"),encoding="utf-8").read() if os.path.exists(os.path.join(DIST,"assets/fbc.js")) else None
if os.path.exists(DIST): shutil.rmtree(DIST)
os.makedirs(os.path.join(DIST,"assets"))
js=open(os.path.join(HERE,"fbc.js"),encoding="utf-8").read()  # build/fbc.js is the source of truth
open(os.path.join(DIST,"assets/fbc.js"),"w",encoding="utf-8").write(js)
pass
shutil.copy(os.path.join(ROOT,"mirror/_next/static/chunks/3ewlfipzmmntq.css"),os.path.join(DIST,"assets/fbc.css"))
import content, pages, sitefiles
content.build_disk_pages()
pages.build_home(); pages.build_checker(); pages.build_cliff(); pages.build_docs(); pages.build_tools_index(); pages.build_legal(); pages.build_snap_limits(); pages.build_coverage_gap(); pages.build_ssi(); pages.build_medicaid(); pages.build_kidcare(); pages.build_cliff_blog(); pages.build_snap_calc(); pages.build_ebt_guide()
# repoint links to pages that never existed on the live site
LINKFIX={"/blog/florida-coverage-gap-explained/":"/tools/coverage-gap/","/blog/florida-liheap-application-2026/":"/programs/liheap/"}
for f in glob.glob(os.path.join(DIST,"**/*.html"),recursive=True):
    t=open(f,encoding="utf-8").read(); o=t
    for a,b in LINKFIX.items():
        t=t.replace("https://www.floridabenefitcheck.com"+a,b).replace('"'+a+'"','"'+b+'"')
    # make absolute self-links root-relative (smaller, environment-proof)
    t=t.replace('href="https://www.floridabenefitcheck.com/','href="/')
    if t!=o: open(f,"w",encoding="utf-8").write(t)
sitefiles.css(); n=sitefiles.sitemap()
open(os.path.join(DIST,"robots.txt"),"w").write(sitefiles.ROBOTS)
open(os.path.join(DIST,"llms.txt"),"w").write(sitefiles.LLMS)
open(os.path.join(DIST,"site.webmanifest"),"w").write(sitefiles.MANIFEST)
sitefiles.images()
import lib
open(os.path.join(DIST,"404.html"),"w").write(lib.page("Page Not Found — FloridaBenefitCheck.com","The page you requested could not be found.","/404.html","",
  '<main id="main-content" class="max-w-3xl mx-auto px-4 py-20 text-center"><h1 class="text-4xl font-bold text-slate-900 mb-3">404 — Page not found</h1><p class="text-slate-600 mb-6">That page doesn\'t exist. Try the eligibility checker or browse the programs.</p><a href="/checker/" class="inline-block text-white font-semibold px-6 py-3 rounded-xl mr-2" style="background:linear-gradient(135deg, #F97316, #EF4444)">Check My Eligibility →</a><a href="/programs/" class="inline-block font-semibold px-6 py-3 rounded-xl border-2 border-slate-200 text-slate-700">Browse Programs</a></main>',robots="noindex, follow"))
# canonical/og absolute URLs must stay absolute: re-absolutize inside <link rel=canonical>/hreflang (they use href=)
for f in glob.glob(os.path.join(DIST,"**/*.html"),recursive=True):
    t=open(f,encoding="utf-8").read()
    t=t.replace('rel="canonical" href="/','rel="canonical" href="https://www.floridabenefitcheck.com/')
    import re
    t=re.sub(r'(rel="alternate" hreflang="[^"]+" href=")/',r'\1https://www.floridabenefitcheck.com/',t)
    open(f,"w",encoding="utf-8").write(t)
# .htaccess for Apache side of Cloudways stack: 404 page, caching, security headers
open(os.path.join(DIST,".htaccess"),"w").write("""ErrorDocument 404 /404.html
Options -Indexes
DirectoryIndex index.html
<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set X-Frame-Options "SAMEORIGIN"
  <FilesMatch "\\.(css|js|png|ico|svg|webmanifest)$">
    Header set Cache-Control "public, max-age=2592000"
  </FilesMatch>
  <FilesMatch "\\.(html|xml|txt)$">
    Header set Cache-Control "public, max-age=3600, must-revalidate"
  </FilesMatch>
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml text/plain
</IfModule>
""")
print("BUILD OK — sitemap urls:",n)

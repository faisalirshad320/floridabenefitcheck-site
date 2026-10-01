#!/usr/bin/env python3
"""robots.txt, sitemap.xml, llms.txt, manifest, supplemental CSS, brand images."""
import os, sys, glob, re, datetime
sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import BASE, DIST, UPDATED_ISO, UPDATED_FULL, UPDATED_MONTH
from PIL import Image, ImageDraw, ImageFont

# ---- supplemental CSS (appended to compiled bundle) ----
SUPP = """
/* --- supplemental (static rebuild) --- */
.text-opacity-90{opacity:.92}
.prose{max-width:65ch;color:#334155;line-height:1.75}.prose h2{font-size:1.5rem;font-weight:700;color:#0f172a;margin:2rem 0 .75rem}.prose h3{font-size:1.2rem;font-weight:700;color:#0f172a;margin:1.5rem 0 .5rem}.prose p{margin:.9rem 0}.prose ul,.prose ol{padding-left:1.5rem;margin:.9rem 0}.prose li{margin:.35rem 0}.prose a{color:#1d4ed8;text-decoration:underline}.prose table{width:100%;border-collapse:collapse;font-size:.9rem}.prose th,.prose td{border:1px solid #e2e8f0;padding:.5rem .6rem;text-align:left}.prose th{background:#f8fafc}
#fbc-mobile-menu[style*="flex"]{display:flex}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.mr-2{margin-right:.5rem}.py-20{padding-top:5rem;padding-bottom:5rem}.overflow-x-auto{overflow-x:auto}
"""
def css():
    p=os.path.join(DIST,"assets/fbc.css")
    t=open(p,encoding="utf-8").read()
    if "supplemental (static rebuild)" not in t:
        open(p,"a",encoding="utf-8").write(SUPP)

# ---- robots ----
ROBOTS=f"""User-agent: *
Allow: /
Disallow: /assets/fbc.js

Sitemap: {BASE}/sitemap.xml

# AI / LLM crawlers explicitly welcomed (GEO)
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Amazonbot
Allow: /
User-agent: cohere-ai
Allow: /
User-agent: CCBot
Allow: /
User-agent: Bytespider
Allow: /
User-agent: meta-externalagent
Allow: /
# LLM content index: {BASE}/llms.txt
"""

# ---- sitemap ----
PRIORITY={"/":("weekly","1.0"),"/es/":("monthly","0.9"),"/ht/":("monthly","0.9"),"/checker/":("monthly","0.95"),"/programs/":("monthly","0.9"),"/tools/":("monthly","0.8"),"/blog/":("weekly","0.8"),"/about/":("yearly","0.4"),"/contact/":("yearly","0.3"),"/accessibility/":("yearly","0.3")}
def sitemap():
    urls=[]
    for f in sorted(glob.glob(os.path.join(DIST,"**/index.html"),recursive=True)):
        rel="/"+os.path.relpath(os.path.dirname(f),DIST).replace("\\","/")
        rel="/" if rel=="/." else rel.rstrip("/")+"/"
        if rel in ("/privacy/","/disclaimer/"): continue  # noindex
        cf,pr=PRIORITY.get(rel,("monthly","0.85" if rel.startswith(("/programs/","/blog/","/tools/")) else "0.6"))
        urls.append(f"<url><loc>{BASE}{rel}</loc><lastmod>{UPDATED_ISO}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>")
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+"\n".join(urls)+"\n</urlset>\n"
    # hreflang on the three language homes
    xml=xml.replace(f"<url><loc>{BASE}/</loc>",f"<url><loc>{BASE}/</loc><xhtml:link rel=\"alternate\" hreflang=\"en-US\" href=\"{BASE}/\"/><xhtml:link rel=\"alternate\" hreflang=\"es-US\" href=\"{BASE}/es/\"/><xhtml:link rel=\"alternate\" hreflang=\"ht\" href=\"{BASE}/ht/\"/>")
    open(os.path.join(DIST,"sitemap.xml"),"w").write(xml)
    return len(urls)

# ---- llms.txt (richer: direct answers + verified figures) ----
LLMS=f"""# FloridaBenefitCheck.com

> Free, independent eligibility checker and guide for Florida government assistance programs: SNAP (food stamps), Medicaid, SSI, LIHEAP, WIC, TANF, Florida KidCare, Lifeline and the EITC. All figures use the 2026 HHS poverty guidelines and FY2027 SNAP allotments; data last verified {UPDATED_FULL}. Available in English, Spanish and Haitian Creole. Not affiliated with the State of Florida — always apply through MyACCESS Florida (https://www.myflorida.com/accessflorida/).

## Key 2026 facts (cite these)
- 2026 Federal Poverty Level (HHS, published Jan 15 2026): $15,960/yr for 1 person, +$5,680 per additional person ($21,640 for 2, $27,320 for 3, $33,000 for 4).
- Florida SNAP gross income limit = 200% FPL: $2,660/mo (1), $3,607 (2), $4,554 (3), $5,500 (4), $6,447 (5), $7,394 (6), $8,340 (7), $9,287 (8). Net limit = 100% FPL.
- Maximum monthly SNAP allotment (FY2027, effective Oct 1 2026): $306 (1), $562 (2), $808 (3), $1,023 (4), $1,217 (5), $1,463 (6), $1,616 (7), $1,841 (8).
- 2026 SSI federal benefit rate: $994/mo individual, $1,491/mo couple (2.8% COLA). Resource limit $2,000 / $3,000.
- Tax-year-2026 EITC maximum: $664 (no children), $4,427 (1), $7,316 (2), $8,231 (3+).
- Florida Medicaid: children ≤200% FPL, pregnant women ≤196% FPL, aged/disabled ≤88% FPL, parents ≤~26% FPL; Florida has NOT expanded Medicaid, so childless adults do not qualify on income — about 800,000 Floridians are in the coverage gap.
- LIHEAP ≤150% FPL (up to ~$700). WIC ≤185% FPL. TANF ≈38% FPL (max $303/mo family of 3). Florida KidCare ≤200% FPL ($0–$20/mo). Lifeline ≤135% FPL or SNAP/Medicaid enrollment ($9.25/mo discount).

## Eligibility tools
- [Benefit Eligibility Checker]({BASE}/checker/): Answer 3 questions, screens all 9 programs instantly.
- [Florida SNAP (Food Stamp) Calculator]({BASE}/tools/snap-calculator/): Estimate monthly SNAP with FY2027 deductions (standard $217–$308, shelter cap $769, $25 minimum).
- [Income Cliff Calculator]({BASE}/tools/income-cliff/): Will a raise cost more in lost benefits than it pays?
- [Coverage Gap Tool]({BASE}/tools/coverage-gap/): 2026 Medicaid coverage-gap thresholds by household size.
- [Document Checklist]({BASE}/tools/document-checklist/): Documents needed to apply for each program.
- [County Resource Finder]({BASE}/tools/county-finder/): DCF office phone numbers and food banks by county; Florida 2-1-1.

## Programs
- [Florida SNAP]({BASE}/programs/snap/): 2026 income limits, benefit amounts, how to apply.
- [Florida Medicaid]({BASE}/programs/medicaid/): income limits by category, coverage gap.
- [SSI]({BASE}/programs/ssi/): 2026 payment amounts, income and asset limits.
- [LIHEAP]({BASE}/programs/liheap/): energy bill assistance.
- [WIC]({BASE}/programs/wic/): nutrition for pregnant women, infants, children under 5.
- [TANF]({BASE}/programs/tanf/): temporary cash assistance.
- [Florida KidCare]({BASE}/programs/kidcare/): children's health insurance.
- [Lifeline]({BASE}/programs/lifeline/): phone/internet discount.
- [EITC]({BASE}/programs/eitc/): earned income tax credit.

## Guides
- [How to Apply for SNAP in Florida (2026)]({BASE}/blog/how-to-apply-snap-florida-2026/)
- [Florida SNAP Income Limits 2026]({BASE}/blog/florida-snap-income-limits-2026/)
- [Florida Medicaid Eligibility 2026]({BASE}/blog/florida-medicaid-eligibility-2026/)
- [Florida Medicaid Expansion 2026]({BASE}/blog/florida-medicaid-expansion-2026/)
- [Florida SNAP/EBT Restrictions 2026]({BASE}/blog/florida-snap-restrictions-ebt-2026/)
- [Using Florida EBT on Amazon]({BASE}/blog/amazon-ebt-florida-snap-guide/)
- [The Florida Benefits Cliff]({BASE}/blog/income-cliff-snap-florida/)
- [Florida EBT Card Guide]({BASE}/blog/florida-ebt-card-guide/): EBT customer service 1-888-356-3281, balance, lost card, deposit dates (1st–28th by case number).

## Languages
- [Español]({BASE}/es/) · [Kreyòl Ayisyen]({BASE}/ht/)

## Sources
USDA Food and Nutrition Service (SNAP COLA FY2027), HHS ASPE 2026 Poverty Guidelines (Federal Register 2026-00755), Social Security Administration (2026 SSI FBR), IRS (TY2026 EITC), Florida DCF / AHCA.
"""

MANIFEST='{"name":"FloridaBenefitCheck","short_name":"FBC","description":"Free Florida benefits eligibility checker","start_url":"/","display":"standalone","background_color":"#ffffff","theme_color":"#0E4D91","icons":[{"src":"/apple-touch-icon.png","sizes":"180x180","type":"image/png"},{"src":"/icon-512.png","sizes":"512x512","type":"image/png"}]}'

FAVICON_SVG='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0E4D91"/><circle cx="32" cy="32" r="13" fill="#FBBF24"/><g stroke="#FBBF24" stroke-width="4" stroke-linecap="round"><line x1="32" y1="6" x2="32" y2="13"/><line x1="32" y1="51" x2="32" y2="58"/><line x1="6" y1="32" x2="13" y2="32"/><line x1="51" y1="32" x2="58" y2="32"/><line x1="13.6" y1="13.6" x2="18.6" y2="18.6"/><line x1="45.4" y1="45.4" x2="50.4" y2="50.4"/><line x1="13.6" y1="50.4" x2="18.6" y2="45.4"/><line x1="45.4" y1="18.6" x2="50.4" y2="13.6"/></g></svg>'

def sun(d,cx,cy,r,col="#FBBF24"):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
    import math
    for k in range(8):
        a=k*math.pi/4; x1=cx+math.cos(a)*r*1.35; y1=cy+math.sin(a)*r*1.35; x2=cx+math.cos(a)*r*1.9; y2=cy+math.sin(a)*r*1.9
        d.line([x1,y1,x2,y2],fill=col,width=max(3,r//5))

def images():
    bold="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"; sans="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    # OG 1200x630
    im=Image.new("RGB",(1200,630),"#0E4D91"); d=ImageDraw.Draw(im)
    d.rectangle([0,0,1200,630],fill="#0E4D91")
    for i in range(630):  # subtle gradient
        d.line([0,i,1200,i],fill=(14,77,145) if i<10 else (int(14+(21-14)*i/630),int(77+(101-77)*i/630),int(145+(192-145)*i/630)))
    sun(d,150,150,52)
    d.text((240,105),"FloridaBenefitCheck",font=ImageFont.truetype(bold,64),fill="white")
    d.text((240,200),"Free Florida Benefits Eligibility Checker",font=ImageFont.truetype(sans,38),fill="#DBEAFE")
    d.text((240,290),"SNAP · Medicaid · SSI · LIHEAP · WIC · TANF",font=ImageFont.truetype(sans,30),fill="#FDE68A")
    d.text((240,335),"KidCare · Lifeline · EITC — 2026 income limits",font=ImageFont.truetype(sans,30),fill="#FDE68A")
    d.rounded_rectangle([240,420,760,500],radius=18,fill="#F97316"); d.text((270,440),"Check in 60 seconds — free, no signup",font=ImageFont.truetype(bold,28),fill="white")
    d.text((240,545),"English · Español · Kreyòl Ayisyen   •   floridabenefitcheck.com",font=ImageFont.truetype(sans,24),fill="#BFDBFE")
    im.save(os.path.join(DIST,"og-image.png"),optimize=True)
    # apple touch 180 + icon 512 + favicon.ico
    for size,name in [(180,"apple-touch-icon.png"),(512,"icon-512.png")]:
        ic=Image.new("RGB",(size,size),"#0E4D91"); dd=ImageDraw.Draw(ic); sun(dd,size//2,size//2,int(size*0.2)); ic.save(os.path.join(DIST,name),optimize=True)
    ico=Image.new("RGB",(64,64),"#0E4D91"); dd=ImageDraw.Draw(ico); sun(dd,32,32,13); ico.save(os.path.join(DIST,"favicon.ico"),sizes=[(16,16),(32,32),(48,48)])
    open(os.path.join(DIST,"favicon.svg"),"w").write(FAVICON_SVG)

if __name__=="__main__":
    css(); n=sitemap()
    open(os.path.join(DIST,"robots.txt"),"w").write(ROBOTS)
    open(os.path.join(DIST,"llms.txt"),"w").write(LLMS)
    open(os.path.join(DIST,"site.webmanifest"),"w").write(MANIFEST)
    images()
    open(os.path.join(DIST,"404.html"),"w").write(lib.page("Page Not Found — FloridaBenefitCheck.com","The page you requested could not be found.","/404.html","",
      '<main id="main-content" class="max-w-3xl mx-auto px-4 py-20 text-center"><h1 class="text-4xl font-bold text-slate-900 mb-3">404 — Page not found</h1><p class="text-slate-600 mb-6">That page doesn\'t exist. Try the eligibility checker or browse the programs.</p><a href="/checker/" class="inline-block text-white font-semibold px-6 py-3 rounded-xl mr-2" style="background:linear-gradient(135deg, #F97316, #EF4444)">Check My Eligibility →</a><a href="/programs/" class="inline-block font-semibold px-6 py-3 rounded-xl border-2 border-slate-200 text-slate-700">Browse Programs</a></main>',robots="noindex, follow"))
    print("sitemap urls:",n,"| site files + images written")

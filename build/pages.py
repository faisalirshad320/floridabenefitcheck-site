#!/usr/bin/env python3
"""Authored / interactive pages: home, checker, income-cliff, document-checklist, privacy, disclaimer, accessibility, tools index."""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import BASE, UPDATED_FULL, UPDATED_MONTH, UPDATED_ISO
from content import SEO, graph, trail_for, fix_dates
from bs4 import BeautifulSoup

JS_TAG = '<script src="/assets/fbc.js" defer></script>'

def related(links, lead="Programs and guides that often go together with this one."):
    lis="".join(f'<li><a href="{u}" style="display:block;padding:12px 14px;background:#fff;border:1px solid #E2E8F0;border-radius:12px;color:#15803D;font-weight:600;text-decoration:none;line-height:1.35">{t} →</a></li>' for t,u in links)
    return f'''<section aria-labelledby="fbc-related-h" style="background:#F8FAFC;border-top:1px solid #E2E8F0;padding:40px 16px"><div style="max-width:64rem;margin:0 auto">
<h2 id="fbc-related-h" style="font-size:1.5rem;font-weight:700;color:#0F172A;margin:0 0 6px">Related Florida benefits</h2>
<p style="color:#475569;margin:0 0 18px;font-size:.95rem">{lead}</p>
<ul style="list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px">{lis}</ul>
<p style="margin:18px 0 0"><a href="/checker/" style="color:#15803D;font-weight:700">Check all 9 programs at once with the free eligibility checker →</a></p></div></section>'''

TOOL_HERO = lambda badge,bg,fg,h1,p: f'''<div class="text-center mb-8"><span class="inline-block text-xs font-bold px-3 py-1 rounded-full mb-3 uppercase tracking-wider" style="background:{bg};color:{fg}">{badge}</span><h1 class="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">{h1}</h1><p class="text-slate-500 text-lg">{p}</p></div>'''

def faq_schema(qa):
    return {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]}

def webapp(path,name,desc):
    return {"@type":"WebApplication","@id":BASE+path+"#app","name":name,"description":desc,"url":BASE+path,
            "applicationCategory":"GovernmentApplication","operatingSystem":"Any","browserRequirements":"Requires JavaScript",
            "isAccessibleForFree":True,"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"publisher":{"@id":BASE+"/#org"},"inLanguage":"en-US"}

HOME_FAQ=[
 ("Is this tool free to use?","Yes, completely free. We never charge for eligibility checks, never require signup, and never sell your data."),
 ("Does this tool store my information?","No. All calculations happen in your browser. We collect zero personal data."),
 ("How accurate are the results?",f"Results are estimates based on official 2026 income thresholds (verified {UPDATED_MONTH}). Only the program agency makes final determinations. Always apply officially."),
 ("Why does Florida have such a low Medicaid limit for adults?","Florida has not expanded Medicaid under the ACA. Adults without children do not qualify at any income; parents only up to about 26% of the federal poverty level, leaving roughly 800,000 people in the coverage gap."),
 ("Can I check eligibility for someone else?","Yes, just enter their household information. Our tool checks for the household as a whole."),
 ("What are the 2026 Florida SNAP income limits?","Florida uses a gross income limit of 200% of the federal poverty level: $2,660/month for 1 person, $3,607 for 2, $4,554 for 3 and $5,500 for 4. Maximum monthly SNAP allotments (effective October 1, 2026) are $306, $562, $808 and $1,023 respectively."),
]

def build_home():
    path="/"; title,desc,kw=SEO[path]
    main,rel=lib.extract_main("index.html")
    main=fix_dates(main)
    soup=BeautifulSoup(main,"html.parser")
    # replace the embedded static checker card contents with a JS mount point
    for d in soup.find_all("div"):
        cls=" ".join(d.get("class",[]))
        if "shadow-xl" in cls and "max-w-2xl" in cls and d.find(string=re.compile("How many people live")):
            d.clear(); d["data-fbc-checker"]="1"; d["aria-live"]="polite"
            d.append(BeautifulSoup('<noscript><p class="text-sm text-slate-600">Enable JavaScript to use the interactive checker, or <a href="/programs/" class="text-blue-700 underline">browse the 2026 income limits for each program</a>.</p></noscript>',"html.parser"))
            break
    # strengthen the hero freshness badge wording (single source of truth)
    main=str(soup)
    main=main.replace("2026 Income Limits — Updated "+UPDATED_MONTH, f"2026 Income Limits — Verified {UPDATED_FULL}")
    # newsletter form has no backend in a static build: keep UI, make it mailto-safe
    main=main.replace('placeholder="your@email.com"','placeholder="your@email.com" disabled')
    g=graph(path,title,desc,trail_for(path),extra=[webapp("/","Florida Benefits Eligibility Checker","Free instant check for SNAP, Medicaid, SSI, LIHEAP, WIC, TANF, KidCare, Lifeline and EITC eligibility in Florida using 2026 income limits."),faq_schema(HOME_FAQ)])
    html=lib.page(title,desc,path,kw,main,jsonld=g,hreflang=True,related_html=rel,extra_body_js=JS_TAG)
    lib.write(path,html)

def build_checker():
    path="/checker/"; title,desc,kw=SEO.get(path,("Florida Benefits Eligibility Checker 2026 — Free, 60 Seconds",
        "Free Florida benefits eligibility checker. Answer 3 questions and instantly see which of 9 programs you may qualify for: SNAP, Medicaid, SSI, LIHEAP, WIC, TANF, KidCare, Lifeline, EITC. 2026 limits, no signup, no data stored.",
        "florida benefits eligibility checker,am i eligible for snap florida,do i qualify for medicaid florida,benefits calculator florida 2026"))
    SEO[path]=(title,desc,kw)
    chips="".join(f'<span class="flex items-center gap-1"><span style="color:#10B981">✓</span> {p}</span>' for p in ["SNAP","Medicaid","SSI","LIHEAP","WIC","TANF","KidCare","Lifeline","EITC"])
    main=f'''<main id="main-content" class="min-h-screen py-10 px-4" style="background:linear-gradient(180deg, #EFF6FF 0%, #F8FAFC 100%)"><div class="max-w-3xl mx-auto">
<div class="text-center mb-8"><span class="inline-block text-xs font-bold px-3 py-1 rounded-full mb-3 uppercase tracking-wider" style="background:#DBEAFE;color:#1D4ED8">Free Tool — 2026 Data</span>
<h1 class="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">Florida Benefits Eligibility Checker</h1>
<p class="text-slate-500 text-lg">Answer 3 questions — we check 9 programs instantly. No signup, no data stored.</p>
<div class="flex flex-wrap justify-center gap-3 mt-4 text-xs text-slate-500">{chips}</div></div>
<div class="bg-white rounded-2xl shadow-xl border border-slate-100 p-6 sm:p-8 max-w-2xl mx-auto" data-fbc-checker="1" aria-live="polite"><noscript><p class="text-sm text-slate-600">Enable JavaScript to use the interactive checker, or <a href="/programs/" class="text-blue-700 underline">browse the 2026 income limits for each program</a>.</p></noscript></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm"><h2 class="font-bold text-slate-900 mb-3">About This Tool</h2>
<p class="text-sm text-slate-600 leading-relaxed mb-4">This checker uses the 2026 Federal Poverty Level guidelines (published by HHS on January 15, 2026) and Florida-specific income thresholds from the USDA Food and Nutrition Service, Florida Department of Children and Families, Social Security Administration, and Department of Health and Human Services. SNAP maximum allotments reflect the FY2027 cost-of-living adjustment effective October 1, 2026.</p>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
<div class="bg-slate-50 rounded-xl p-3"><div class="font-bold text-slate-900">{UPDATED_FULL}</div><div class="text-xs text-slate-500">Data Last Verified</div></div>
<div class="bg-slate-50 rounded-xl p-3"><div class="font-bold text-slate-900">9 Programs</div><div class="text-xs text-slate-500">Programs Checked</div></div>
<div class="bg-slate-50 rounded-xl p-3"><div class="font-bold text-slate-900">60 Seconds</div><div class="text-xs text-slate-500">Time Required</div></div></div></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm"><h2 class="font-bold text-slate-900 mb-3">How the checker decides</h2>
<ul class="space-y-2 text-sm text-slate-600 leading-relaxed">
<li><strong>SNAP:</strong> gross income at or below 200% of the poverty level (Florida's broad-based categorical eligibility limit); households with a member 60+ or disabled use the 100% net-income test instead.</li>
<li><strong>Medicaid:</strong> children up to 211% FPL (under 1), 145% (ages 1–5) and 138% (6–18), pregnant women up to 196% FPL, aged/disabled up to 88% FPL, parents only up to 26% FPL (KFF, January 2026). Florida has not expanded Medicaid, so childless adults do not qualify on income alone.</li>
<li><strong>SSI:</strong> age 65+ or disabled, countable income under the 2026 limit and resources under $2,000 ($3,000 for a couple). The 2026 federal benefit rate is $994 (individual) / $1,491 (couple).</li>
<li><strong>LIHEAP</strong> 150% FPL • <strong>WIC</strong> 185% FPL • <strong>TANF</strong> about 38% FPL • <strong>KidCare</strong> 215% FPL • <strong>Lifeline</strong> 135% FPL or SNAP/Medicaid enrollment • <strong>EITC</strong> tax-year-2026 IRS income limits (max credit $8,231 with 3+ children).</li></ul></div>
</div></main>'''
    rel=related([("Florida SNAP (food stamps) income limits","/programs/snap/"),("Florida Medicaid eligibility","/programs/medicaid/"),("SSI in Florida: eligibility and payments","/programs/ssi/"),("How to apply for SNAP in Florida, step by step","/blog/how-to-apply-snap-florida-2026/")])
    g=graph(path,title,desc,trail_for(path),extra=[webapp(path,"Florida Benefits Eligibility Checker",desc)])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel,extra_body_js=JS_TAG))

def build_cliff():
    path="/tools/income-cliff/"; title,desc,kw=SEO[path]
    opts="".join(f'<option value="{n}"{" selected" if n==3 else ""}>{n} person{"s" if n>1 else ""}</option>' for n in range(1,9))
    main=f'''<main id="main-content" class="min-h-screen py-10 px-4 bg-slate-50"><div class="max-w-3xl mx-auto">
{TOOL_HERO("Florida-Only Tool","#DBEAFE","#1D4ED8","Income Cliff Calculator","If I earn $200 more per month, will I lose more in benefits than I gain? This calculator shows you the real net impact of a raise.")}
<div class="bg-white rounded-2xl shadow-xl border border-slate-100 p-6 sm:p-8" data-fbc-cliff="1">
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
<div><label for="cl-hh" class="block text-sm font-semibold text-slate-700 mb-2">Household Size</label><select id="cl-hh" data-hh class="w-full p-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:outline-none">{opts}</select></div>
<div><label for="cl-cur" class="block text-sm font-semibold text-slate-700 mb-2">Current Monthly Income</label><div class="relative"><span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold">$</span><input id="cl-cur" data-cur type="number" min="0" value="1500" class="w-full pl-8 p-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:outline-none text-lg font-semibold"></div></div>
<div><label for="cl-prop" class="block text-sm font-semibold text-slate-700 mb-2">Proposed Monthly Income (after raise)</label><div class="relative"><span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold">$</span><input id="cl-prop" data-prop type="number" min="0" value="1700" class="w-full pl-8 p-3 border-2 rounded-xl focus:border-blue-500 focus:outline-none text-lg font-semibold" style="border-color:#3B82F6"></div></div>
<div class="flex flex-col gap-2"><span class="text-sm font-semibold text-slate-700">Your Situation</span>
<label class="flex items-center gap-2 text-sm text-slate-600 cursor-pointer"><input data-kids type="checkbox" class="w-4 h-4 accent-blue-600" checked>Have children</label>
<label class="flex items-center gap-2 text-sm text-slate-600 cursor-pointer"><input data-dis type="checkbox" class="w-4 h-4 accent-blue-600">Have a disability</label>
<label class="flex items-center gap-2 text-sm text-slate-600 cursor-pointer"><input data-cit type="checkbox" class="w-4 h-4 accent-blue-600" checked>US Citizen / Qualified Immigrant</label></div></div>
<button type="button" data-go class="w-full py-4 rounded-xl text-white font-bold text-lg transition-all hover:opacity-90 hover:shadow-lg" style="background:linear-gradient(135deg, #0E4D91, #1565C0)">Calculate Impact of This Raise →</button>
<div data-out class="mt-6" style="display:none" aria-live="polite"></div></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm"><h2 class="font-bold text-slate-900 mb-3">What is the Florida benefits cliff?</h2>
<p class="text-sm text-slate-600 leading-relaxed mb-3">A "benefits cliff" happens when a small raise pushes your income over a program's limit, so you lose a benefit worth more than the raise. In Florida the sharpest cliffs are the SNAP gross-income limit (200% of the poverty level), the Medicaid parent limit (about 26% FPL) and the LIHEAP limit (150% FPL). SNAP itself tapers gradually — roughly 30 cents of benefit per extra dollar of net income — so most raises still leave you ahead unless they cross a hard limit.</p>
<p class="text-sm text-slate-600 leading-relaxed">This calculator compares your estimated benefits before and after the raise using the 2026 thresholds verified {UPDATED_FULL}. Treat it as a planning aid; only DCF, SSA or the IRS can make a final determination.</p></div>
</div></main>'''
    rel=related([("Florida SNAP (food stamps) income limits","/programs/snap/"),("Florida Medicaid eligibility","/programs/medicaid/"),("Earned Income Tax Credit (EITC) for families","/programs/eitc/"),("The Florida SNAP income cliff explained","/blog/income-cliff-snap-florida/")])
    g=graph(path,title,desc,trail_for(path),extra=[webapp(path,"Florida Income Cliff Calculator",desc),faq_schema([
        ("Will a raise make me lose my Florida food stamps?","Usually not all at once. SNAP benefits taper by about 30 cents per extra dollar of net income. You lose SNAP entirely only when gross income passes Florida's limit of 200% of the federal poverty level ($5,500/month for a family of 4 in 2026)."),
        ("What is a benefits cliff?","A benefits cliff is when a small income increase crosses a program's eligibility limit and you lose a benefit worth more than the raise. Florida's biggest cliffs are the Medicaid parent limit and the SNAP gross-income limit.")])])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel,extra_body_js=JS_TAG))

def build_docs():
    path="/tools/document-checklist/"; title,desc,kw=SEO[path]
    progs=[("snap","🛒 SNAP (Food Stamps)"),("medicaid","🏥 Florida Medicaid"),("ssi","♿ SSI Benefits"),("liheap","⚡ LIHEAP Energy Assistance"),("wic","🥛 WIC Nutrition"),("kidcare","👶 Florida KidCare")]
    boxes="".join(f'<label class="flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all hover:bg-green-50" style="border-color:#E2E8F0"><input type="checkbox" data-prog="{s}" class="w-5 h-5 accent-green-600"><span class="text-sm font-medium text-slate-700">{l}</span></label>' for s,l in progs)
    main=f'''<main id="main-content" class="min-h-screen py-10 px-4 bg-slate-50"><div class="max-w-3xl mx-auto">
{TOOL_HERO("Florida-Only Tool","#DCFCE7","#166534","Document Checklist Generator","Tell us which programs you're applying for and we'll generate a personalized list of documents to bring.")}
<div class="bg-white rounded-2xl shadow-xl border border-slate-100 p-6 sm:p-8" data-fbc-docs="1">
<h2 class="font-bold text-slate-900 text-lg mb-4">Which programs are you applying for?</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">{boxes}</div>
<button type="button" data-go disabled class="w-full py-4 rounded-xl text-white font-bold text-lg transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed" style="background:linear-gradient(135deg, #16A34A, #15803D)">Generate My Document Checklist</button>
<div data-out class="mt-6" style="display:none" aria-live="polite"></div></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm"><h2 class="font-bold text-slate-900 mb-3">What documents do you need to apply for Florida benefits?</h2>
<p class="text-sm text-slate-600 leading-relaxed mb-3">Every Florida application through MyACCESS asks for the same core proof: photo ID, Social Security numbers, proof of Florida residence, proof of all income for the last 4 weeks, and proof of citizenship or qualified immigration status. SNAP additionally rewards you for proving rent, utilities, child-care and medical costs, because those deductions raise your benefit. SSI requires medical and financial records; LIHEAP needs your current energy bill.</p>
<p class="text-sm text-slate-600 leading-relaxed">You can upload documents in your MyACCESS account, fax them, or bring copies to a DCF service center — see the <a href="/tools/county-finder/" class="text-blue-700 underline">County Resource Finder</a> for your local office.</p></div>
</div></main>'''
    rel=related([("Florida SNAP (food stamps) income limits","/programs/snap/"),("Florida Medicaid eligibility","/programs/medicaid/"),("SSI in Florida: eligibility and payments","/programs/ssi/"),("How to apply for SNAP in Florida, step by step","/blog/how-to-apply-snap-florida-2026/")])
    g=graph(path,title,desc,trail_for(path),extra=[webapp(path,"Florida Benefits Document Checklist Generator",desc),faq_schema([
        ("What documents do I need to apply for food stamps in Florida?","Photo ID, Social Security numbers for everyone applying, proof of Florida residence, proof of all income for the last 4 weeks, proof of citizenship or immigration status, plus rent/utility bills and child-care or medical expenses to maximize your deductions."),
        ("How do I submit documents to Florida DCF?","Upload them in your MyACCESS account, fax them to DCF, or bring copies to your local DCF service center. Keep your case number on every page.")])])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel,extra_body_js=JS_TAG))

def build_tools_index():
    path="/tools/"; title,desc,kw=SEO[path]
    cards=[("🛒","SNAP Benefit Calculator","How much food stamps will I get? FY2027 rules, with rent & bills.","/tools/snap-calculator/","#DCFCE7","#166534"),
           ("📈","Income Cliff Calculator","If I get a $200 raise, will I lose more in benefits than I gain?","/tools/income-cliff/","#DBEAFE","#1D4ED8"),
           ("🕳️","Coverage Gap Tool","Are you trapped between Medicaid and ACA subsidies? 800K Floridians are.","/tools/coverage-gap/","#FEE2E2","#B91C1C"),
           ("📋","Document Checklist","Auto-generate your personalized application document list.","/tools/document-checklist/","#DCFCE7","#166534"),
           ("📍","County Resource Finder","Find DCF offices and food banks in all 67 Florida counties.","/tools/county-finder/","#FEF3C7","#92400E")]
    grid="".join(f'''<a href="{u}" class="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover-lift block"><span class="inline-block text-xs font-bold px-3 py-1 rounded-full mb-3 uppercase tracking-wider" style="background:{bg};color:{fg}">Florida-Only Tool</span><div class="text-3xl mb-2" aria-hidden="true">{ic}</div><h2 class="font-bold text-slate-900 text-lg mb-1">{t}</h2><p class="text-sm text-slate-600 leading-relaxed mb-3">{d}</p><span class="text-sm font-semibold" style="color:#0E4D91">Use Tool →</span></a>''' for ic,t,d,u,bg,fg in cards)
    main=f'''<main id="main-content" class="min-h-screen py-10 px-4 bg-slate-50"><div class="max-w-4xl mx-auto">
{TOOL_HERO("Exclusive Tools","#DBEAFE","#1D4ED8","Free Florida Benefits Tools","Original calculators and finders built specifically for Florida residents — no signup, no data stored, updated for 2026.")}
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">{grid}</div>
<div class="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm text-center"><h2 class="font-bold text-slate-900 text-xl mb-2">Not sure where to start?</h2><p class="text-sm text-slate-600 mb-4">Run the 60-second eligibility checker first — it screens all 9 Florida programs at once.</p><a href="/checker/" class="inline-block text-white font-semibold px-6 py-3 rounded-xl" style="background:linear-gradient(135deg, #F97316, #EF4444)">Check My Eligibility Now →</a></div>
</div></main>'''
    g=graph(path,title,desc,trail_for(path),webtype="CollectionPage")
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g))

def legal(path,h1,body,updated=UPDATED_FULL):
    title,desc,kw=SEO[path]
    main=f'''<main id="main-content" class="max-w-3xl mx-auto px-4 py-12"><h1 class="text-3xl font-bold text-slate-900 mb-6">{h1}</h1><p class="text-sm text-slate-500 mb-8">Last updated: {updated}</p><div class="space-y-6 text-slate-600 text-sm leading-relaxed">{body}</div></main>'''
    g=graph(path,title,desc,trail_for(path))
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,robots="noindex, follow" if path in ("/privacy/","/disclaimer/") else "index, follow"))

def sec(h2,p): return f'<section><h2 class="text-lg font-bold text-slate-900 mb-2">{h2}</h2>{p}</section>'

def build_legal():
    SEO["/privacy/"]=("Privacy Policy — FloridaBenefitCheck.com","How FloridaBenefitCheck.com handles your data: the eligibility checker runs entirely in your browser and we never collect or store what you enter.","privacy policy floridabenefitcheck")
    SEO["/disclaimer/"]=("Disclaimer — FloridaBenefitCheck.com","FloridaBenefitCheck.com provides eligibility estimates for informational purposes only and is not affiliated with any government agency.","disclaimer floridabenefitcheck")
    SEO["/accessibility/"]=("Accessibility Statement — FloridaBenefitCheck.com","Our commitment to making Florida benefits information accessible to everyone, including keyboard navigation, screen-reader support, large text and three languages.","accessibility statement floridabenefitcheck")
    legal("/privacy/","Privacy Policy",
      sec("Information We Collect","<p>FloridaBenefitCheck.com does NOT collect, transmit, or store any personal information entered into our eligibility checker or calculators. All calculations are performed locally in your browser. We never see your household size, income, or any other information you enter.</p>")+
      sec("Analytics","<p>We may use privacy-respecting analytics (such as Google Analytics 4) to collect anonymous usage data — page views, traffic sources and device type. This data contains no personally identifiable information and is used only to improve the site.</p>")+
      sec("Advertising","<p>Pages may display advertising served by Google AdSense. Google and its partners may use cookies to serve ads based on prior visits to this or other websites. You can opt out of personalized advertising at <a href=\"https://www.google.com/settings/ads\" class=\"text-blue-600 underline\" rel=\"noopener noreferrer\" target=\"_blank\">Google Ads Settings</a>.</p>")+
      sec("Newsletter","<p>If you voluntarily sign up for our newsletter, we collect only your email address, used solely to send benefit update notifications. We never sell or share email addresses. You can unsubscribe at any time.</p>")+
      sec("Cookies","<p>We use minimal cookies for analytics and advertising only. We do not use cookies to track personal information entered into our tools.</p>")+
      sec("Contact","<p>Questions about this privacy policy? Contact us at privacy@floridabenefitcheck.com.</p>"))
    legal("/disclaimer/","Disclaimer",
      '<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5"><p class="font-semibold text-amber-900">FloridaBenefitCheck.com provides eligibility estimates for informational purposes only. We are not affiliated with, endorsed by, or connected to any government agency, including the Florida Department of Children and Families, the Social Security Administration, or the USDA Food and Nutrition Service.</p></div>'+
      f'<p>Eligibility results provided by this tool are estimates based on publicly available 2026 income thresholds and program rules, last verified on {UPDATED_FULL}. Actual eligibility is determined solely by the relevant government agency upon review of a completed application.</p>'+
      '<p>Program rules, income limits, and benefit amounts are subject to change. While we strive to keep our data current, we make no guarantee that all information is up to date at the time of your visit.</p>'+
      '<p>Do not rely solely on this tool to make decisions about your benefits. Always apply directly through official government channels and consult with a qualified benefits counselor for advice specific to your situation.</p>'+
      '<p>Official application portals: <a href="https://www.myflorida.com/accessflorida/" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline">ACCESS Florida</a> | <a href="https://www.ssa.gov/" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline">SSA.gov</a></p>')
    legal("/accessibility/","Accessibility Statement",
      sec("Our commitment","<p>FloridaBenefitCheck.com is built so that every Floridian — including people using screen readers, keyboard-only navigation, magnification or mobile devices — can check their benefit eligibility. We aim to conform to the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA.</p>")+
      sec("What we do","<ul class=\"list-disc pl-5 space-y-1\"><li>A \"Skip to main content\" link on every page and a logical heading structure.</li><li>All interactive controls work with a keyboard and announce their state to assistive technology (<code>aria-pressed</code>, <code>aria-expanded</code>, live regions for results).</li><li>Color is never the only way information is conveyed; text contrast meets AA ratios.</li><li>Animations respect the <em>prefers-reduced-motion</em> setting.</li><li>Content is available in English, Spanish and Haitian Creole.</li><li>Print-friendly checklists and no time limits on any form.</li></ul>")+
      sec("Known limitations","<p>The eligibility checker and calculators require JavaScript. If JavaScript is unavailable, every program page still lists the 2026 income limits in plain text.</p>")+
      sec("Feedback","<p>If you encounter an accessibility barrier, email accessibility@floridabenefitcheck.com and we will respond within 5 business days. For help applying in person, call Florida 2-1-1 or visit your <a href=\"/tools/county-finder/\" class=\"text-blue-600 underline\">local DCF office</a>.</p>"))

if __name__=="__main__":
    build_home(); build_checker(); build_cliff(); build_docs(); build_tools_index(); build_legal()
    print("authored pages written")

# ======================================================================
# Rewritten from verified data (were stale on the live site)
# ======================================================================
FPL_BASE, FPL_ADD = 15960, 5680
SNAP_MAX = {1:306,2:562,3:808,4:1023,5:1217,6:1463,7:1616,8:1841}
def fpl_m(n): return round((FPL_BASE+FPL_ADD*max(n-1,0))/12)
def money(x): return "${:,.0f}".format(x)
SNAP_GROSS = {1:2660,2:3607,3:4554,4:5500,5:6447,6:7394,7:8340,8:9287}
SNAP_NET   = {1:1330,2:1804,3:2277,4:2750,5:3224,6:3697,7:4170,8:4644}

def build_snap_limits():
    path="/blog/florida-snap-income-limits-2026/"; title,desc,kw=SEO[path]
    rows="".join(f'<tr class="{"bg-white" if n%2 else "bg-slate-50"}"><td class="px-4 py-3 font-semibold">{n} {"person" if n==1 else "people"}</td><td class="px-4 py-3 text-right">{money(SNAP_GROSS[n])}</td><td class="px-4 py-3 text-right">{money(SNAP_NET[n])}</td><td class="px-4 py-3 text-right font-bold" style="color:#16A34A">{money(SNAP_MAX[n])}</td></tr>' for n in range(1,9))
    qa=[
     ("What is the SNAP gross income limit in Florida for 2026?",f"Florida uses broad-based categorical eligibility, so most households qualify with gross income at or below 200% of the federal poverty level: {money(SNAP_GROSS[1])}/month for 1 person, {money(SNAP_GROSS[3])} for 3 and {money(SNAP_GROSS[4])} for a family of 4. The federal 130% limit does not apply to most Florida households."),
     ("What is the net income limit?",f"After deductions for housing, utilities, child care and medical costs (for members 60+ or disabled), net income must be at or below 100% of the poverty level — {money(SNAP_NET[4])}/month for a family of 4 in 2026."),
     ("What is the maximum SNAP benefit in Florida?",f"From October 1, 2026 (federal fiscal year 2027) the maximum monthly allotment is {money(SNAP_MAX[1])} for 1 person, {money(SNAP_MAX[2])} for 2, {money(SNAP_MAX[3])} for 3 and {money(SNAP_MAX[4])} for 4. Most households receive less, because 30% of net income is subtracted."),
     ("Who only has to meet the net income test?","Households with a member aged 60 or older or a member with a disability only need to meet the 100% net income limit, not the gross limit. Households where everyone receives SSI or TANF are categorically eligible."),
     ("When do Florida SNAP numbers change?","Two dates each year: maximum allotments and deductions change every October 1 with the USDA cost-of-living adjustment, and income limits follow the HHS poverty guidelines published each January (the 2026 guidelines were released January 15, 2026)."),
    ]
    faq_html="".join(f'<div class="mb-6"><h3 class="font-bold text-slate-900 mb-2">{q}</h3><p class="text-slate-700">{a}</p></div>' for q,a in qa)
    main=f'''<main id="main-content"><article class="max-w-3xl mx-auto px-4 py-12">
<nav class="text-sm text-slate-500 mb-6" aria-label="Breadcrumb"><a href="/" class="hover:text-blue-700">Home</a> / <a href="/blog/" class="hover:text-blue-700">Blog</a> / <span>SNAP Income Limits 2026</span></nav>
<div class="flex items-center gap-2 mb-4"><span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#DCFCE7;color:#166534">SNAP</span><span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#DBEAFE;color:#1D4ED8">✅ Verified {UPDATED_FULL}</span></div>
<h1 class="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-4">Florida SNAP Income Limits 2026 — Complete Table by Household Size</h1>
<p class="text-xl text-slate-600 mb-6">Florida food stamp (SNAP) eligibility uses a gross income limit of <strong>200% of the 2026 federal poverty level</strong> — {money(SNAP_GROSS[4])} a month for a family of four — and a net limit of 100%. Maximum benefits rose on October 1, 2026 to {money(SNAP_MAX[4])} a month for four people.</p>
<p class="text-sm text-slate-500 mb-8">📅 Last verified {UPDATED_FULL} • Sources: USDA FNS, HHS 2026 Poverty Guidelines, Florida DCF • ⏱️ 5 min read</p>
<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-8"><p class="text-sm text-amber-900"><strong>Quick answer:</strong> A Florida household can generally get SNAP if its gross monthly income is at or below {money(SNAP_GROSS[1])} (1 person), {money(SNAP_GROSS[2])} (2), {money(SNAP_GROSS[3])} (3) or {money(SNAP_GROSS[4])} (4), and net income after deductions is at or below 100% of the poverty level.</p></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">2026 SNAP Income Limits Table (Florida)</h2>
<div class="overflow-x-auto rounded-2xl border border-slate-100 shadow-sm mb-3"><table class="w-full text-sm"><caption class="sr-only">Florida SNAP gross and net monthly income limits and maximum benefit by household size, effective October 1, 2026</caption>
<thead><tr style="background:#16A34A;color:#fff"><th scope="col" class="px-4 py-3 text-left">Household Size</th><th scope="col" class="px-4 py-3 text-right">Gross Monthly (200% FPL)</th><th scope="col" class="px-4 py-3 text-right">Net Monthly (100% FPL)</th><th scope="col" class="px-4 py-3 text-right">Max Benefit (FY2027)</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="text-sm text-slate-600 mb-10">Each additional person adds about {money(round(2*FPL_ADD/12))}/month to the gross limit and {money(round(FPL_ADD/12))} to the net limit. Gross and net limits are based on the 2026 HHS poverty guidelines ({money(FPL_BASE)}/year for one person + {money(FPL_ADD)} per additional person); maximum benefits are the USDA FY2027 allotments for the 48 states and DC.</p>
<h2 class="text-2xl font-bold text-slate-900 mt-10 mb-4">How your SNAP amount is calculated</h2>
<p class="text-slate-700 mb-3">SNAP expects households to spend about 30% of their net income on food. Your benefit is the maximum allotment for your household size <em>minus 30% of your net income</em>. Example: a family of 4 with {money(1500)} net monthly income would receive about {money(SNAP_MAX[4]-450)} ({money(SNAP_MAX[4])} − {money(450)}).</p>
<p class="text-slate-700 mb-3">Net income is gross income minus a 20% earned-income deduction, the standard deduction, dependent-care costs, medical costs over $35 for members 60+ or disabled, child support paid, and an excess-shelter deduction when rent and utilities exceed half of your remaining income. That is why documenting rent and utility bills can noticeably raise your benefit.</p>
<h2 class="text-2xl font-bold text-slate-900 mt-10 mb-4">Key Facts About Florida SNAP 2026</h2>
{faq_html}
<div class="rounded-2xl p-6 text-white text-center mt-10" style="background:linear-gradient(135deg, #16A34A, #15803D)"><h2 class="text-2xl font-bold mb-2">Not Sure If You Qualify?</h2><p class="mb-4">Our free checker uses these exact 2026 thresholds and also screens Medicaid, WIC, LIHEAP and 5 more programs.</p><a href="/checker/" class="inline-block bg-white font-bold px-6 py-3 rounded-xl" style="color:#15803D">Check My SNAP Eligibility — Free</a></div>
<p class="text-xs text-slate-500 mt-8">Sources: <a class="underline" href="https://www.fns.usda.gov/snap/allotment/cola" rel="noopener" target="_blank">USDA FNS — SNAP COLA FY2027</a> • <a class="underline" href="https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines" rel="noopener" target="_blank">HHS ASPE — 2026 Poverty Guidelines</a> • <a class="underline" href="https://www.myflfamilies.com/services/public-assistance" rel="noopener" target="_blank">Florida DCF — Public Assistance</a></p>
</article></main>'''
    dataset={"@type":"Dataset","name":"Florida SNAP income limits and maximum benefits 2026 (FY2027)","description":"Gross (200% FPL) and net (100% FPL) monthly income limits and maximum SNAP allotments by household size for Florida, effective October 1, 2026.",
             "url":BASE+path,"creator":{"@id":BASE+"/#org"},"license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True,"temporalCoverage":"2026-10-01/2027-09-30","spatialCoverage":{"@type":"State","name":"Florida"},
             "isBasedOn":["https://www.fns.usda.gov/snap/allotment/cola","https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines"],"dateModified":UPDATED_ISO}
    art={"@type":"Article","@id":BASE+path+"#article","headline":title,"description":desc,"datePublished":"2026-01-20","dateModified":UPDATED_ISO,
         "author":{"@type":"Organization","name":"FloridaBenefitCheck.com","url":BASE+"/"},"publisher":{"@id":BASE+"/#org"},"mainEntityOfPage":{"@id":BASE+path+"#webpage"},"image":BASE+"/og-image.png","inLanguage":"en-US"}
    g=graph(path,title,desc,trail_for(path),extra=[art,faq_schema(qa),dataset])
    rel=related([("Florida SNAP eligibility & how to apply","/programs/snap/"),("How to apply for SNAP in Florida, step by step","/blog/how-to-apply-snap-florida-2026/"),("Income Cliff Calculator","/tools/income-cliff/"),("Florida EBT restrictions 2026","/blog/florida-snap-restrictions-ebt-2026/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

def build_coverage_gap():
    path="/tools/coverage-gap/"; title,desc,kw=SEO[path]
    cards=""
    for n in range(1,9):
        med=round(0.26*fpl_m(n)); aca=fpl_m(n)
        cards+=f'''<div class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"><h3 class="font-bold text-slate-900 mb-3">Household of {n}</h3>
<div class="space-y-2 text-sm"><div class="flex justify-between gap-2 p-2 rounded-lg" style="background:#DCFCE7"><span class="text-slate-700">Medicaid (parents)</span><strong style="color:#166534">Under {money(med)}/mo</strong></div>
<div class="flex justify-between gap-2 p-2 rounded-lg" style="background:#FEE2E2"><span class="text-slate-700 font-semibold">COVERAGE GAP</span><strong style="color:#B91C1C">{money(med)}–{money(aca)}/mo</strong></div>
<div class="flex justify-between gap-2 p-2 rounded-lg" style="background:#DBEAFE"><span class="text-slate-700">ACA subsidies</span><strong style="color:#1D4ED8">{money(aca)}+/mo</strong></div></div></div>'''
    opts=[("🏥","Federally Qualified Health Centers (FQHCs)","Sliding-scale free or low-cost primary care based on your income. Florida has 50+ FQHC organizations with hundreds of sites — find one at findahealthcenter.hrsa.gov."),
          ("💊","Prescription Assistance Programs","Most drug manufacturers offer free medications to uninsured low-income patients; NeedyMeds and RxAssist list them."),
          ("🦷","Florida Dental Association Foundation","Free dental clinics (Florida Mission of Mercy) throughout Florida for uninsured patients."),
          ("📈","Earn just enough for Marketplace help",f"If your income reaches 100% of the poverty level ({money(fpl_m(1))}/mo for one person), you can buy an ACA Marketplace plan with premium tax credits — often $0–$50/month."),
          ("📋","Florida Medicaid expansion","Florida has not expanded Medicaid. Follow the status of the proposed ballot measure in our expansion tracker.")]
    ohtml="".join(f'<div class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm flex gap-3"><span class="text-2xl" aria-hidden="true">{i}</span><div><h3 class="font-bold text-slate-900 mb-1">{t}</h3><p class="text-sm text-slate-600 leading-relaxed">{d}</p></div></div>' for i,t,d in opts)
    main=f'''<main id="main-content" class="min-h-screen py-10 px-4 bg-slate-50"><div class="max-w-4xl mx-auto">
{TOOL_HERO("Florida-Only Tool","#FEE2E2","#B91C1C","Florida Coverage Gap Tool 2026","About 800,000 Floridians are in the coverage gap — earning too much for Medicaid but too little for ACA Marketplace subsidies. Check where you fall and discover your options.")}
<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-8"><p class="text-sm text-amber-900"><strong>Quick answer:</strong> In Florida, a parent in a family of 4 loses Medicaid above about {money(round(0.26*fpl_m(4)))}/month, but Marketplace premium tax credits only start at {money(fpl_m(4))}/month (100% of the poverty level). Adults without children cannot get Medicaid on income alone at any level, so anyone below 100% FPL without children is in the gap.</p></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">Florida Coverage Gap Thresholds (2026)</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-3">{cards}</div>
<p class="text-xs text-slate-500 mb-10">Thresholds use the 2026 HHS poverty guidelines ({money(FPL_BASE)} + {money(FPL_ADD)} per person). Medicaid column = Florida's parent/caretaker limit (≈26% FPL); childless adults have no income-based Medicaid category. ACA column = 100% FPL, the floor for premium tax credits on 2027 Marketplace plans (open enrollment starts November 1, 2026). Verified {UPDATED_FULL}.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">If You Are in the Coverage Gap — Your Options</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">{ohtml}</div>
<div class="text-center"><a href="/checker/" class="inline-block text-white font-semibold px-6 py-3 rounded-xl" style="background:linear-gradient(135deg, #F97316, #EF4444)">Check All Your Benefit Options →</a></div>
</div></main>'''
    qa=[("What is the Medicaid coverage gap in Florida?","Because Florida has not expanded Medicaid, adults without children cannot qualify on income alone and parents qualify only up to about 26% of the poverty level. ACA Marketplace subsidies start at 100% of the poverty level, so adults earning between those points get neither."),
        ("How many Floridians are in the coverage gap?","Roughly 800,000 Florida adults fall into the gap, one of the largest totals of any state.")]
    g=graph(path,title,desc,trail_for(path),extra=[webapp(path,"Florida Medicaid Coverage Gap Tool",desc),faq_schema(qa)])
    rel=related([("Florida Medicaid eligibility","/programs/medicaid/"),("Florida Medicaid expansion 2026 tracker","/blog/florida-medicaid-expansion-2026/"),("Florida KidCare for children","/programs/kidcare/"),("Florida Medicaid eligibility 2026 guide","/blog/florida-medicaid-eligibility-2026/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

def build_ssi():
    path="/programs/ssi/"; title,desc,kw=SEO[path]
    FBR,CPL=994,1491
    def row(a,b,c,bg): return f'<tr class="{bg}"><td class="px-4 py-3">{a}</td><td class="px-4 py-3 text-right font-semibold">{b}</td><td class="px-4 py-3 text-right font-semibold">{c}</td></tr>'
    inc=(row("Federal Benefit Rate (max monthly SSI)",money(FBR),money(CPL),"bg-white")+
         row("General income exclusion (any income)","$20","$20","bg-slate-50")+
         row("Earned income exclusion","$65 + ½ of the rest","$65 + ½ of the rest","bg-white")+
         row("Income limit — only unearned income (e.g. SSDI)",money(FBR+20),money(CPL+20),"bg-slate-50")+
         row("Income limit — only earned income (wages)",money(2*FBR+85),money(2*CPL+85),"bg-white")+
         row("Resource (asset) limit","$2,000","$3,000","bg-slate-50"))
    qa=[("How much is SSI in Florida in 2026?",f"The 2026 federal SSI payment is up to {money(FBR)} a month for an individual and {money(CPL)} for an eligible couple, after a 2.8% cost-of-living increase. Florida adds no state supplement for people living on their own; a supplement (Optional State Supplementation) is only paid to residents of assisted living facilities, adult family care homes and certain residential settings."),
        ("What is the SSI income limit in 2026?",f"It depends on the type of income. With only unearned income (such as SSDI) you can have up to about {money(FBR+20)} a month; with only wages, up to about {money(2*FBR+85)} because Social Security excludes $65 plus half of the rest of your earnings."),
        ("What is the SSI asset limit?","Countable resources must be $2,000 or less for an individual and $3,000 for a couple. Your home, one car, household goods, burial plots and up to $1,500 in burial funds are not counted."),
        ("Does SSI automatically qualify me for Medicaid in Florida?","Yes. In Florida, SSI recipients are automatically eligible for Medicaid — you do not need a separate application."),
        ("Can I get SSI and SSDI at the same time?","Yes, if your SSDI payment is low. Your SSI is reduced dollar-for-dollar by SSDI after the $20 general exclusion — these are called concurrent benefits."),
        ("Can I work while receiving SSI?","Yes. The first $65 a month plus half of remaining earnings are excluded, and work incentives such as PASS plans, Impairment-Related Work Expenses and Blind Work Expenses let you keep more."),
        ("How long does SSI approval take in Florida?","Initial decisions typically take 3–6 months; disability-based claims often take 6–12 months or longer. If denied, you have 60 days to appeal.")]
    faq="".join(f'<div class="mb-6"><h3 class="font-bold text-slate-900 mb-2">{q}</h3><p class="text-slate-700 text-sm leading-relaxed">{a}</p></div>' for q,a in qa)
    who=[("Age 65 or Older","You are 65 or older, regardless of disability status."),("Legally Blind","Vision of 20/200 or worse in the better eye with correction, or a visual field of 20 degrees or less."),("Disabled","A physical or mental impairment that prevents substantial work for 12+ months or is expected to result in death.")]
    whohtml="".join(f'<div class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"><h3 class="font-bold text-slate-900 mb-1">{t}</h3><p class="text-sm text-slate-600">{d}</p></div>' for t,d in who)
    main=f'''<main id="main-content">
<section class="py-14 px-4 text-white" style="background:linear-gradient(135deg, #7C3AED, #5B21B6)"><div class="max-w-4xl mx-auto">
<p class="text-xs font-bold uppercase tracking-wider mb-3" style="color:#DDD6FE">Federal + State Program • Verified {UPDATED_FULL}</p>
<h1 class="text-4xl sm:text-5xl font-bold mb-4">SSI in Florida 2026 — Payment Amounts, Income Limits &amp; Eligibility</h1>
<p class="text-lg mb-6" style="color:#EDE9FE">Supplemental Security Income pays up to <strong>{money(FBR)}/month</strong> to an eligible individual and <strong>{money(CPL)}/month</strong> to a couple in 2026 — for people who are 65+, blind or disabled with limited income and resources.</p>
<div class="flex flex-wrap gap-3"><a href="/checker/" class="inline-block bg-white font-bold px-6 py-3 rounded-xl" style="color:#5B21B6">Check My SSI Eligibility →</a><a href="https://www.ssa.gov/benefits/ssi/" target="_blank" rel="noopener noreferrer" class="inline-block font-bold px-6 py-3 rounded-xl border-2 border-white text-white">Apply at SSA.gov</a></div></div></section>
<div class="max-w-4xl mx-auto px-4 py-12">
<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-12 text-center">
<div class="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm"><div class="text-2xl font-bold" style="color:#7C3AED">{money(FBR)}</div><div class="text-xs text-slate-500">Federal SSI (individual)</div></div>
<div class="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm"><div class="text-2xl font-bold" style="color:#7C3AED">$0</div><div class="text-xs text-slate-500">FL supplement (living on your own)</div></div>
<div class="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm"><div class="text-2xl font-bold" style="color:#7C3AED">{money(FBR)}</div><div class="text-xs text-slate-500">Total (individual alone)</div></div>
<div class="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm"><div class="text-2xl font-bold" style="color:#7C3AED">{money(CPL)}</div><div class="text-xs text-slate-500">SSI (couple)</div></div></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">Who Qualifies for SSI in Florida?</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">{whohtml}</div>
<p class="text-sm text-slate-600 mb-12"><strong>Additional requirements:</strong> U.S. citizen or qualifying non-citizen, Florida resident, countable income and resources under the limits below, and you must apply for any other benefits you may be entitled to (such as Social Security).</p>
<h2 class="text-2xl font-bold text-slate-900 mb-2">2026 SSI Income Limits</h2>
<p class="text-sm text-slate-600 mb-4">Not all income counts — Social Security applies exclusions before comparing your income to the federal benefit rate.</p>
<div class="overflow-x-auto rounded-2xl border border-slate-100 shadow-sm mb-12"><table class="w-full text-sm"><caption class="sr-only">2026 SSI income and resource limits for individuals and couples</caption><thead><tr style="background:#7C3AED;color:#fff"><th scope="col" class="px-4 py-3 text-left">Rule</th><th scope="col" class="px-4 py-3 text-right">Individual</th><th scope="col" class="px-4 py-3 text-right">Couple</th></tr></thead><tbody>{inc}</tbody></table></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">Asset Rules — What Counts?</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-12">
<div class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"><h3 class="font-bold text-slate-900 mb-2">Counted (toward the $2,000 limit)</h3><ul class="list-disc pl-5 text-sm text-slate-600 space-y-1"><li>Cash, checking and savings accounts</li><li>Stocks, bonds, mutual funds</li><li>A second vehicle or extra property</li><li>Cash value of life insurance over $1,500 face value</li></ul></div>
<div class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"><h3 class="font-bold text-slate-900 mb-2">NOT counted (excluded)</h3><ul class="list-disc pl-5 text-sm text-slate-600 space-y-1"><li>The home you live in</li><li>One vehicle used for transportation</li><li>Household goods and personal items</li><li>Burial plots and up to $1,500 in burial funds</li><li>ABLE account balances up to $100,000</li></ul></div></div>
<h2 class="text-2xl font-bold text-slate-900 mb-2">Florida State Supplement (OSS)</h2>
<p class="text-sm text-slate-600 mb-4">Florida does not add money to SSI for people living independently or with family. Its Optional State Supplementation (OSS) is paid only to eligible residents of licensed assisted living facilities, adult family care homes, mental health residential treatment facilities and similar settings, and is administered by Florida DCF. The amount depends on the facility's rate and your income.</p>
<div class="overflow-x-auto rounded-2xl border border-slate-100 shadow-sm mb-12"><table class="w-full text-sm"><thead><tr style="background:#7C3AED;color:#fff"><th scope="col" class="px-4 py-3 text-left">Living situation</th><th scope="col" class="px-4 py-3 text-right">FL supplement</th><th scope="col" class="px-4 py-3 text-right">Total monthly (individual)</th></tr></thead><tbody>
<tr class="bg-white"><td class="px-4 py-3">Living alone or with others</td><td class="px-4 py-3 text-right">$0</td><td class="px-4 py-3 text-right font-semibold">up to {money(FBR)}</td></tr>
<tr class="bg-slate-50"><td class="px-4 py-3">Living in someone else's household who provides food &amp; shelter</td><td class="px-4 py-3 text-right">$0</td><td class="px-4 py-3 text-right font-semibold">up to {money(round(FBR*2/3))} (⅓ reduction)</td></tr>
<tr class="bg-white"><td class="px-4 py-3">Assisted living / adult family care home</td><td class="px-4 py-3 text-right">OSS — varies</td><td class="px-4 py-3 text-right font-semibold">Varies by facility</td></tr></tbody></table></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">How to Apply for SSI in Florida</h2>
<ol class="list-decimal pl-6 space-y-3 text-sm text-slate-700 mb-6"><li><strong>Apply online at SSA.gov</strong> — adults 18–65 applying based on disability can start online at ssa.gov/benefits/ssi.</li><li><strong>Call Social Security</strong> at 1-800-772-1213 (TTY 1-800-325-0778), Monday–Friday 8am–7pm, to request an SSI appointment.</li><li><strong>Visit a local SSA office</strong> — find yours at ssa.gov/locator; call ahead and bring your documents.</li></ol>
<p class="text-sm text-slate-600 mb-12">Not sure what to bring? Use the <a href="/tools/document-checklist/" class="text-blue-700 underline">Document Checklist Generator</a> for a personalized SSI list.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">SSI Florida FAQ</h2>{faq}
<div class="rounded-2xl p-6 text-white text-center mt-6" style="background:linear-gradient(135deg, #7C3AED, #5B21B6)"><h2 class="text-2xl font-bold mb-2">Find Out If You Qualify — Free, No Sign-Up</h2><p class="mb-4">Check SSI plus 8 other Florida benefit programs in under 2 minutes.</p><a href="/checker/" class="inline-block bg-white font-bold px-6 py-3 rounded-xl" style="color:#5B21B6">Start Free Eligibility Check →</a></div>
<p class="text-xs text-slate-500 mt-8">Sources: <a class="underline" href="https://www.ssa.gov/oact/cola/SSI.html" target="_blank" rel="noopener">SSA — SSI federal payment amounts</a> • <a class="underline" href="https://www.ssa.gov/ssi/text-resources-ussi.htm" target="_blank" rel="noopener">SSA — SSI resources</a> • <a class="underline" href="https://www.myflfamilies.com/" target="_blank" rel="noopener">Florida DCF — Optional State Supplementation</a></p>
</div></main>'''
    from content import gov_service, PROG_PROVIDER
    nm,d,pn,pu=PROG_PROVIDER["ssi"]
    g=graph(path,title,desc,trail_for(path),extra=[gov_service(path,nm,d,pn,pu),faq_schema(qa)])
    rel=related([("Florida Medicaid eligibility","/programs/medicaid/"),("Florida SNAP (food stamps) income limits","/programs/snap/"),("Document Checklist Generator","/tools/document-checklist/"),("Income Cliff Calculator","/tools/income-cliff/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

def _prog_shell(path,color1,color2,badge,h1,lead,body,qa,rel_links,cta_label):
    title,desc,kw=SEO[path]
    faq="".join(f'<div class="mb-6"><h3 class="font-bold text-slate-900 mb-2">{q}</h3><p class="text-slate-700 text-sm leading-relaxed">{a}</p></div>' for q,a in qa)
    main=f'''<main id="main-content">
<section class="py-14 px-4 text-white" style="background:linear-gradient(135deg, {color1}, {color2})"><div class="max-w-4xl mx-auto">
<p class="text-xs font-bold uppercase tracking-wider mb-3" style="color:#E0F2FE">{badge} • Verified {UPDATED_FULL}</p>
<h1 class="text-4xl sm:text-5xl font-bold mb-4">{h1}</h1><p class="text-lg mb-6" style="color:#F0F9FF">{lead}</p>
<a href="/checker/" class="inline-block bg-white font-bold px-6 py-3 rounded-xl" style="color:{color2}">{cta_label}</a></div></section>
<div class="max-w-4xl mx-auto px-4 py-12">{body}
<h2 class="text-2xl font-bold text-slate-900 mb-4 mt-12">Frequently Asked Questions</h2>{faq}
</div></main>'''
    return title,desc,kw,main

def _tbl(headers,rows,cap,color):
    th="".join(f'<th scope="col" class="px-4 py-3 {"text-left" if i==0 else "text-right"}">{h}</th>' for i,h in enumerate(headers))
    tr="".join(f'<tr class="{"bg-white" if k%2==0 else "bg-slate-50"}">'+"".join(f'<td class="px-4 py-3 {"font-semibold" if i==0 else "text-right"}">{c}</td>' for i,c in enumerate(r))+'</tr>' for k,r in enumerate(rows))
    return f'<div class="overflow-x-auto rounded-2xl border border-slate-100 shadow-sm mb-3"><table class="w-full text-sm"><caption class="sr-only">{cap}</caption><thead><tr style="background:{color};color:#fff">{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def build_medicaid():
    path="/programs/medicaid/"
    P=lambda pct,n: money(round(pct/100*fpl_m(n)))
    cats=[("👶","Children under 1","211% FPL",P(211,3)),("🧒","Children ages 1–5","145% FPL",P(145,3)),("🧑","Children ages 6–18","138% FPL",P(138,3)),
          ("🛡️","Children via KidCare (CHIP)","215% FPL",P(215,3)),("🤰","Pregnant women","196% FPL",P(196,3)),
          ("👴","Aged 65+, blind or disabled (MEDS-AD)","88% FPL (individual)",money(round(0.88*fpl_m(1)))+" for 1 person"),
          ("👨‍👩‍👧","Parents & caretaker relatives","26% FPL",P(26,3)),("🚫","Adults without children","Not eligible on income","—")]
    rows=[[f"{i} {n}",lim,d] for i,n,lim,d in cats]
    body=f'''<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-10"><p class="text-sm text-amber-900"><strong>Quick answer:</strong> Florida Medicaid covers children (up to 138–211% of the poverty level depending on age, and up to 215% through KidCare), pregnant women up to 196%, aged/blind/disabled adults up to 88%, and parents only up to 26% — about {P(26,3)}/month for a family of 3. Adults without children cannot qualify on income alone because Florida has not expanded Medicaid.</p></div>
<h2 class="text-2xl font-bold text-slate-900 mb-2">2026 Florida Medicaid Income Limits</h2>
<p class="text-sm text-slate-600 mb-4">Monthly amounts are for a household of 3 unless noted, using the 2026 federal poverty level ({money(FPL_BASE+2*FPL_ADD)}/year for 3). Limits include the standard 5-point MAGI disregard.</p>
{_tbl(["Who","Income limit","Monthly (household of 3)"],rows,"Florida Medicaid income limits by eligibility group, 2026","#2563EB")}
<p class="text-xs text-slate-500 mb-10">Source: KFF state Medicaid eligibility tables (as of January 2026); HHS 2026 Poverty Guidelines; Florida DCF. MEDS-AD also has an asset limit of $5,000 (individual) / $6,000 (couple).</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">The Florida Coverage Gap: about 800,000 people</h2>
<p class="text-slate-700 text-sm leading-relaxed mb-3">Florida is one of the states that has not expanded Medicaid under the Affordable Care Act. Parents lose Medicaid above 26% of the poverty level, and adults without children are not eligible at any income unless they are pregnant, 65+, blind or disabled. ACA Marketplace premium tax credits only begin at 100% of the poverty level ({money(fpl_m(1))}/month for one person), so adults in between get neither.</p>
<p class="text-sm mb-10"><a href="/tools/coverage-gap/" class="text-blue-700 underline font-semibold">See the 2026 coverage-gap thresholds for your household size →</a></p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">How to Apply for Florida Medicaid</h2>
<ol class="list-decimal pl-6 space-y-3 text-sm text-slate-700 mb-6"><li><strong>Apply online</strong> through MyACCESS Florida (myflorida.com/accessflorida) — you can apply for Medicaid, SNAP and TANF at the same time.</li><li><strong>Children only?</strong> Apply through Florida KidCare at floridakidcare.org; the application screens for Medicaid automatically.</li><li><strong>Gather documents</strong> — ID, Social Security numbers, 4 weeks of income proof, and proof of pregnancy or disability if relevant (<a href="/tools/document-checklist/" class="text-blue-700 underline">get your checklist</a>).</li><li><strong>Wait for a decision</strong> — usually within 45 days (90 days for disability-based applications). Coverage can be retroactive up to 3 months for unpaid medical bills.</li></ol>
<p class="text-xs text-slate-500">Sources: <a class="underline" href="https://www.kff.org/affordable-care-act/state-indicator/medicaid-income-eligibility-limits-for-parents/" target="_blank" rel="noopener">KFF — Medicaid limits for parents</a> • <a class="underline" href="https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-children-as-a-percent-of-the-federal-poverty-level/" target="_blank" rel="noopener">KFF — children</a> • <a class="underline" href="https://ahca.myflorida.com/medicaid" target="_blank" rel="noopener">Florida AHCA — Medicaid</a></p>'''
    qa=[("What is the income limit for Medicaid in Florida in 2026?",f"It depends on who you are: children up to 138–211% of the poverty level by age (215% via KidCare), pregnant women up to 196%, aged/blind/disabled adults up to 88% ({money(round(0.88*fpl_m(1)))}/month for one person), and parents up to 26% ({P(26,3)}/month for a family of 3). Childless adults do not qualify on income."),
        ("Can a single adult with no children get Medicaid in Florida?","Generally no. Florida has not expanded Medicaid, so non-disabled adults under 65 without children, who are not pregnant, are not eligible at any income level."),
        ("Does SSI automatically give me Medicaid in Florida?","Yes. Florida SSI recipients are automatically eligible for Medicaid."),
        ("How long does a Florida Medicaid application take?","Most decisions are made within 45 days; disability-based applications can take up to 90 days. Medicaid can cover unpaid bills from up to 3 months before you applied.")]
    title,desc,kw,main=_prog_shell(path,"#2563EB","#1E40AF","Health Coverage","Florida Medicaid Eligibility &amp; Income Limits 2026",
        "Free or low-cost health coverage for Florida children, pregnant women, parents, seniors and people with disabilities — with the exact 2026 income limits for each group.",body,qa,None,"Check My Medicaid Eligibility →")
    from content import gov_service, PROG_PROVIDER
    nm,d,pn,pu=PROG_PROVIDER["medicaid"]
    g=graph(path,title,desc,trail_for(path),extra=[gov_service(path,nm,d,pn,pu),faq_schema(qa)])
    rel=related([("Florida Coverage Gap Tool","/tools/coverage-gap/"),("Florida KidCare for children","/programs/kidcare/"),("Florida Medicaid expansion 2026","/blog/florida-medicaid-expansion-2026/"),("Florida Medicaid eligibility guide","/blog/florida-medicaid-eligibility-2026/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

def build_kidcare():
    path="/programs/kidcare/"
    rows=[[f"{n} people",money(round(1.38*fpl_m(n))),money(round(2.15*fpl_m(n)))] for n in range(2,9)]
    progs=[("Medicaid for children","Birth–18","Up to 211% (under 1), 145% (1–5), 138% (6–18)","Free"),
           ("MediKids","Ages 1–4","Above Medicaid, up to 215% FPL","$15–$20/month per family"),
           ("Florida Healthy Kids","Ages 5–18","Above Medicaid, up to 215% FPL","$15–$20/month per family"),
           ("Children's Medical Services (CMS)","Birth–20","Same income rules, for children with special health care needs","Free–$20/month")]
    ph="".join(f'<div class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm"><h3 class="font-bold text-slate-900 mb-2">{a}</h3><p class="text-sm text-slate-600"><strong>Ages:</strong> {b}<br><strong>Income:</strong> {c}<br><strong>Cost:</strong> {d}</p></div>' for a,b,c,d in progs)
    body=f'''<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-10"><p class="text-sm text-amber-900"><strong>Quick answer:</strong> Florida KidCare covers uninsured children from birth through age 18. Families earning up to 215% of the poverty level — {money(round(2.15*fpl_m(4)))}/month for a family of 4 in 2026 — pay $0–$20 a month per family; above that, children can still enroll at the full (unsubsidized) premium.</p></div>
<h2 class="text-2xl font-bold text-slate-900 mb-2">2026 KidCare Income Limits (monthly gross)</h2>
{_tbl(["Family size","Free Medicaid (ages 6–18, 138% FPL)","Subsidized KidCare (215% FPL)"],rows,"Florida KidCare monthly income limits by family size, 2026","#0891B2")}
<p class="text-xs text-slate-500 mb-10">Based on the 2026 HHS poverty guidelines and KFF Medicaid/CHIP limits for Florida (January 2026). Younger children qualify for free Medicaid at higher incomes (145% ages 1–5, 211% under age 1).</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">The 4 KidCare Programs</h2><div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">{ph}</div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">What's Covered</h2>
<ul class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-slate-700 mb-10">{"".join(f"<li>✓ {x}</li>" for x in ["Doctor visits & checkups","Hospital stays & surgery","Emergency room","Prescription drugs","Dental care","Vision exams & glasses","Mental health & counseling","Immunizations","Lab tests & x-rays","Therapies for special needs"])}</ul>
<h2 class="text-2xl font-bold text-slate-900 mb-4">How to Apply</h2>
<p class="text-sm text-slate-700 mb-6">Apply online at <a href="https://www.floridakidcare.org/" class="text-blue-700 underline" target="_blank" rel="noopener noreferrer">floridakidcare.org</a> or call 1-888-540-5437. One application screens your children for every KidCare program, including free Medicaid. You'll need each child's Social Security number, proof of income and proof of citizenship or immigration status.</p>'''
    qa=[("What is the income limit for Florida KidCare in 2026?",f"Subsidized KidCare covers children in families earning up to 215% of the federal poverty level — {money(round(2.15*fpl_m(3)))}/month for a family of 3 or {money(round(2.15*fpl_m(4)))}/month for a family of 4. Families above that can still buy KidCare at full price."),
        ("How much does Florida KidCare cost?","Children who qualify for Medicaid pay nothing. MediKids and Florida Healthy Kids cost $15 or $20 per month per family, depending on income, with small copays for some services."),
        ("Can my child get KidCare if I have a job with insurance?","Usually not for the subsidized programs if the child is already covered by affordable employer insurance, but children in Medicaid can have other insurance too.")]
    title,desc,kw,main=_prog_shell(path,"#0891B2","#0E7490","Children's Health Coverage","Florida KidCare 2026 — Affordable Kids' Health Insurance",
        "Comprehensive health coverage for uninsured Florida children from birth through age 18 — doctor visits, dental, vision, mental health, hospital and prescriptions.",body,qa,None,"Check Eligibility →")
    from content import gov_service, PROG_PROVIDER
    nm,d,pn,pu=PROG_PROVIDER["kidcare"]
    g=graph(path,title,desc,trail_for(path),extra=[gov_service(path,nm,d,pn,pu),faq_schema(qa)])
    rel=related([("Florida Medicaid eligibility","/programs/medicaid/"),("Florida WIC for young children","/programs/wic/"),("Document Checklist Generator","/tools/document-checklist/"),("Florida Coverage Gap Tool","/tools/coverage-gap/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

def build_cliff_blog():
    path="/blog/income-cliff-snap-florida/"; title,desc,kw=SEO[path]
    title="The Florida Benefits Cliff 2026 — When a Raise Costs You"
    desc="Where Florida's real benefit cliffs are in 2026 — parent Medicaid at 26% FPL, LIHEAP at 150%, WIC at 185%, SNAP at 200% and KidCare at 215% — with dollar amounts and how to avoid them."
    SEO[path]=(title,desc,kw)
    P=lambda pct: money(round(pct/100*fpl_m(3)))
    cliff=[[P(26),"26%","Parent Medicaid ends — and ACA subsidies don't start until 100% FPL (coverage gap)"],
           [P(100),"100%","ACA Marketplace premium tax credits begin; SNAP net-income limit"],
           [P(138),"138%","Free Medicaid ends for children 6–18 (they move to KidCare, $15–$20/mo)"],
           [P(150),"150%","LIHEAP energy assistance ends (up to ~$700/year)"],
           [P(185),"185%","WIC ends for pregnant women, infants and children under 5"],
           [P(196),"196%","Pregnancy Medicaid ends"],
           [P(200),"200%","SNAP gross-income limit — SNAP ends entirely"],
           [P(215),"215%","KidCare subsidy ends — children move to full-price premiums"]]
    qa=[("What is the benefits cliff in Florida?","It's when a small raise pushes your income past an eligibility limit and you lose a benefit worth more than the raise. Florida's sharpest cliff is parent Medicaid at 26% of the poverty level, because Florida did not expand Medicaid and ACA subsidies don't begin until 100%."),
        ("At what income does SNAP stop in Florida?",f"Florida uses a 200% FPL gross-income limit: {money(2660)}/month for 1 person, {P(200)} for a family of 3 and $5,500 for a family of 4. Below that, SNAP shrinks gradually — about 30 cents per extra dollar of net income — rather than dropping off."),
        ("Does a raise always make me worse off?","No. Because SNAP phases out gradually, most raises leave you ahead. The cases to watch are raises that cross a hard limit — Medicaid for parents, LIHEAP, WIC, the 200% SNAP limit and the 215% KidCare limit."),
        ("Does the EITC count as income for SNAP?","No. Federal tax refunds, including the EITC, are not counted as income for SNAP or Medicaid and are excluded as resources for 12 months.")]
    faq="".join(f'<div class="mb-6"><h3 class="font-bold text-slate-900 mb-2">{q}</h3><p class="text-slate-700">{a}</p></div>' for q,a in qa)
    strat=[("Run the numbers first","Use the <a href=\"/tools/income-cliff/\" class=\"text-blue-700 underline\">Income Cliff Calculator</a> before accepting a raise or extra shifts."),
           ("Use pre-tax deductions","401(k), HSA, FSA and commuter contributions reduce countable income for SNAP and Medicaid while building savings."),
           ("Report every deduction","Child-care costs, high rent and utilities, and medical costs (60+ or disabled) lower your SNAP net income — many families under-report them."),
           ("Ask for non-cash compensation","Employer health insurance, paid leave and tuition help don't count as income."),
           ("Claim the EITC","Worth up to $8,231 for families with 3+ children in tax year 2026, and it never counts against SNAP or Medicaid."),
           ("Plan around the coverage gap","If a raise would take a parent above 26% FPL but not to 100%, consider whether a bigger change (more hours) can reach 100% FPL, where Marketplace subsidies start.")]
    sh="".join(f'<li><strong>{a}:</strong> {b}</li>' for a,b in strat)
    rows="".join(f'<tr class="{"bg-white" if i%2==0 else "bg-slate-50"}"><td class="px-4 py-3 font-semibold">{a}</td><td class="px-4 py-3">{b}</td><td class="px-4 py-3">{c}</td></tr>' for i,(a,b,c) in enumerate(cliff))
    main=f'''<main id="main-content"><article class="max-w-3xl mx-auto px-4 py-12">
<nav class="text-sm text-slate-500 mb-6" aria-label="Breadcrumb"><a href="/" class="hover:text-blue-700">Home</a> / <a href="/blog/" class="hover:text-blue-700">Blog</a> / <span>Florida Benefits Cliff</span></nav>
<div class="flex items-center gap-2 mb-4"><span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#FEE2E2;color:#B91C1C">Policy Deep Dive</span><span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#DBEAFE;color:#1D4ED8">✅ Verified {UPDATED_FULL}</span></div>
<h1 class="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-4">The Florida Benefits Cliff: When a Raise Can Cost You Money</h1>
<p class="text-xl text-slate-600 mb-6">Most Florida benefits shrink gradually as you earn more — but a few end all at once. Here is exactly where those cliffs are in 2026, what each one costs, and how to avoid them.</p>
<p class="text-sm text-slate-500 mb-8">📅 Last verified {UPDATED_FULL} • ⏱️ 7 min read</p>
<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-8"><p class="text-sm text-amber-900"><strong>Quick answer:</strong> For a Florida family of 3, the hard cliffs are parent Medicaid at {P(26)}/month, LIHEAP at {P(150)}, WIC at {P(185)}, SNAP at {P(200)} and the KidCare subsidy at {P(215)}. SNAP itself phases out gradually below its limit, so most raises still leave you ahead.</p></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">A real Florida example</h2>
<p class="text-slate-700 mb-3"><strong>Maria</strong> is a single mom in Jacksonville with two children. She works part-time earning <strong>{money(560)}/month</strong> — just under the parent Medicaid limit of {P(26)} — so she, her kids and her family all have Medicaid, plus SNAP.</p>
<p class="text-slate-700 mb-3">Her manager offers 8 more hours a week, taking her to <strong>{money(860)}/month</strong>. Her SNAP drops only modestly (about 30 cents per extra dollar of net income) and her children keep Medicaid. But <strong>Maria loses her own Medicaid</strong> — and because she is still below {P(100)} (100% FPL), she can't get Marketplace premium tax credits either. She has fallen into Florida's coverage gap.</p>
<p class="text-slate-700 mb-8">The extra $300 a month is real, but for someone with ongoing medical needs, losing coverage can cost far more. Florida community health centers (sliding-scale fees) and prescription assistance programs can soften the blow — see the <a href="/tools/coverage-gap/" class="text-blue-700 underline">Coverage Gap Tool</a>.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">2026 Florida Benefit Cliff Map (family of 3)</h2>
<div class="overflow-x-auto rounded-2xl border border-slate-100 shadow-sm mb-3"><table class="w-full text-sm"><caption class="sr-only">Florida benefit cliffs by monthly income for a household of 3, 2026</caption><thead><tr style="background:#DC2626;color:#fff"><th scope="col" class="px-4 py-3 text-left">Income / month</th><th scope="col" class="px-4 py-3 text-left">% FPL</th><th scope="col" class="px-4 py-3 text-left">What changes</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="text-xs text-slate-500 mb-10">Based on the 2026 HHS poverty guidelines ($27,320/year for 3) and KFF Medicaid/CHIP limits for Florida (January 2026). SNAP uses gross income; Medicaid and KidCare use MAGI income.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">Why SNAP is usually not the big cliff</h2>
<p class="text-slate-700 mb-8">SNAP benefits equal the maximum allotment minus 30% of net income, so every extra dollar earned reduces SNAP by roughly 24 cents after the 20% earned-income deduction. By the time a family nears Florida's 200% gross limit, the remaining SNAP benefit is usually small. The cliffs that hurt are the all-or-nothing programs: Medicaid, LIHEAP, WIC and KidCare subsidies.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">Strategies to avoid the cliff</h2>
<ul class="list-disc pl-6 space-y-2 text-slate-700 mb-10">{sh}</ul>
<h2 class="text-2xl font-bold text-slate-900 mb-4">FAQs</h2>{faq}
<div class="rounded-2xl p-6 text-white text-center mt-6" style="background:linear-gradient(135deg, #0E4D91, #1565C0)"><h2 class="text-2xl font-bold mb-2">Model Your Cliff Before You Move</h2><p class="mb-4">See what you gain and lose at any income level.</p><a href="/tools/income-cliff/" class="inline-block bg-white font-bold px-6 py-3 rounded-xl" style="color:#0E4D91">Run Income Cliff Check →</a></div>
</article></main>'''
    art={"@type":"Article","@id":BASE+path+"#article","headline":title,"description":desc,"datePublished":"2026-06-20","dateModified":UPDATED_ISO,
         "author":{"@type":"Organization","name":"FloridaBenefitCheck.com","url":BASE+"/"},"publisher":{"@id":BASE+"/#org"},"mainEntityOfPage":{"@id":BASE+path+"#webpage"},"image":BASE+"/og-image.png","inLanguage":"en-US"}
    g=graph(path,title,desc,trail_for(path),extra=[art,faq_schema(qa)])
    rel=related([("Income Cliff Calculator","/tools/income-cliff/"),("Florida Coverage Gap Tool","/tools/coverage-gap/"),("Florida SNAP income limits 2026","/blog/florida-snap-income-limits-2026/"),("EITC for Florida families","/programs/eitc/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

def build_snap_calc():
    path="/tools/snap-calculator/"
    title="Florida Food Stamp Calculator 2026 — How Much SNAP Will I Get?"
    desc="Free Florida SNAP calculator using the new FY2027 rules (Oct 1, 2026). Enter income, rent and bills to estimate your monthly food stamp benefit — up to $1,023 for a family of 4."
    kw="florida food stamp calculator,florida snap calculator,how much food stamps will i get florida,how much food stamps for a family of 4 in florida,snap benefits calculator florida"
    SEO[path]=(title,desc,kw)
    opts="".join(f'<option value="{n}"{" selected" if n==3 else ""}>{n} person{"s" if n>1 else ""}</option>' for n in range(1,9))
    def fld(lbl,attr,val="0",hint=""):
        return f'<div><label for="sc-{attr}" class="block text-sm font-semibold text-slate-700 mb-1">{lbl}</label><div class="relative"><span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold">$</span><input id="sc-{attr}" data-{attr} type="number" min="0" value="{val}" inputmode="decimal" class="w-full pl-8 p-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:outline-none font-semibold"></div>{f"<p class=\"text-xs text-slate-500 mt-1\">{hint}</p>" if hint else ""}</div>'
    maxrows="".join(f'<tr class="{"bg-white" if n%2 else "bg-slate-50"}"><td class="px-4 py-3 font-semibold">{n} {"person" if n==1 else "people"}</td><td class="px-4 py-3 text-right font-bold" style="color:#16A34A">{money(SNAP_MAX[n])}</td><td class="px-4 py-3 text-right">{money(SNAP_GROSS[n])}</td></tr>' for n in range(1,9))
    qa=[("How much food stamps will I get in Florida?","Your SNAP benefit is the maximum allotment for your household size minus 30% of your net income. In 2026–27 the maximum is $306 for 1 person, $562 for 2, $808 for 3 and $1,023 for 4. Use the calculator above for an estimate based on your income, rent and bills."),
        ("How much food stamps does a family of 4 get in Florida?","A family of 4 can receive up to $1,023 a month from October 1, 2026. A family of 4 earning $2,500 a month with $1,650 in rent and utilities and $300 in child care would get about $812."),
        ("How much food stamps does a family of 5 get in Florida?","The maximum for 5 people is $1,217 a month (FY2027). A family of 5 earning $3,000 a month with $1,800 in housing costs would receive roughly $797."),
        ("If I make $1,800 a month can I get food stamps in Florida?","Yes for most household sizes — Florida's gross limit is $2,660 for 1 person and higher for larger households. A single person earning $1,800 with $1,200 in rent and utilities would get about $115 a month."),
        ("What is the minimum SNAP benefit?","Eligible 1- and 2-person households receive at least $25 a month (FY2027).")]
    faq="".join(f'<div class="mb-6"><h3 class="font-bold text-slate-900 mb-2">{q}</h3><p class="text-slate-700 text-sm leading-relaxed">{a}</p></div>' for q,a in qa)
    main=f'''<main id="main-content" class="min-h-screen py-10 px-4 bg-slate-50"><div class="max-w-3xl mx-auto">
{TOOL_HERO("New — FY2027 Rules","#DCFCE7","#166534","Florida Food Stamp (SNAP) Calculator","Estimate how much SNAP you'll get each month using the official rules that took effect October 1, 2026 — including rent, utility and child-care deductions.")}
<div class="bg-white rounded-2xl shadow-xl border border-slate-100 p-6 sm:p-8" data-fbc-snapcalc="1">
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
<div><label for="sc-hh" class="block text-sm font-semibold text-slate-700 mb-1">Household size</label><select id="sc-hh" data-hh class="w-full p-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:outline-none">{opts}</select></div>
{fld("Monthly earnings (before taxes)","earned","2000","Wages, tips, self-employment")}
{fld("Other monthly income","unearned","0","Social Security, SSI, child support received, unemployment")}
{fld("Rent or mortgage","rent","1100","Include property tax & insurance")}
{fld("Utilities","util","200","Electric, gas, water, phone")}
{fld("Child or dependent care","care","0")}
{fld("Child support you pay","support","0")}
{fld("Medical costs (only if 60+ or disabled)","medical","0")}
</div>
<label class="flex items-center gap-2 text-sm text-slate-700 mb-5 cursor-pointer"><input data-ed type="checkbox" class="w-4 h-4 accent-green-600">Someone in my household is 60+ or has a disability</label>
<button type="button" data-go class="w-full py-4 rounded-xl text-white font-bold text-lg transition-all hover:opacity-90 hover:shadow-lg" style="background:linear-gradient(135deg, #16A34A, #15803D)">Calculate My SNAP Benefit →</button>
<div data-out class="mt-6" style="display:none" aria-live="polite"></div></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
<h2 class="font-bold text-slate-900 text-xl mb-3">Florida SNAP maximum benefits &amp; income limits (from Oct 1, 2026)</h2>
<div class="overflow-x-auto rounded-xl border border-slate-100 mb-3"><table class="w-full text-sm"><caption class="sr-only">Florida SNAP maximum monthly benefit and gross income limit by household size, FY2027</caption><thead><tr style="background:#16A34A;color:#fff"><th scope="col" class="px-4 py-3 text-left">Household</th><th scope="col" class="px-4 py-3 text-right">Max benefit</th><th scope="col" class="px-4 py-3 text-right">Gross income limit</th></tr></thead><tbody>{maxrows}</tbody></table></div>
<p class="text-xs text-slate-500">Standard deduction: $217 (1–3 people), $229 (4), $268 (5), $308 (6+). Excess shelter deduction capped at $769 unless a member is 60+ or disabled. Source: USDA FNS FY2027 COLA; HHS 2026 poverty guidelines.</p></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm"><h2 class="font-bold text-slate-900 text-xl mb-3">How the SNAP amount is calculated</h2>
<ol class="list-decimal pl-6 space-y-2 text-sm text-slate-700"><li>Add up gross monthly income. Florida allows gross income up to 200% of the poverty level (no gross test for households with someone 60+ or disabled).</li><li>Subtract 20% of earnings, the standard deduction, dependent care, child support paid and (for 60+/disabled) medical costs over $35.</li><li>Subtract excess shelter costs — housing and utilities above half of your adjusted income (up to $769).</li><li>The result is net income; it must be at or below 100% of the poverty level.</li><li>Your benefit = maximum allotment − 30% of net income (minimum $25 for 1–2 people).</li></ol></div>
<div class="mt-8 bg-white rounded-2xl p-6 border border-slate-100 shadow-sm"><h2 class="font-bold text-slate-900 text-xl mb-4">Frequently asked questions</h2>{faq}</div>
</div></main>'''
    g=graph(path,title,desc,trail_for(path),extra=[webapp(path,"Florida Food Stamp (SNAP) Calculator",desc),faq_schema(qa)])
    rel=related([("Florida SNAP income limits 2026","/blog/florida-snap-income-limits-2026/"),("How to apply for SNAP in Florida","/blog/how-to-apply-snap-florida-2026/"),("Florida EBT card guide","/blog/florida-ebt-card-guide/"),("Income Cliff Calculator","/tools/income-cliff/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel,extra_body_js=JS_TAG))

def build_ebt_guide():
    path="/blog/florida-ebt-card-guide/"
    title="Florida EBT Card Guide 2026 — Balance, Phone & Deposit Dates"
    desc="Florida EBT customer service number (1-888-356-3281), how to check your SNAP balance, replace a lost or stolen card, change your PIN, and when food stamps are deposited each month."
    kw="florida ebt phone number,florida ebt balance,lost ebt card florida,when does ebt reload florida,florida ebt customer service"
    SEO[path]=(title,desc,kw)
    qa=[("What is the Florida EBT customer service phone number?","Call 1-888-356-3281. It is free, available 24 hours a day, 7 days a week, and lets you check your balance, hear recent transactions, report a lost or stolen card and change your PIN."),
        ("How do I check my Florida EBT balance?","Call 1-888-356-3281, log in at ebtEDGE.com or the ebtEDGE app, check your last grocery receipt, or view it in your MyACCESS Florida account."),
        ("What do I do if I lose my Florida EBT card?","Call 1-888-356-3281 immediately to freeze the card so no one else can use your benefits, then request a replacement. Replacement cards usually arrive by mail within 7–10 days; benefits already on the old card move to the new one."),
        ("When does my Florida EBT card reload?","Florida deposits SNAP benefits on the same day every month, between the 1st and the 28th. Your date is set by your case number — you can see it in your MyACCESS Florida account. Benefits are available early that morning."),
        ("Can I use my Florida EBT card online?","Yes. Florida SNAP EBT cards work for online grocery orders at approved retailers such as Amazon, Walmart and Aldi. Delivery fees cannot be paid with SNAP."),
        ("Can stolen SNAP benefits be replaced?","Federal replacement of skimmed benefits ended for thefts after December 20, 2024 unless Congress renews it. Protect your card by freezing it in the ebtEDGE app between purchases and changing your PIN regularly.")]
    faq="".join(f'<div class="mb-6"><h3 class="font-bold text-slate-900 mb-2">{q}</h3><p class="text-slate-700">{a}</p></div>' for q,a in qa)
    main=f'''<main id="main-content"><article class="max-w-3xl mx-auto px-4 py-12">
<nav class="text-sm text-slate-500 mb-6" aria-label="Breadcrumb"><a href="/" class="hover:text-blue-700">Home</a> / <a href="/blog/" class="hover:text-blue-700">Blog</a> / <span>Florida EBT Card Guide</span></nav>
<div class="flex items-center gap-2 mb-4"><span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#DCFCE7;color:#166534">EBT</span><span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#DBEAFE;color:#1D4ED8">✅ Verified {UPDATED_FULL}</span></div>
<h1 class="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-4">Florida EBT Card Guide: Balance, Phone Number, Lost Card &amp; Deposit Dates</h1>
<p class="text-xl text-slate-600 mb-6">Everything you need to manage your Florida SNAP EBT card — in one place.</p>
<div class="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-8"><p class="text-sm text-amber-900"><strong>Quick answer:</strong> Florida EBT customer service is <strong>1-888-356-3281</strong> (free, 24/7). Use it to check your balance, report a lost card or change your PIN. You can also check your balance at ebtEDGE.com or in the ebtEDGE app.</p></div>
<h2 class="text-2xl font-bold text-slate-900 mb-4">Important Florida EBT contacts</h2>
<div class="overflow-x-auto rounded-2xl border border-slate-100 shadow-sm mb-10"><table class="w-full text-sm"><tbody>
<tr class="bg-white"><td class="px-4 py-3 font-semibold">EBT customer service (balance, lost card, PIN)</td><td class="px-4 py-3 text-right"><a href="tel:18883563281" class="text-blue-700 font-semibold">1-888-356-3281</a></td></tr>
<tr class="bg-slate-50"><td class="px-4 py-3 font-semibold">Online balance &amp; card lock</td><td class="px-4 py-3 text-right">ebtEDGE.com / ebtEDGE app</td></tr>
<tr class="bg-white"><td class="px-4 py-3 font-semibold">Case questions, renewals, deposit date</td><td class="px-4 py-3 text-right"><a href="https://www.myflorida.com/accessflorida/" target="_blank" rel="noopener noreferrer" class="text-blue-700">MyACCESS Florida</a> • <a href="tel:18667622237" class="text-blue-700">1-866-762-2237</a></td></tr>
<tr class="bg-slate-50"><td class="px-4 py-3 font-semibold">Local help 24/7</td><td class="px-4 py-3 text-right"><a href="tel:211" class="text-blue-700">Dial 2-1-1</a></td></tr></tbody></table></div>
<h2 class="text-2xl font-bold text-slate-900 mb-3">How to check your Florida EBT balance</h2>
<ul class="list-disc pl-6 space-y-2 text-slate-700 mb-10"><li><strong>Phone:</strong> call 1-888-356-3281 and enter your 16-digit card number.</li><li><strong>Online:</strong> log in at ebtEDGE.com or the free ebtEDGE app (iOS/Android).</li><li><strong>Receipt:</strong> your remaining balance prints at the bottom of every grocery receipt.</li><li><strong>MyACCESS:</strong> your benefit history shows in your MyACCESS Florida account.</li></ul>
<h2 class="text-2xl font-bold text-slate-900 mb-3">Lost, stolen or damaged card</h2>
<ol class="list-decimal pl-6 space-y-2 text-slate-700 mb-10"><li>Call 1-888-356-3281 right away to deactivate the card.</li><li>Request a replacement — it is mailed to the address on your case (usually 7–10 days). Update your address in MyACCESS first if you moved.</li><li>When the new card arrives, set a new PIN. Remaining benefits transfer automatically.</li><li>To prevent skimming, lock your card in the ebtEDGE app when you're not shopping and never share your PIN.</li></ol>
<h2 class="text-2xl font-bold text-slate-900 mb-3">When are food stamps deposited in Florida?</h2>
<p class="text-slate-700 mb-10">Florida staggers SNAP deposits across the <strong>1st to the 28th</strong> of each month. Your deposit day never changes from month to month and is determined by your case number — check "Benefits" in your MyACCESS account to see your exact date. Benefits are available early on the morning of your deposit day. Unused SNAP benefits roll over month to month, but are removed if the card is not used for 9 months.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-3">Where you can use your Florida EBT card</h2>
<p class="text-slate-700 mb-10">Any store displaying the SNAP/EBT logo, most farmers markets, and online at approved retailers including <a href="/blog/amazon-ebt-florida-snap-guide/" class="text-blue-700 underline">Amazon</a>, Walmart and Aldi. Since April 20, 2026 Florida restricts some purchases — see <a href="/blog/florida-snap-restrictions-ebt-2026/" class="text-blue-700 underline">what EBT can and can't buy in Florida</a>.</p>
<h2 class="text-2xl font-bold text-slate-900 mb-4">FAQs</h2>{faq}
<div class="rounded-2xl p-6 text-white text-center mt-6" style="background:linear-gradient(135deg, #16A34A, #15803D)"><h2 class="text-2xl font-bold mb-2">How much SNAP should you be getting?</h2><p class="mb-4">Check your amount with the free FY2027 Florida SNAP calculator.</p><a href="/tools/snap-calculator/" class="inline-block bg-white font-bold px-6 py-3 rounded-xl" style="color:#15803D">Open the SNAP Calculator →</a></div>
</article></main>'''
    art={"@type":"Article","@id":BASE+path+"#article","headline":title,"description":desc,"datePublished":UPDATED_ISO,"dateModified":UPDATED_ISO,
         "author":{"@type":"Organization","name":"FloridaBenefitCheck.com","url":BASE+"/"},"publisher":{"@id":BASE+"/#org"},"mainEntityOfPage":{"@id":BASE+path+"#webpage"},"image":BASE+"/og-image.png","inLanguage":"en-US"}
    g=graph(path,title,desc,trail_for(path),extra=[art,faq_schema(qa)])
    rel=related([("Florida SNAP calculator","/tools/snap-calculator/"),("Florida EBT restrictions 2026","/blog/florida-snap-restrictions-ebt-2026/"),("Using EBT on Amazon in Florida","/blog/amazon-ebt-florida-snap-guide/"),("How to apply for SNAP in Florida","/blog/how-to-apply-snap-florida-2026/")])
    lib.write(path,lib.page(title,desc,path,kw,main,jsonld=g,related_html=rel))

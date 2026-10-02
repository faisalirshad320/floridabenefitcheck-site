#!/usr/bin/env python3
"""Static-ify + SEO-enhance the captured content pages into dist/."""
import os, re, json, sys
sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import BASE, UPDATED_MONTH, UPDATED_FULL, UPDATED_ISO

KW_CORE = "florida benefits,florida snap eligibility,florida medicaid 2026,food stamps florida,florida benefits checker"

# Site-wide schema graph nodes (reused on every page)
def org_node():
    return {"@type":"Organization","@id":BASE+"/#org","name":"FloridaBenefitCheck.com","url":BASE+"/",
            "logo":{"@type":"ImageObject","url":BASE+"/og-image.png","width":1200,"height":630},
            "description":"Free, independent Florida government benefits eligibility checker with 2026 income limits.",
            "areaServed":{"@type":"State","name":"Florida"},"sameAs":[],
            "email":"info@floridabenefitcheck.com",
            "contactPoint":{"@type":"ContactPoint","contactType":"customer support","email":"info@floridabenefitcheck.com","url":BASE+"/contact/","availableLanguage":["English","Spanish"]},
            "parentOrganization":{"@type":"Organization","name":"Omnia Ventures","url":"https://www.omniaventures.org/",
                "founder":{"@type":"Person","name":"Dr. Faisal Irshad","url":"https://www.omniaventures.org/"}}}
def website_node():
    return {"@type":"WebSite","@id":BASE+"/#website","url":BASE+"/","name":"FloridaBenefitCheck.com",
            "description":"Free Florida government benefits eligibility checker","publisher":{"@id":BASE+"/#org"},
            "inLanguage":["en-US","es-US","ht"],
            "potentialAction":{"@type":"SearchAction","target":BASE+"/?q={search_term_string}","query-input":"required name=search_term_string"}}

def breadcrumb(trail):
    items=[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u} for i,(n,u) in enumerate(trail)]
    return {"@type":"BreadcrumbList","@id":BASE+trail[-1][1]+"#breadcrumb","itemListElement":items}

def webpage_node(path,title,desc,typ="WebPage"):
    return {"@type":typ,"@id":BASE+path+"#webpage","url":BASE+path,"name":title,"description":desc,
            "isPartOf":{"@id":BASE+"/#website"},"inLanguage":"en-US",
            "dateModified":UPDATED_ISO,"datePublished":"2026-06-19",
            "breadcrumb":{"@id":BASE+path+"#breadcrumb"},
            "publisher":{"@id":BASE+"/#org"}}

def graph(path,title,desc,trail,extra=None,webtype="WebPage"):
    g=[website_node(),org_node(),webpage_node(path,title,desc,webtype),breadcrumb(trail)]
    if extra:
        g+= extra if isinstance(extra,list) else [extra]
    return {"@context":"https://schema.org","@graph":g}

def gov_service(path,name,desc,provider_name,provider_url):
    return {"@type":"GovernmentService","name":name,"serviceType":"Government benefit program",
            "description":desc,"areaServed":{"@type":"State","name":"Florida"},
            "provider":{"@type":"GovernmentOrganization","name":provider_name,"url":provider_url},
            "audience":{"@type":"Audience","audienceType":"Florida residents with low income"},
            "availableChannel":{"@type":"ServiceChannel","serviceUrl":"https://www.myflorida.com/accessflorida/"}}

PROG_PROVIDER={
 "snap":("Florida SNAP (Food Stamps)","Florida's Supplemental Nutrition Assistance Program providing monthly food benefits via EBT.","Florida Department of Children and Families","https://www.myflfamilies.com/"),
 "medicaid":("Florida Medicaid","Free or low-cost health coverage for eligible low-income Florida residents, children, pregnant women, elderly and disabled.","Florida Agency for Health Care Administration","https://ahca.myflorida.com/"),
 "ssi":("Supplemental Security Income (SSI) in Florida","Monthly federal cash benefits for aged, blind or disabled people with limited income and resources.","Social Security Administration","https://www.ssa.gov/"),
 "liheap":("Florida LIHEAP (Home Energy Assistance)","Help paying home heating and cooling energy bills for income-eligible Florida households.","Florida Department of Commerce","https://www.floridajobs.org/"),
 "wic":("Florida WIC","Nutrition assistance for pregnant women, new mothers, infants and children under 5.","Florida Department of Health","https://www.floridawic.org/"),
 "tanf":("Florida TANF (Temporary Cash Assistance)","Temporary monthly cash assistance for very low-income families with children.","Florida Department of Children and Families","https://www.myflorida.com/accessflorida/"),
 "kidcare":("Florida KidCare","Low-cost children's health insurance for Florida families.","Florida Healthy Kids Corporation","https://www.floridakidcare.org/"),
 "lifeline":("Lifeline in Florida","Federal discount on monthly phone or internet service for income-eligible households.","Universal Service Administrative Company","https://www.lifelinesupport.org/"),
 "eitc":("Earned Income Tax Credit (EITC)","Refundable federal tax credit for low-to-moderate-income working people and families.","Internal Revenue Service","https://www.irs.gov/"),
}

# title / description / keywords per path (strong, keyword-targeted, 2026)
SEO={
 "/": ("Florida Benefits Checker 2026 — SNAP, Medicaid, SSI & More",
   "Check if you qualify for SNAP, Medicaid, SSI, LIHEAP, WIC, TANF, KidCare, Lifeline and EITC in Florida in 60 seconds. Free, no signup, 2026 income limits. English, Español, Kreyòl.",
   "florida benefits checker,florida snap eligibility 2026,florida medicaid eligibility 2026,snap income limits florida 2026,am i eligible for food stamps florida"),
 "/programs/": ("Florida Benefit Programs 2026 — Income Limits for 9 Programs",
   "Compare 2026 eligibility and income limits for Florida SNAP, Medicaid, SSI, LIHEAP, WIC, TANF, KidCare, Lifeline and the EITC. See which assistance programs you may qualify for.",
   "florida benefit programs,florida assistance programs 2026,florida welfare programs,florida income limits 2026"),
 "/programs/snap/": ("Florida SNAP Eligibility & Income Limits 2026 — Food Stamps Guide",
   "2026 Florida SNAP (food stamps) income limits by household size, who qualifies, benefit amounts up to $1,023/mo for a family of 4, and how to apply through ACCESS Florida.",
   "florida snap eligibility 2026,snap income limits florida 2026,food stamps florida income limit,how to apply for food stamps florida,florida ebt"),
 "/programs/medicaid/": ("Florida Medicaid Eligibility & Income Limits 2026 — Who Qualifies",
   "2026 Florida Medicaid income limits for children, pregnant women, parents, elderly and disabled residents, the coverage gap explained, and how to apply.",
   "florida medicaid eligibility 2026,florida medicaid income limits 2026,medicaid florida who qualifies,florida medicaid application"),
 "/programs/ssi/": ("Florida SSI 2026 — Payment Amounts, Income Limits & Eligibility",
   "2026 SSI federal benefit rate ($994 individual, $1,491 couple), income and asset limits, and how to qualify for Supplemental Security Income in Florida.",
   "ssi florida 2026,ssi payment amount 2026,ssi income limit 2026,supplemental security income florida,ssi eligibility"),
 "/programs/liheap/": ("Florida LIHEAP 2026 — Energy Bill Help & Income Limits",
   "Florida LIHEAP helps pay home cooling and heating bills. 2026 income limits (150% FPL), benefit amounts up to $700, and how to apply by county.",
   "florida liheap 2026,liheap florida income limit,energy bill assistance florida,help paying electric bill florida"),
 "/programs/wic/": ("Florida WIC 2026 — Eligibility, Income Limits & Benefits",
   "Florida WIC nutrition benefits for pregnant women, new mothers, infants and children under 5. 2026 income limits (185% FPL) and how to apply.",
   "florida wic 2026,wic income limit florida,wic eligibility florida,wic benefits florida"),
 "/programs/tanf/": ("Florida TANF 2026 — Temporary Cash Assistance Eligibility & Amounts",
   "Florida TANF temporary cash assistance for families with children. 2026 income limits, payment amounts (up to $303/mo for a family of 3), and how to apply.",
   "florida tanf 2026,temporary cash assistance florida,tanf income limit florida,florida welfare cash"),
 "/programs/kidcare/": ("Florida KidCare 2026 — Children's Health Insurance Eligibility & Cost",
   "Florida KidCare low-cost children's health insurance. 2026 income eligibility, monthly premiums ($0–$20), covered services, and how to enroll.",
   "florida kidcare 2026,florida kidcare eligibility,florida kidcare income limit,childrens health insurance florida"),
 "/programs/lifeline/": ("Lifeline Florida 2026 — Free/Discounted Phone & Internet Eligibility",
   "Lifeline gives income-eligible Florida households $9.25/mo off phone or internet. 2026 eligibility (135% FPL or SNAP/Medicaid) and how to apply.",
   "lifeline florida 2026,free phone florida,lifeline internet discount florida,lifeline eligibility"),
 "/programs/eitc/": ("Florida EITC 2026 — Earned Income Tax Credit Up to $8,231",
   "2026 Earned Income Tax Credit for Florida workers: who qualifies, income limits by number of children, and the maximum credit of $8,231 for 3+ children.",
   "eitc 2026,earned income tax credit 2026,eitc florida,eitc income limit 2026,maximum eitc 2026"),
 "/tools/": ("Free Florida Benefits Tools 2026 — Calculators & Resource Finders",
   "Four free Florida-only tools: the Income Cliff Calculator, Medicaid Coverage Gap Tool, Document Checklist generator and County Resource Finder.",
   "florida benefits calculator,income cliff calculator florida,medicaid coverage gap florida,florida dcf office finder"),
 "/tools/income-cliff/": ("Florida Income Cliff Calculator 2026 — Will a Raise Cut My Benefits?",
   "See whether a pay raise will cost you more in lost Florida benefits than you gain. Free 2026 income cliff calculator for SNAP, Medicaid, SSI and LIHEAP.",
   "income cliff calculator,benefits cliff florida,will a raise affect my benefits,snap income cliff florida 2026"),
 "/tools/coverage-gap/": ("Florida Medicaid Coverage Gap Tool 2026 — Are You Stuck in the Gap?",
   "800,000 Floridians earn too much for Medicaid but too little for ACA subsidies. Check the 2026 coverage gap thresholds by household size and see your options.",
   "florida coverage gap,medicaid coverage gap florida,florida medicaid gap 2026,no medicaid expansion florida"),
 "/tools/document-checklist/": ("Florida Benefits Document Checklist 2026 — What to Bring to Apply",
   "Generate a personalized checklist of documents needed to apply for Florida SNAP, Medicaid, SSI, LIHEAP, WIC and KidCare. Know exactly what to bring.",
   "florida benefits documents,what documents for food stamps florida,snap application documents florida,medicaid application documents"),
 "/tools/county-finder/": ("Florida County Resource Finder 2026 — DCF Offices & Food Banks",
   "Find your local Florida DCF office phone number, food bank and benefits help by county, plus the Florida 2-1-1 helpline for 24/7 assistance.",
   "florida dcf office,dcf office near me,florida food bank,florida 211,benefits office florida by county"),
 "/blog/": ("Florida Benefits Blog 2026 — SNAP, Medicaid & EBT Guides",
   "Guides and updates on Florida SNAP, Medicaid, EBT rules, income limits and how to apply, written for Florida residents. Updated for 2026.",
   "florida benefits blog,florida snap news 2026,florida ebt rules 2026,florida medicaid news"),
 "/blog/florida-snap-restrictions-ebt-2026/": ("Florida SNAP Changes 2026 — New EBT Restrictions Explained",
   "Florida's 2026 SNAP changes explained: the junk-food and soda limits that began April 20, 2026, the full list of what EBT can and can't buy, and how the new FY2027 benefit amounts affect you.",
   "florida snap benefits changes,florida ebt restrictions 2026,junk food snap limits florida,can you buy chips with ebt in florida,what can you buy with ebt florida"),
 "/blog/florida-snap-income-limits-2026/": ("Florida SNAP Income Limits 2026 — Full Chart by Household Size",
   "Complete 2026 Florida SNAP income limits by household size: gross (200% FPL) and net limits, maximum monthly allotments, and who qualifies.",
   "snap income limits florida 2026,food stamp income limit florida,florida snap chart 2026,snap gross income limit"),
 "/blog/florida-medicaid-eligibility-2026/": ("Florida Medicaid Eligibility 2026 — Income Limits & Who Qualifies",
   "Who qualifies for Florida Medicaid in 2026: income limits for children, pregnant women, parents, aged and disabled, plus the coverage gap explained.",
   "florida medicaid eligibility 2026,medicaid income limit florida 2026,who qualifies for medicaid florida"),
 "/blog/how-to-apply-snap-florida-2026/": ("How to Apply for Food Stamps (SNAP) in Florida 2026 — Step by Step",
   "Step-by-step 2026 guide to applying for Florida SNAP food stamps through ACCESS Florida: documents needed, the interview, timelines and approval.",
   "how to apply for food stamps florida,apply snap florida 2026,access florida application,florida snap interview"),
 "/blog/amazon-ebt-florida-snap-guide/": ("Using Florida EBT on Amazon 2026 — SNAP Online Grocery Guide",
   "How to use your Florida EBT card on Amazon for SNAP-eligible groceries in 2026: setup, what qualifies, delivery, and no Prime required.",
   "amazon ebt florida,use ebt on amazon,snap online grocery florida,florida ebt amazon 2026"),
 "/blog/income-cliff-snap-florida/": ("The Florida SNAP Income Cliff Explained 2026 — Raises & Benefits",
   "What the SNAP benefit cliff means in Florida, how a raise can reduce food stamps, and how to avoid losing more than you gain in 2026.",
   "snap income cliff florida,benefits cliff florida,does a raise affect food stamps florida"),
 "/blog/florida-medicaid-expansion-2026/": ("Florida Medicaid Expansion 2026 — Current Status & the Coverage Gap",
   "The 2026 status of Florida Medicaid expansion, why 800,000 residents are in the coverage gap, and what it means for adults without children.",
   "florida medicaid expansion 2026,florida medicaid gap,medicaid expansion ballot florida"),
 "/about/": ("About FloridaBenefitCheck.com — Our Mission & Data Sources",
   "FloridaBenefitCheck.com is a free, independent resource helping Florida residents check benefit eligibility. Learn about our mission, data sources and methodology.",
   "about floridabenefitcheck,florida benefits resource,benefits eligibility methodology"),
 "/contact/": ("Contact FloridaBenefitCheck.com",
   "Contact FloridaBenefitCheck.com with questions or corrections about Florida benefit eligibility information. We are an independent informational resource.",
   "contact floridabenefitcheck,florida benefits questions"),
 "/es/": ("Verificador de Beneficios de Florida 2026 — SNAP, Medicaid, SSI y Más",
   "Verifique si califica para SNAP, Medicaid, SSI, LIHEAP, WIC, TANF, KidCare, Lifeline y EITC en Florida en 60 segundos. Gratis, sin registro, límites de ingresos 2026.",
   "beneficios florida espanol,elegibilidad snap florida 2026,medicaid florida espanol,cupones de alimentos florida"),
 "/ht/": ("Verifikatè Benefis Florid 2026 — SNAP, Medicaid, SSI ak Plis",
   "Verifye si ou kalifye pou SNAP, Medicaid, SSI, LIHEAP, WIC, TANF, KidCare, Lifeline ak EITC nan Florid nan 60 segonn. Gratis, san enskripsyon, limit revni 2026.",
   "benefis florid kreyol,snap florid,medicaid florid,koupon manje florid"),
}

TRAIL_BASE=[("Home","/")]
def trail_for(path):
    t=[("Home","/")]
    if path=="/": return t
    segs=[s for s in path.strip("/").split("/")]
    # build labels
    labelmap={"programs":"Programs","tools":"Tools","blog":"Blog","about":"About","contact":"Contact",
              "privacy":"Privacy","disclaimer":"Disclaimer","accessibility":"Accessibility","checker":"Eligibility Checker",
              "es":"Español","ht":"Kreyòl"}
    cur=""
    for i,s in enumerate(segs):
        cur+="/"+s
        name=labelmap.get(s, SEO.get(cur+"/",(s.replace("-"," ").title(),))[0].split(" — ")[0] if (cur+"/") in SEO else s.replace("-"," ").title())
        t.append((name, cur+"/"))
    return t

DATE_FIXES=[
  ("2026 Income Limits Updated September 25", f"2026 Income Limits — Updated {UPDATED_MONTH}"),
  ("Updated September 25", f"Updated {UPDATED_MONTH}"),
  ("September 25, 2026", UPDATED_FULL),
  ("Updated January 15", f"Updated {UPDATED_MONTH}"),
  ("Data updated January 2026", f"Data updated {UPDATED_MONTH}"),
  ("January 15 FPL update — all programs now reflect new thresholds", f"Verified {UPDATED_FULL}: 2026 poverty guidelines + new FY2027 SNAP amounts"),
  ("2026 Income Limits Updated</h3>", "2026 Income Limits Verified</h3>"),
  ("UPDATED 2026-09-25", "UPDATED 2026-10-01"),
  ("updated January 15, 2026. A family of 4 can earn up to $3,575/month", "verified October 1, 2026. A family of 4 can earn up to $5,500/month (200% FPL)"),("2026-09-25", "2026-10-01"),
  ("Data updated January 15", f"Data updated {UPDATED_MONTH}"),
]
def fix_dates(hmtl):
    for a,b in DATE_FIXES:
        hmtl=hmtl.replace(a,b)
    # catch "Updated January 15" variants in news card subtitle
    hmtl=re.sub(r"Updated January 15[, ]*2026?", f"Updated {UPDATED_MONTH}", hmtl)
    return hmtl


# ---- page-scoped factual corrections (verified vs KFF Jan 2026 / HHS 2026 FPL / USDA FY2027) ----
G130={1:"1,729",2:"2,345",3:"2,960",4:"3,575",5:"4,191",6:"4,806",7:"5,421",8:"6,037"}
G200={1:"2,660",2:"3,607",3:"4,554",4:"5,500",5:"6,447",6:"7,394",7:"8,340",8:"9,287"}
PAGE_FIXES={
 "/about/":[('<div class="bg-amber-50 rounded-2xl p-4 border border-amber-200 text-sm"><strong>Disclaimer:</strong>','<h2 class="text-xl font-bold text-slate-900">Who Runs FloridaBenefitCheck.com</h2><p>FloridaBenefitCheck.com is an independent website operated by <a class="text-blue-600 hover:underline" href="https://www.omniaventures.org/">Omnia Ventures</a>, a small publisher of free health and utility websites founded by Dr. Faisal Irshad. We are not a government agency, a law firm or a benefits contractor, and no agency or company pays us to send people anywhere. We never ask for your Social Security number, case number or bank details.</p><h2 class="text-xl font-bold text-slate-900">Editor</h2><p><strong>Dr. Faisal Irshad</strong> (MBBS, M.Phil Chemical Pathology), founder of Omnia Ventures, edits the site and is responsible for its accuracy. Every income limit, benefit amount and percentage on this site is checked against the primary sources below before publication, and corrections are made as soon as an error is confirmed.</p><div class="bg-slate-50 rounded-2xl p-6 border border-slate-100"><h2 class="text-xl font-bold text-slate-900 mb-3">How We Verify Our Figures</h2><ul class="space-y-2 text-sm"><li><strong>Federal poverty level (FPL):</strong> 2026 HHS Poverty Guidelines — $15,960 for one person plus $5,680 per additional person.</li><li><strong>SNAP:</strong> USDA FNS fiscal-year 2027 cost-of-living adjustment (effective October 1, 2026) for maximum allotments and deductions; Florida&rsquo;s 200% FPL gross-income limit under broad-based categorical eligibility (Florida DCF).</li><li><strong>Medicaid and KidCare:</strong> KFF Medicaid and CHIP eligibility limits as of January 2026, cross-checked with Florida DCF and Florida KidCare.</li><li><strong>SSI:</strong> Social Security Administration 2026 federal benefit rates ($994 individual / $1,491 couple).</li><li><strong>EITC:</strong> IRS tax-year 2026 inflation adjustments (maximum credit $8,231 with three or more children).</li></ul><p class="text-sm mt-3">We re-verify everything twice a year: each <strong>October 1</strong> (new SNAP amounts) and each <strong>January</strong> (new poverty guidelines). The &ldquo;Verified&rdquo; date shown on each page is the last time its figures were checked. Found an error? Email <a class="text-blue-600 hover:underline" href="mailto:info@floridabenefitcheck.com">info@floridabenefitcheck.com</a> and include the page and the source you are comparing against.</p></div><div class="bg-amber-50 rounded-2xl p-4 border border-amber-200 text-sm"><strong>Disclaimer:</strong>')],
 "/contact/":[('partnership inquiries, or press:</p>','partnership inquiries, or press:</p><p class="text-sm text-slate-600 mb-4">FloridaBenefitCheck.com is operated by <a class="text-blue-600 hover:underline" href="https://www.omniaventures.org/">Omnia Ventures</a> and edited by Dr. Faisal Irshad. We reply to most messages within three working days. We cannot look up or change your benefits case &mdash; for that, contact the official agencies above.</p>')],
 "/programs/snap/":[("Gross Monthly Limit","Gross Monthly Limit (200% FPL)")]+[(f'$<!-- -->{G130[n]}</td>',f'$<!-- -->{G200[n]}</td>') for n in G130]+[
   ("* Gross limit = 130% FPL federally (Florida allows up to 200% FPL for most households). Net limit = 100% FPL. Elderly/disabled households only need to meet net income test. For households of 9+, add $616 gross / $474 net per additional person.",
    "* Gross limit = 200% FPL — Florida uses broad-based categorical eligibility, so most households are tested at 200% instead of the federal 130%. Net limit = 100% FPL. Households with a member 60+ or disabled only need to meet the net income test. For households of 9+, add about $947 gross / $474 net per additional person. Max benefits are FY2027 amounts effective October 1, 2026.")],
 "/blog/how-to-apply-snap-florida-2026/":[("Gross household income at or below 130% FPL ($2,960/mo for family of 3 in 2026)","Gross household income at or below 200% FPL ($4,554/mo for a family of 3 in 2026 — Florida's broad-based limit)")],
 "/blog/florida-medicaid-eligibility-2026/":[
   ("Florida Medicaid covers children up to 200% FPL, pregnant women up to 200% FPL, elderly/disabled adults up to 100% FPL, and parents up to 33% FPL.",
    "Florida Medicaid covers children up to 211% FPL (under age 1), 145% (ages 1–5) and 138% (ages 6–18), with KidCare covering children up to 215% FPL; pregnant women up to 196% FPL; aged/disabled adults up to 88% FPL; and parents only up to 26% FPL (KFF, January 2026)."),
   ("Up to 200% FPL via KidCare ($66,000/year for family of 4)","Up to 215% FPL via Medicaid + KidCare ($70,950/year for family of 4)"),
   ("Up to 200% FPL (based on household size)","Up to 196% FPL (about $53,547/year for a household of 3)"),
   ("Up to 88% FPL (~$14,184/year for 1 person)","Up to 88% FPL (~$14,045/year for 1 person)"),
   ("limit is just 33% FPL for parents, zero for childless adults","limit is just 26% FPL for parents, zero for childless adults")],
}
CALLOUT='<div style="max-width:56rem;margin:24px auto;padding:0 16px"><div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:16px;padding:18px 20px"><strong style="color:#166534">New:</strong> <a href="/tools/snap-calculator/" style="color:#15803D;font-weight:700;text-decoration:underline">Estimate your exact SNAP amount with the FY2027 Florida food stamp calculator</a> · <a href="/blog/florida-ebt-card-guide/" style="color:#15803D;font-weight:600;text-decoration:underline">EBT card balance, phone number &amp; deposit dates</a></div></div>'
def apply_page_fixes(path,html):
    for a,b in PAGE_FIXES.get(path,[]):
        html=html.replace(a,b)
    if path in ("/programs/snap/","/blog/how-to-apply-snap-florida-2026/","/blog/florida-snap-restrictions-ebt-2026/","/blog/amazon-ebt-florida-snap-guide/"):
        html=html.replace("</main>",CALLOUT+"</main>",1)
    return html

# pages to static-ify from mirror disk (path -> mirror file)
DISK_PAGES = {
 "/programs/":"programs/index.html",
 "/programs/snap/":"programs/snap/index.html",
"/programs/liheap/":"programs/liheap/index.html",
 "/programs/wic/":"programs/wic/index.html","/programs/tanf/":"programs/tanf/index.html",
 "/programs/lifeline/":"programs/lifeline/index.html",
 "/programs/eitc/":"programs/eitc/index.html",
 "/tools/county-finder/":"tools/county-finder/index.html",
 "/blog/":"blog/index.html",
 "/blog/florida-snap-restrictions-ebt-2026/":"blog/florida-snap-restrictions-ebt-2026/index.html",
  "/blog/florida-medicaid-eligibility-2026/":"blog/florida-medicaid-eligibility-2026/index.html",
 "/blog/how-to-apply-snap-florida-2026/":"blog/how-to-apply-snap-florida-2026/index.html",
 "/blog/amazon-ebt-florida-snap-guide/":"blog/amazon-ebt-florida-snap-guide/index.html",
 
 "/blog/florida-medicaid-expansion-2026/":"blog/florida-medicaid-expansion-2026/index.html",
 "/about/":"about/index.html","/contact/":"contact/index.html",
 "/es/":"es/index.html","/ht/":"ht/index.html",
}

def build_disk_pages():
    n=0
    for path,mrel in DISK_PAGES.items():
        title,desc,kw = SEO[path]
        main,related = lib.extract_main(mrel)
        main=fix_dates(main); related=fix_dates(related)
        main=apply_page_fixes(path,main)
        trail=trail_for(path)
        extra=None; webtype="WebPage"
        if path.startswith("/programs/") and path!="/programs/":
            slug=path.strip("/").split("/")[1]
            nm,d,pn,pu=PROG_PROVIDER[slug]
            extra=[gov_service(path,nm,d,pn,pu)]
            webtype="WebPage"
        if path.startswith("/blog/") and path!="/blog/":
            MON={"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
            mm=re.search(r"Updated (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2})",re.sub(r"<[^>]+>"," ",main))
            dmod=f"2026-{MON[mm.group(1).lower()]:02d}-{int(mm.group(2)):02d}" if mm else UPDATED_ISO
            extra=[{"@type":"Article","@id":BASE+path+"#article","headline":title,"description":desc,
                    "datePublished":min("2026-06-20",dmod),"dateModified":dmod,
                    "author":{"@type":"Organization","name":"FloridaBenefitCheck.com","url":BASE+"/"},
                    "publisher":{"@id":BASE+"/#org"},"mainEntityOfPage":{"@id":BASE+path+"#webpage"},
                    "image":BASE+"/og-image.png","inLanguage":"en-US"}]
        hreflang = path in ("/","/es/","/ht/")
        g=graph(path,title,desc,trail,extra=extra,webtype=webtype)
        if path.startswith("/blog/") and path!="/blog/":
            g["@graph"][2]["dateModified"]=extra[0]["dateModified"]; g["@graph"][2]["datePublished"]=extra[0]["datePublished"]
        htmlout=lib.page(title,desc,path,kw,main,jsonld=g,hreflang=hreflang,related_html=related)
        fp=lib.write(path,htmlout); n+=1
    return n

if __name__=="__main__":
    import shutil
    os.makedirs(lib.DIST,exist_ok=True)
    n=build_disk_pages()
    print("content pages written:",n)

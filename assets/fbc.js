/* FloridaBenefitCheck — eligibility engine + tools (vanilla JS, no framework).
 * Engine is a faithful port of the site's original checkAllEligibility() logic.
 * All constants verified Oct 2026: 2026 HHS FPL ($15,960 + $5,680/person),
 * FY2027 SNAP allotments (eff. Oct 1 2026), 2026 SSI FBR ($994/$1,491), TY2026 EITC. */
(function(){
"use strict";
/* ---------- constants ---------- */
var FPL_BASE=15960, FPL_ADD=5680;
function fplMonthly(hh){ return Math.round((FPL_BASE+FPL_ADD*Math.max(hh-1,0))/12); }
var SNAP={1:{g:2660,n:1330,max:306},2:{g:3607,n:1804,max:562},3:{g:4554,n:2277,max:808},4:{g:5500,n:2750,max:1023},
          5:{g:6447,n:3224,max:1217},6:{g:7394,n:3697,max:1463},7:{g:8340,n:4170,max:1616},8:{g:9287,n:4644,max:1841}};
var MED_CHILD=211, MED_PREG=196, MED_PARENT=26, MED_AGED=88, KIDCARE=215; /* KFF, Jan 2026 */
var SSI_IND=994, SSI_CPL=1491, SSI_FL_SUP_IND=0, SSI_FL_SUP_CPL=0, SSI_INC_IND=2073, SSI_INC_CPL=3067, SSI_AST_IND=2000, SSI_AST_CPL=3000;
var EITC_MAX={noChildren:664,oneChild:4427,twoChildren:7316,threeOrMore:8231};
var EITC_SINGLE={noChildren:19540,oneChild:51593,twoChildren:58629,threeOrMore:62974};
var EITC_MARRIED={noChildren:26820,oneChild:58863,twoChildren:65899,threeOrMore:70244};

/* ---------- engine ---------- */
function checkSNAP(e){
  var t=SNAP[Math.min(e.householdSize,8)]||SNAP[8], g=t.g, n=t.n;
  if(e.hasElderly||e.hasDisabled){
    return e.grossMonthlyIncome<=n
      ? {eligible:true,reason:"Meets income limits for elderly/disabled household",est:t.max,g:g,n:n}
      : {eligible:false,reason:"Income $"+e.grossMonthlyIncome+"/mo exceeds the $"+n+"/mo limit for your household size",est:0,g:g,n:n};
  }
  if(e.grossMonthlyIncome<=g){
    var net=Math.max(0,0.8*e.grossMonthlyIncome), est=Math.max(0,t.max-Math.round(0.3*net));
    if(e.householdSize<=2&&est<25) est=25; /* FY2027 minimum benefit for 1-2 person households */
    if(est<=0) return {eligible:false,reason:"Your income is under the $"+g+"/mo gross limit, but after the 30% benefit reduction your estimated SNAP amount is $0. Deductions for rent, utilities, child care or medical costs could still qualify you — apply to get an exact figure.",est:0,g:g,n:n};
    return {eligible:true,reason:"Meets gross income limit",est:est,g:g,n:n};
  }
  return {eligible:false,reason:"Income $"+e.grossMonthlyIncome+"/mo exceeds the $"+g+"/mo gross limit for household of "+e.householdSize,est:0,g:g,n:n};
}
function checkMedicaid(e){
  if(!e.isCitizen) return {eligible:false,category:"",reason:"Must be a US citizen or qualified immigrant"};
  var f=fplMonthly(e.householdSize);
  if(e.hasChildren&&e.age<19&&e.grossMonthlyIncome<=MED_CHILD/100*f) return {eligible:true,category:"Children's Medicaid",reason:"Child under 19 meets income limits"};
  if(e.isPregnant&&e.grossMonthlyIncome<=MED_PREG/100*f) return {eligible:true,category:"Pregnancy Medicaid",reason:"Pregnant and meets income limits"};
  if((e.age>=65||e.isDisabled)&&e.grossMonthlyIncome<=MED_AGED/100*f) return {eligible:true,category:"Aged/Disabled Medicaid",reason:"Elderly or disabled and meets income limits"};
  var lim=MED_PARENT/100*f;
  if(e.hasChildren&&e.grossMonthlyIncome<=lim) return {eligible:true,category:"Adult Medicaid (very limited)",reason:"Meets Florida's restrictive adult income limit"};
  return {eligible:false,category:"",reason:"Florida has not expanded Medicaid — parents qualify only up to 26% FPL and adults without children not at all ($"+Math.round(lim)+"/mo). You may be in the coverage gap."};
}
function checkSSI(e){
  var aged=e.age>=65, dis=e.isDisabled;
  if(!aged&&!dis) return {eligible:false,reason:"Must be 65+ or have a qualifying disability",est:0};
  var incLim=e.isMarried?SSI_INC_CPL:SSI_INC_IND, astLim=e.isMarried?SSI_AST_CPL:SSI_AST_IND;
  if(e.assets>astLim) return {eligible:false,reason:"Assets $"+e.assets.toLocaleString()+" exceed the $"+astLim.toLocaleString()+" limit",est:0};
  if(e.monthlyIncome>incLim) return {eligible:false,reason:"Income $"+e.monthlyIncome+"/mo exceeds the $"+incLim+"/mo SSI income limit",est:0};
  var fbr=e.isMarried?SSI_CPL:SSI_IND, sup=e.isMarried?SSI_FL_SUP_CPL:SSI_FL_SUP_IND;
  var fed=Math.max(0,fbr-Math.max(0,e.monthlyIncome-65));
  return {eligible:true,reason:"Meets age/disability, income, and asset requirements",est:fed+sup};
}
function checkAll(e){
  var out=[], f=fplMonthly(e.householdSize);
  var s=checkSNAP({householdSize:e.householdSize,grossMonthlyIncome:e.grossMonthlyIncome,hasElderly:e.hasElderly,hasDisabled:e.isDisabled});
  out.push({program:"SNAP (Food Stamps)",slug:"snap",eligible:s.eligible,reason:s.reason,monthly:s.est,
    estimatedBenefit:s.eligible?"Up to $"+s.est+"/month for groceries":"Not eligible",applyUrl:"https://www.myflorida.com/accessflorida/",color:"#16A34A",icon:"🛒"});
  var m=checkMedicaid(e);
  out.push({program:"Florida Medicaid",slug:"medicaid",eligible:m.eligible,reason:m.reason,monthly:0,
    estimatedBenefit:m.eligible?"Free or low-cost health coverage":"Not eligible — see Coverage Gap tool",applyUrl:"https://www.myflorida.com/accessflorida/",color:"#2563EB",icon:"🏥"});
  if(e.age>=65||e.isDisabled){
    var si=checkSSI({isDisabled:e.isDisabled,age:e.age,monthlyIncome:e.grossMonthlyIncome,assets:e.assets,isMarried:e.isMarried});
    out.push({program:"SSI (Disability/Elderly)",slug:"ssi",eligible:si.eligible,reason:si.reason,monthly:si.est,
      estimatedBenefit:si.eligible?"~$"+si.est+"/month (federal SSI)":"Not eligible",applyUrl:"https://www.ssa.gov/benefits/ssi/",color:"#7C3AED",icon:"♿"});
  }
  var lih=1.5*f, lihOK=e.grossMonthlyIncome<=lih;
  out.push({program:"LIHEAP (Energy Bills)",slug:"liheap",eligible:lihOK,reason:lihOK?"Meets 150% FPL income limit for energy assistance":"Income exceeds 150% FPL ($"+Math.round(lih)+"/mo) for energy assistance",monthly:0,
    estimatedBenefit:lihOK?"Up to $700 for cooling/heating bills":"Not eligible",applyUrl:"https://www.floridajobs.org/community-planning-and-development/community-services/low-income-home-energy-assistance-program",color:"#DC2626",icon:"⚡"});
  var wic=1.85*f, wicOK=(e.isPregnant||e.childrenUnder5)&&e.grossMonthlyIncome<=wic;
  if(e.isPregnant||e.childrenUnder5) out.push({program:"WIC (Nutrition)",slug:"wic",eligible:wicOK,reason:wicOK?"Pregnant/young child household meets 185% FPL income limit":"Income exceeds 185% FPL ($"+Math.round(wic)+"/mo) for WIC",monthly:wicOK?50:0,
    estimatedBenefit:wicOK?"~$50/month in healthy food benefits":"Not eligible",applyUrl:"https://www.floridawic.org/",color:"#DB2777",icon:"🥛"});
  var tanf=0.38*f, tanfOK=e.hasChildren&&e.grossMonthlyIncome<=tanf;
  if(e.hasChildren) out.push({program:"TANF (Cash Assistance)",slug:"tanf",eligible:tanfOK,reason:tanfOK?"Family with children meets Florida's very low 38% FPL limit":"Income $"+e.grossMonthlyIncome+"/mo exceeds Florida's very restrictive $"+Math.round(tanf)+"/mo TANF limit",monthly:tanfOK?303:0,
    estimatedBenefit:tanfOK?"Up to $303/month for family of 3":"Not eligible",applyUrl:"https://www.myflorida.com/accessflorida/",color:"#EA580C",icon:"💵"});
  var kcOK=e.hasChildren&&e.grossMonthlyIncome<=KIDCARE/100*f;
  if(e.hasChildren) out.push({program:"Florida KidCare",slug:"kidcare",eligible:kcOK,reason:kcOK?"Children likely qualify for Medicaid or KidCare (Florida covers children up to 215% FPL)":"Income may be too high — check KidCare directly",monthly:0,
    estimatedBenefit:kcOK?"Low-cost child health insurance ($0–$20/month)":"May still qualify — check floridakidcare.org",applyUrl:"https://www.floridakidcare.org/",color:"#0891B2",icon:"👶"});
  var llOK=e.grossMonthlyIncome<=1.35*f||s.eligible;
  out.push({program:"Lifeline (Phone/Internet)",slug:"lifeline",eligible:llOK,reason:llOK?"Qualifies through income or enrollment in SNAP/Medicaid":"Does not meet income or program requirements",monthly:llOK?9.25:0,
    estimatedBenefit:llOK?"$9.25/month off phone or internet":"Not eligible",applyUrl:"https://www.lifelinesupport.org/",color:"#059669",icon:"📱"});
  var key=e.numChildren>=3?"threeOrMore":e.numChildren===2?"twoChildren":e.numChildren===1?"oneChild":"noChildren";
  var lim=e.isMarried?EITC_MARRIED[key]:EITC_SINGLE[key], eOK=e.annualIncome<=lim&&e.annualIncome>0;
  out.push({program:"EITC (Tax Credit)",slug:"eitc",eligible:eOK,reason:eOK?"Annual income qualifies for Earned Income Tax Credit":"Income too high or zero income for EITC",monthly:0,
    estimatedBenefit:eOK?"Up to $"+EITC_MAX[key].toLocaleString()+" back on your taxes":"Not eligible",applyUrl:"https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit",color:"#7C3AED",icon:"💰"});
  return out;
}
window.FBC={checkAll:checkAll,fplMonthly:fplMonthly,SNAP:SNAP};

/* ---------- helpers ---------- */
function h(tag,attrs,children){var el=document.createElement(tag);if(attrs)for(var k in attrs){if(k==="style")el.setAttribute("style",attrs[k]);else if(k==="class")el.className=attrs[k];else if(k.indexOf("on")===0)el.addEventListener(k.slice(2),attrs[k]);else el.setAttribute(k,attrs[k]);}
  (children||[]).forEach(function(c){if(c==null)return;el.appendChild(typeof c==="string"?document.createTextNode(c):c);});return el;}
function sumValue(results){return Math.round(results.filter(function(r){return r.eligible;}).reduce(function(a,r){return a+(r.monthly||0);},0));}

/* ---------- checker widget ---------- */
function mountChecker(root){
  var STEPS=["Household","Income","Details","Results"];
  var st={step:0,data:{householdSize:2,grossMonthlyIncome:0,hasChildren:false,childrenUnder5:false,isPregnant:false,isDisabled:false,hasElderly:false,age:35,isMarried:false,assets:0,isCitizen:true,numChildren:0},results:[]};
  var G_BLUE="linear-gradient(135deg, #0E4D91, #1565C0)", G_ORANGE="linear-gradient(135deg, #F97316, #EF4444)", G_GREEN="linear-gradient(135deg, #10B981, #059669)";
  function set(k,v){st.data[k]=v;render();}
  function stepper(){
    var wrap=h("div",{class:"flex items-center justify-center mb-8 gap-0"});
    STEPS.forEach(function(lab,i){
      var circle=h("div",{class:"w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all "+(i<st.step?"bg-green-500 text-white":i===st.step?"text-white shadow-lg":"bg-slate-200 text-slate-500"),style:i===st.step?"background:"+G_BLUE:""},[i<st.step?"✓":String(i+1)]);
      var col=h("div",{class:"flex flex-col items-center"},[circle,h("span",{class:"text-xs mt-1 font-medium "+(i===st.step?"text-blue-700":"text-slate-400")},[lab])]);
      var item=h("div",{class:"flex items-center"},[col]);
      if(i<STEPS.length-1) item.appendChild(h("div",{class:"h-0.5 w-10 sm:w-16 mx-1 mb-5 transition-all "+(i<st.step?"bg-green-500":"bg-slate-200")}));
      wrap.appendChild(item);
    });return wrap;
  }
  function btn(label,bg,onclick,cls){return h("button",{type:"button",class:cls||"w-full py-4 rounded-xl text-white font-bold text-lg transition-all hover:opacity-90 hover:shadow-lg",style:"background:"+bg,onclick:onclick},[label]);}
  function back(to){return h("button",{type:"button",class:"flex-1 py-4 rounded-xl border-2 border-slate-200 text-slate-700 font-semibold hover:bg-slate-50",onclick:function(){st.step=to;render();}},["← Back"]);}
  function step0(){
    var grid=h("div",{class:"grid grid-cols-4 gap-3 mb-6"});
    [1,2,3,4,5,6,7,8].forEach(function(n){var sel=st.data.householdSize===n;
      grid.appendChild(h("button",{type:"button","aria-pressed":String(sel),class:"py-4 rounded-xl font-bold text-lg transition-all border-2 "+(sel?"text-white shadow-lg scale-105 border-blue-700":"border-slate-200 text-slate-700 hover:border-blue-300 hover:bg-blue-50"),style:sel?"background:"+G_BLUE:"",onclick:function(){set("householdSize",n);}},[String(n)+(n===8?"+":"")]));});
    return h("div",null,[h("h2",{class:"text-2xl font-bold text-slate-900 mb-1"},["How many people live in your household?"]),h("p",{class:"text-slate-500 text-sm mb-6"},["Include yourself, your spouse, and any children you support"]),grid,btn("Continue →",G_ORANGE,function(){st.step=1;render();})]);
  }
  function step1(){
    var inp=h("input",{type:"number",min:"0",max:"20000",placeholder:"0",value:st.data.grossMonthlyIncome||"",class:"w-full pl-10 pr-4 py-5 text-2xl font-bold border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:outline-none","aria-label":"Monthly household income in dollars",oninput:function(ev){st.data.grossMonthlyIncome=parseInt(ev.target.value,10)||0;rng.value=st.data.grossMonthlyIncome;}});
    var rng=h("input",{type:"range",min:"0",max:"8000",step:"50",value:st.data.grossMonthlyIncome,class:"w-full accent-blue-700","aria-label":"Income slider",oninput:function(ev){st.data.grossMonthlyIncome=parseInt(ev.target.value,10);inp.value=st.data.grossMonthlyIncome;}});
    var box=h("div",{class:"mb-6"},[h("div",{class:"relative mb-4"},[h("span",{class:"absolute left-4 top-1/2 -translate-y-1/2 text-2xl font-bold text-slate-400"},["$"]),inp,h("span",{class:"absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 text-sm"},["/month"])]),rng,
      h("div",{class:"flex justify-between text-xs text-slate-400 mt-1"},[h("span",null,["$0"]),h("span",null,["$2,000"]),h("span",null,["$4,000"]),h("span",null,["$6,000"]),h("span",null,["$8,000+"])])]);
    return h("div",null,[h("h2",{class:"text-2xl font-bold text-slate-900 mb-1"},["What is your household's total monthly income?"]),h("p",{class:"text-slate-500 text-sm mb-6"},["Include wages, Social Security, child support, and any other income. Enter $0 if no income."]),box,
      h("div",{class:"flex gap-3"},[back(0),btn("Continue →",G_ORANGE,function(){st.step=2;render();},"flex-1 py-4 rounded-xl text-white font-bold transition-all hover:opacity-90")])]);
  }
  function step2(){
    var opts=[["hasChildren","👶 You have children under 18 in your household"],["childrenUnder5","🍼 You have children under 5 years old"],["isPregnant","🤰 You or someone in your household is pregnant"],["isDisabled","♿ You or someone has a disability"],["hasElderly","👴 Someone in your household is 60 or older"],["isCitizen","🇺🇸 You are a US citizen or qualified immigrant"]];
    var list=h("div",{class:"space-y-4"});
    opts.forEach(function(o){var k=o[0],on=!!st.data[k];
      var cb=h("input",{type:"checkbox",class:"w-5 h-5 accent-blue-700",onchange:function(ev){st.data[k]=ev.target.checked;if(k==="hasChildren")st.data.numChildren=ev.target.checked?Math.max(1,st.data.numChildren):0;render();}});cb.checked=on;
      list.appendChild(h("label",{class:"flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all hover:bg-blue-50 hover:border-blue-300",style:on?"border-color:#0E4D91;background:#EFF6FF":""},[cb,h("span",{class:"text-sm font-medium text-slate-700"},[o[1]])]));});
    if(st.data.hasChildren){
      var nc=h("input",{type:"number",min:"1",max:"10",value:st.data.numChildren||1,class:"w-full p-3 border border-slate-200 rounded-lg text-lg font-semibold focus:border-blue-500 focus:outline-none",oninput:function(ev){st.data.numChildren=parseInt(ev.target.value,10)||1;}});
      list.appendChild(h("div",{class:"p-4 rounded-xl border-2 border-slate-200"},[h("label",{class:"text-sm font-medium text-slate-700 block mb-2"},["How many children (for the tax-credit estimate)"]),nc]));
    }
    var age=h("input",{type:"number",min:"18",max:"100",value:st.data.age,class:"w-full p-3 border border-slate-200 rounded-lg text-lg font-semibold focus:border-blue-500 focus:outline-none",oninput:function(ev){st.data.age=parseInt(ev.target.value,10)||18;}});
    list.appendChild(h("div",{class:"p-4 rounded-xl border-2 border-slate-200"},[h("label",{class:"text-sm font-medium text-slate-700 block mb-2"},["Your age"]),age]));
    return h("div",null,[h("h2",{class:"text-2xl font-bold text-slate-900 mb-1"},["Tell us a little more"]),h("p",{class:"text-slate-500 text-sm mb-6"},["This helps us check all programs you may qualify for"]),list,
      h("div",{class:"flex gap-3 mt-6"},[back(1),btn("✓ Check My Benefits",G_GREEN,function(){var d=Object.assign({},st.data,{annualIncome:12*st.data.grossMonthlyIncome});st.results=checkAll(d);st.step=3;render();},"flex-1 py-4 rounded-xl text-white font-bold text-lg transition-all hover:opacity-90 hover:shadow-lg")])]);
  }
  function card(r){
    var kids=[h("div",{class:"flex items-center gap-2 mb-1 flex-wrap"},[h("h3",{class:"font-bold text-slate-900 text-sm"},[r.program]),r.eligible?h("span",{class:"text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold"},["✓ Likely Eligible"]):h("span",{class:"text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full"},["Not Eligible"])])];
    if(r.eligible) kids.push(h("p",{class:"text-sm font-semibold mb-1",style:"color:"+r.color},[r.estimatedBenefit]));
    kids.push(h("p",{class:"text-xs text-slate-500 leading-relaxed"},[r.reason]));
    if(r.eligible) kids.push(h("a",{href:r.applyUrl,target:"_blank",rel:"noopener noreferrer",class:"inline-block mt-2 text-xs font-semibold text-white px-3 py-1.5 rounded-lg transition-all hover:opacity-90",style:"background-color:"+r.color},["Apply Now →"]));
    return h("div",{class:"rounded-xl p-4 border-l-4 transition-all "+(r.eligible?"bg-white border-green-500 shadow-md hover-lift":"bg-slate-50 border-slate-200 opacity-75")},[h("div",{class:"flex items-start gap-3"},[h("span",{class:"text-2xl","aria-hidden":"true"},[r.icon]),h("div",{class:"flex-1 min-w-0"},kids)])]);
  }
  function step3(){
    var n=st.results.filter(function(r){return r.eligible;}).length, val=sumValue(st.results);
    var top=n>0?h("div",{class:"text-center mb-6 p-5 rounded-xl text-white",style:"background:"+G_GREEN},[h("div",{class:"text-4xl mb-2"},["🎉"]),h("h2",{class:"text-2xl font-bold mb-1"},["You likely qualify for "+n+" program"+(n!==1?"s":"")+"!"]),val>0?h("p",{class:"text-green-100"},["Estimated recurring value: about ",h("strong",null,["$"+val.toLocaleString()+"/month"])]):null,
        (function(){var x=[];st.results.forEach(function(r){if(r.eligible&&r.slug==="eitc")x.push("an EITC refund at tax time");if(r.eligible&&r.slug==="liheap")x.push("one-time LIHEAP energy help");if(r.eligible&&(r.slug==="medicaid"||r.slug==="kidcare"))x.push("health coverage");});
          return x.length?h("p",{class:"text-green-100 text-sm mt-1"},["Plus "+x.filter(function(v,i){return x.indexOf(v)===i;}).join(", ")+"."]):null;})()])
      :h("div",{class:"text-center mb-6 p-5 rounded-xl bg-slate-100"},[h("div",{class:"text-4xl mb-2"},["🔍"]),h("h2",{class:"text-xl font-bold text-slate-700 mb-1"},["Based on what you entered, you may not qualify"]),h("p",{class:"text-slate-500 text-sm"},["Income limits change — use the tools below to explore options"])]);
    var list=h("div",{class:"space-y-3 mb-6"},st.results.map(card));
    return h("div",null,[top,list,h("div",{class:"bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4"},[h("p",{class:"text-xs text-amber-800"},[h("strong",null,["Important:"])," These results are estimates only. Actual eligibility is determined by official program staff. Always apply directly through the official links above. This tool does NOT collect or store any personal data."])]),
      h("button",{type:"button",class:"w-full py-3 rounded-xl border-2 border-slate-200 text-slate-700 font-semibold hover:bg-slate-50",onclick:function(){st.step=0;st.results=[];render();}},["← Start Over"])]);
  }
  function render(){root.innerHTML="";root.appendChild(stepper());root.appendChild([step0,step1,step2,step3][st.step]());if(st.step===3)root.scrollIntoView({behavior:"smooth",block:"start"});}
  render();
}

/* ---------- income cliff ---------- */
function mountCliff(root){
  var G_BLUE="linear-gradient(135deg, #0E4D91, #1565C0)";
  var hh=root.querySelector("[data-hh]"),cur=root.querySelector("[data-cur]"),prop=root.querySelector("[data-prop]"),kids=root.querySelector("[data-kids]"),dis=root.querySelector("[data-dis]"),cit=root.querySelector("[data-cit]"),out=root.querySelector("[data-out]"),go=root.querySelector("[data-go]");
  function monthlyOf(results){return results.filter(function(r){return r.eligible;}).reduce(function(a,r){return a+(r.monthly||0);},0);}
  function run(){
    var n=parseInt(hh.value,10)||1,c=parseInt(cur.value,10)||0,p=parseInt(prop.value,10)||0;
    var base={householdSize:n,hasChildren:kids.checked,childrenUnder5:false,isPregnant:false,isDisabled:dis.checked,hasElderly:false,age:35,isMarried:false,assets:0,isCitizen:cit.checked,numChildren:kids.checked?1:0};
    var before=checkAll(Object.assign({},base,{grossMonthlyIncome:c,annualIncome:12*c})), after=checkAll(Object.assign({},base,{grossMonthlyIncome:p,annualIncome:12*p}));
    var bB=monthlyOf(before), bA=monthlyOf(after), raise=p-c, lost=bB-bA, net=raise-lost;
    var lostProgs=before.filter(function(r){return r.eligible;}).filter(function(r){var a=after.find(function(x){return x.slug===r.slug;});return !a||!a.eligible;});
    var reduced=before.filter(function(r){return r.eligible&&r.monthly;}).filter(function(r){var a=after.find(function(x){return x.slug===r.slug;});return a&&a.eligible&&a.monthly<r.monthly;});
    var good=net>=0;
    out.innerHTML="";
    out.appendChild(h("div",{class:"rounded-2xl p-6 text-white mb-4",style:"background:"+(good?"linear-gradient(135deg, #10B981, #059669)":"linear-gradient(135deg, #EF4444, #DC2626)")},[
      h("div",{class:"text-4xl mb-2"},[good?"✅":"⚠️"]),
      h("h2",{class:"text-2xl font-bold mb-1"},[good?"This raise helps you — take it.":"Careful: this raise could cost you more than it pays."]),
      h("p",{class:"text-white text-opacity-90"},["Raise: +$"+raise.toLocaleString()+"/mo • Estimated benefits lost: −$"+Math.max(0,lost).toLocaleString()+"/mo • ",h("strong",null,["Net monthly change: "+(net>=0?"+":"−")+"$"+Math.abs(net).toLocaleString()])])]));
    var rows=h("div",{class:"grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4 text-center"},[
      h("div",{class:"bg-slate-50 rounded-xl p-4"},[h("div",{class:"text-xs text-slate-500"},["Benefits now"]),h("div",{class:"font-bold text-slate-900 text-xl"},["$"+bB.toLocaleString()+"/mo"])]),
      h("div",{class:"bg-slate-50 rounded-xl p-4"},[h("div",{class:"text-xs text-slate-500"},["Benefits after raise"]),h("div",{class:"font-bold text-slate-900 text-xl"},["$"+bA.toLocaleString()+"/mo"])]),
      h("div",{class:"bg-slate-50 rounded-xl p-4"},[h("div",{class:"text-xs text-slate-500"},["Programs you'd lose"]),h("div",{class:"font-bold text-slate-900 text-xl"},[String(lostProgs.length)])])]);
    out.appendChild(rows);
    if(lostProgs.length||reduced.length){
      var ul=h("ul",{class:"space-y-2 text-sm text-slate-700 mb-4"});
      lostProgs.forEach(function(r){ul.appendChild(h("li",null,["❌ You would no longer qualify for ",h("strong",null,[r.program])," (",r.estimatedBenefit,")"]));});
      reduced.forEach(function(r){var a=after.find(function(x){return x.slug===r.slug;});ul.appendChild(h("li",null,["📉 ",h("strong",null,[r.program])," would drop from $"+r.monthly+" to $"+a.monthly+"/mo"]));});
      out.appendChild(h("div",{class:"bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4"},[h("h3",{class:"font-bold text-amber-900 mb-2 text-sm"},["What changes"]),ul]));
    }
    out.appendChild(h("p",{class:"text-xs text-slate-500"},["Estimates use 2026 Florida thresholds. Medicaid, KidCare and EITC are counted as eligibility (not dollars), so real losses can be larger — losing health coverage is often the biggest cliff. Confirm with the agency before changing hours."]));
    out.style.display="block";out.scrollIntoView({behavior:"smooth",block:"start"});
  }
  go.addEventListener("click",run);
}

/* ---------- document checklist ---------- */
var DOCS={
 common:{title:"Documents every Florida application needs",items:["Photo ID (driver license, state ID, passport) for the applicant","Social Security numbers for everyone applying","Proof of Florida residence (lease, utility bill, mail with your address)","Proof of ALL income for the last 4 weeks (pay stubs, award letters, child support)","Proof of citizenship or qualified immigration status (birth certificate, naturalization papers, I-94/green card)"]},
 snap:{title:"🛒 SNAP (Food Stamps) — extra documents",items:["Rent or mortgage statement and utility bills (these raise your benefit via deductions)","Child-care or dependent-care costs","Medical expenses over $35/mo if anyone is 60+ or disabled","Court-ordered child support you PAY","Bank statements if DCF asks about resources"]},
 medicaid:{title:"🏥 Florida Medicaid — extra documents",items:["Proof of pregnancy if applying for pregnancy Medicaid","Current health insurance cards/policies (if any)","Proof of disability or age 65+ for aged/disabled Medicaid","Proof of assets for aged/disabled categories (bank, vehicles, property)"]},
 ssi:{title:"♿ SSI — extra documents",items:["Birth certificate or proof of age","Medical records, doctor/hospital names, dates of treatment, medication list","Work history for the last 15 years and most recent W-2 or tax return","Bank statements, life insurance, vehicle titles, deeds (SSI resource limit $2,000 / $3,000 couple)","Proof of living arrangement and what you pay for rent/food"]},
 liheap:{title:"⚡ LIHEAP — extra documents",items:["Your current electric or gas bill (account must be in a household member's name)","Disconnect/shut-off notice if applying for crisis help","Proof of income for the last 30 days for all household members","Proof of SNAP/TANF/SSI enrollment if you have it (speeds approval)"]},
 wic:{title:"🥛 WIC — extra documents",items:["Proof of pregnancy, or the child's birth certificate/immunization record","Proof of income OR your Medicaid/SNAP/TANF card (automatically income-eligible)","Proof of identity for each child applying","Bring each infant/child to the first appointment for a quick health check"]},
 kidcare:{title:"👶 Florida KidCare — extra documents",items:["Each child's birth certificate or proof of age","Each child's Social Security number","Proof of household income (last 4 weeks of pay stubs or last year's tax return)","Proof of the child's citizenship or immigration status","Current insurance information if the child has any coverage"]}
};
function mountDocs(root){
  var boxes=root.querySelectorAll("input[data-prog]"),go=root.querySelector("[data-go]"),out=root.querySelector("[data-out]");
  function sync(){var any=Array.prototype.some.call(boxes,function(b){return b.checked;});go.disabled=!any;boxes.forEach(function(b){b.closest("label").style.borderColor=b.checked?"#16A34A":"#E2E8F0";b.closest("label").style.background=b.checked?"#F0FDF4":"";});}
  boxes.forEach(function(b){b.addEventListener("change",sync);});sync();
  go.addEventListener("click",function(){
    var sel=Array.prototype.filter.call(boxes,function(b){return b.checked;}).map(function(b){return b.getAttribute("data-prog");});
    out.innerHTML="";
    function section(d){var ul=h("ul",{class:"space-y-2"});d.items.forEach(function(t){var cb=h("input",{type:"checkbox",class:"w-4 h-4 accent-green-600 mt-0.5"});ul.appendChild(h("li",{class:"flex items-start gap-2 text-sm text-slate-700"},[cb,h("span",null,[t])]));});return h("div",{class:"bg-white rounded-2xl p-5 border border-slate-100 shadow-sm mb-4"},[h("h3",{class:"font-bold text-slate-900 mb-3"},[d.title]),ul]);}
    out.appendChild(section(DOCS.common));sel.forEach(function(s){if(DOCS[s])out.appendChild(section(DOCS[s]));});
    out.appendChild(h("div",{class:"flex gap-3 no-print"},[h("button",{type:"button",class:"flex-1 py-3 rounded-xl text-white font-semibold",style:"background:linear-gradient(135deg, #16A34A, #15803D)",onclick:function(){window.print();}},["🖨️ Print this checklist"])]));
    out.appendChild(h("p",{class:"text-xs text-slate-500 mt-3"},["Tip: upload documents in your MyACCESS account or bring copies to your DCF office. Missing documents are the #1 reason Florida applications are delayed."]));
    out.style.display="block";out.scrollIntoView({behavior:"smooth",block:"start"});
  });
}


/* ---------- SNAP benefit calculator (FY2027 rules, eff. Oct 1 2026) ---------- */
var SNAP_STD={1:217,2:217,3:217,4:229,5:268}; function stdDed(n){return n>=6?308:SNAP_STD[n];}
var SHELTER_CAP=769, SNAP_MIN=25;
function snapEstimate(i){
  var n=Math.min(Math.max(i.hh,1),8), t=SNAP[n], f=fplMonthly(i.hh);
  var gross=i.earned+i.unearned, ed=!!i.elderlyDisabled;
  var steps=[];
  if(!ed && gross>t.g) return {eligible:false,amount:0,reason:"Gross income $"+gross.toLocaleString()+"/mo is above Florida's 200% FPL limit of $"+t.g.toLocaleString()+" for "+i.hh+(i.hh>1?" people":" person")+".",steps:steps};
  var earnDed=Math.round(0.2*i.earned), sd=stdDed(n), med=ed?Math.max(0,i.medical-35):0;
  var adj=Math.max(0,gross-earnDed-sd-i.care-i.support-med);
  steps.push(["Gross monthly income","$"+gross.toLocaleString()]);
  steps.push(["− 20% earned-income deduction","$"+earnDed.toLocaleString()]);
  steps.push(["− Standard deduction (FY2027)","$"+sd]);
  if(i.care) steps.push(["− Dependent-care costs","$"+i.care.toLocaleString()]);
  if(i.support) steps.push(["− Child support paid","$"+i.support.toLocaleString()]);
  if(med) steps.push(["− Medical costs over $35 (60+/disabled)","$"+med.toLocaleString()]);
  steps.push(["= Adjusted income","$"+adj.toLocaleString()]);
  var shelter=i.rent+i.util, excess=Math.max(0,shelter-Math.round(adj/2)); if(!ed) excess=Math.min(excess,SHELTER_CAP);
  steps.push(["− Excess shelter deduction"+(ed?" (no cap: 60+/disabled)":" (cap $"+SHELTER_CAP+")"),"$"+excess.toLocaleString()]);
  var net=Math.max(0,adj-excess); steps.push(["= Net monthly income","$"+net.toLocaleString()]);
  if(net>t.n) return {eligible:false,amount:0,reason:"Net income $"+net.toLocaleString()+"/mo is above the 100% FPL net limit of $"+t.n.toLocaleString()+".",steps:steps};
  var amt=t.max-Math.ceil(0.3*net);
  steps.push(["Max allotment − 30% of net income","$"+t.max+" − $"+Math.ceil(0.3*net)]);
  if(n<=2) amt=Math.max(SNAP_MIN,amt);
  if(amt<=0) return {eligible:false,amount:0,reason:"You pass the income tests, but 30% of your net income is more than the maximum benefit, so the estimate is $0.",steps:steps};
  return {eligible:true,amount:amt,reason:"",steps:steps,max:t.max};
}
window.FBC.snapEstimate=snapEstimate;
function mountSnapCalc(root){
  var q=function(s){return root.querySelector(s);}, out=q("[data-out]");
  function num(s){return Math.max(0,parseFloat(q(s).value)||0);}
  q("[data-go]").addEventListener("click",function(){
    var r=snapEstimate({hh:parseInt(q("[data-hh]").value,10),earned:num("[data-earned]"),unearned:num("[data-unearned]"),rent:num("[data-rent]"),util:num("[data-util]"),care:num("[data-care]"),support:num("[data-support]"),medical:num("[data-medical]"),elderlyDisabled:q("[data-ed]").checked});
    out.innerHTML="";
    out.appendChild(h("div",{class:"rounded-2xl p-6 text-white mb-4",style:"background:"+(r.eligible?"linear-gradient(135deg, #16A34A, #15803D)":"linear-gradient(135deg, #64748B, #475569)")},[
      h("div",{class:"text-sm font-semibold mb-1"},["Estimated monthly SNAP benefit"]),
      h("div",{class:"text-4xl font-bold mb-1"},["$"+r.amount.toLocaleString()+"/month"]),
      h("p",{class:"text-sm"},[r.eligible?"Paid on your EBT card each month. Maximum for your household: $"+r.max.toLocaleString()+".":r.reason])]));
    if(r.steps.length){var tb=h("table",{class:"w-full text-sm"},[]);r.steps.forEach(function(s,k){tb.appendChild(h("tr",{class:k%2?"bg-slate-50":"bg-white"},[h("td",{class:"px-4 py-2"},[s[0]]),h("td",{class:"px-4 py-2 text-right font-semibold"},[s[1]])]));});
      out.appendChild(h("div",{class:"rounded-2xl border border-slate-100 overflow-x-auto mb-4"},[tb]));}
    out.appendChild(h("p",{class:"text-xs text-slate-500"},["Estimate using FY2027 USDA rules effective October 1, 2026. Florida DCF makes the final determination — apply at MyACCESS Florida to get your exact amount."]));
    out.appendChild(h("a",{href:"https://www.myflorida.com/accessflorida/",target:"_blank",rel:"noopener noreferrer",class:"inline-block mt-3 text-white font-semibold px-5 py-3 rounded-xl",style:"background:linear-gradient(135deg, #F97316, #EF4444)"},["Apply on MyACCESS Florida →"]));
    out.style.display="block";out.scrollIntoView({behavior:"smooth",block:"start"});
  });
}

/* ---------- boot ---------- */
document.addEventListener("DOMContentLoaded",function(){
  document.querySelectorAll("[data-fbc-checker]").forEach(mountChecker);
  document.querySelectorAll("[data-fbc-cliff]").forEach(mountCliff);
  document.querySelectorAll("[data-fbc-docs]").forEach(mountDocs);
  document.querySelectorAll("[data-fbc-snapcalc]").forEach(mountSnapCalc);
});
})();

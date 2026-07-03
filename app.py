"""
CardTick — search site + price API.
RUN:  pip install flask requests  ->  python app.py  ->  http://localhost:5000
Data: pokemontcg.io (free).
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
POKEMON_API = "https://api.pokemontcg.io/v2/cards"
API_KEY = "7f5dd6b6-45b1-42c8-ab83-83a95f8a9f48"  # optional free key from https://dev.pokemontcg.io


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CardTick</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{--ink:#0B0E14;--panel:#121724;--panel2:#0F1420;--line:rgba(255,255,255,.08);
    --text:#E7ECF6;--mute:#7C879E;--teal:#36E2C6;--gold:#F4B43C;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--ink);color:var(--text);font-family:'Inter',system-ui,sans-serif;
    -webkit-font-smoothing:antialiased;padding:30px 16px 70px;position:relative;min-height:100vh;}
  /* ambient background art */
  body::before{content:"";position:fixed;inset:0;z-index:-2;background:
    radial-gradient(720px 520px at 8% 4%, rgba(54,226,198,.20), transparent 62%),
    radial-gradient(760px 600px at 92% 96%, rgba(244,180,60,.17), transparent 62%),
    radial-gradient(560px 560px at 80% 10%, rgba(120,90,255,.14), transparent 60%),
    radial-gradient(600px 500px at 20% 90%, rgba(120,90,255,.10), transparent 60%),
    var(--ink);}
  body::after{content:"";position:fixed;inset:0;z-index:-1;opacity:.5;pointer-events:none;
    background-image:radial-gradient(rgba(255,255,255,.045) 1px, transparent 1px);background-size:26px 26px;}
  .ghost{position:fixed;z-index:-1;border-radius:14px;border:1px solid rgba(255,255,255,.06);
    background:linear-gradient(150deg,rgba(54,226,198,.06),rgba(244,180,60,.05) 55%,transparent);
    box-shadow:inset 0 0 45px rgba(54,226,198,.05);opacity:.55;}
  .g1{width:155px;height:215px;left:-48px;top:33%;transform:rotate(13deg);}
  .g2{width:132px;height:184px;right:-40px;top:14%;transform:rotate(-15deg);}
  .g3{width:112px;height:156px;right:9%;bottom:-46px;transform:rotate(9deg);opacity:.35;}
  .g4{width:98px;height:136px;left:6%;bottom:5%;transform:rotate(-8deg);opacity:.32;}
  .spark{position:fixed;z-index:-1;width:4px;height:4px;border-radius:50%;background:var(--teal);
    box-shadow:0 0 9px 1px rgba(54,226,198,.55);opacity:.55;}
  .spark.gold{background:var(--gold);box-shadow:0 0 9px 1px rgba(244,180,60,.55);}
  #grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:14px;margin-top:16px;}
  .mini{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px;cursor:pointer;text-align:center;transition:transform .12s,border-color .12s;}
  .mini:hover{border-color:var(--teal);transform:translateY(-3px);}
  .mini img{width:100%;aspect-ratio:63/88;object-fit:cover;border-radius:8px;display:block;}
  .mini .mn{font-family:'Space Mono';font-size:11px;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .mini .mp{font-family:'Space Mono';font-size:12.5px;color:var(--gold);margin-top:3px;font-weight:700;}
  .ld{color:var(--mute);font-family:'Space Mono';font-size:13px;padding:10px 0;}
  #more{display:none;margin:24px auto 0;background:var(--panel);border:1px solid var(--line);color:var(--text);
    padding:12px 28px;border-radius:12px;font-family:'Space Grotesk';font-weight:600;font-size:14px;cursor:pointer;}
  #more:hover{border-color:var(--teal);color:var(--teal);}
  .groupgrid{display:flex;flex-direction:column;gap:12px;margin-top:14px;}
  .gbox{position:relative;height:78px;border-radius:16px;overflow:hidden;cursor:pointer;border:1px solid var(--line);background:var(--panel2);}
  .gbox .bg{position:absolute;inset:0;background-size:cover;background-position:center 28%;filter:blur(7px) brightness(.45);transform:scale(1.2);transition:filter .2s;}
  .gbox .lbl{position:absolute;inset:0;display:flex;align-items:center;justify-content:flex-start;padding-left:28px;
    font-family:'Space Grotesk';font-weight:700;font-size:22px;letter-spacing:.5px;z-index:1;text-shadow:0 2px 12px rgba(0,0,0,.85);}
  .gbox:hover{border-color:var(--teal);}
  .gbox:hover .bg{filter:blur(5px) brightness(.6);}
  @keyframes rgb{0%{filter:drop-shadow(0 0 12px #ff4d4d)}33%{filter:drop-shadow(0 0 12px #36e2c6)}66%{filter:drop-shadow(0 0 12px #7b5bff)}100%{filter:drop-shadow(0 0 12px #ff4d4d)}}
  .mascot{position:fixed;top:34%;width:190px;z-index:-1;opacity:.9;animation:rgb 5s linear infinite;}
  .mascot.l{left:3%}.mascot.r{right:3%;transform:scaleX(-1)}
  @media(max-width:1280px){.mascot{display:none}}

  .wrap{max-width:1120px;margin:0 auto;position:relative;}
  .brand{font-family:'Space Grotesk';font-weight:700;font-size:25px;letter-spacing:-.4px;display:flex;align-items:center;gap:9px;}
  .bolt{width:11px;height:20px;background:var(--gold);clip-path:polygon(55% 0,0 58%,42% 58%,30% 100%,100% 38%,55% 38%);display:inline-block;}
  .tagline{color:var(--mute);font-family:'Space Mono';font-size:12.5px;margin:6px 0 24px;}

  .searchwrap{position:relative;}
  .searchbar{display:flex;gap:10px;}
  input{flex:1;background:var(--panel);border:1px solid var(--line);color:var(--text);
    padding:15px 16px;border-radius:12px;font-size:15px;font-family:'Inter';}
  input:focus{outline:2px solid var(--teal);outline-offset:1px;border-color:transparent;}
  button{background:var(--gold);color:#1A1606;border:none;padding:15px 24px;border-radius:12px;
    font-family:'Space Grotesk';font-weight:600;font-size:15px;cursor:pointer;}
  button:active{transform:translateY(1px);}
  #suggest{position:absolute;left:0;right:96px;top:56px;background:var(--panel);border:1px solid var(--line);
    border-radius:12px;overflow:hidden;z-index:5;display:none;}
  #suggest div{padding:11px 15px;font-size:14px;cursor:pointer;border-top:1px solid var(--line);}
  #suggest div:first-child{border-top:none;}
  #suggest div:hover{background:var(--panel2);color:var(--teal);}

  .chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;}
  .chip{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:7px 14px;
    font-size:13px;color:var(--mute);cursor:pointer;font-family:'Space Mono';}
  .chip:hover{color:var(--teal);border-color:var(--teal);}
  .chips .lbl{color:var(--mute);font-family:'Space Mono';font-size:11px;letter-spacing:1px;text-transform:uppercase;align-self:center;margin-right:2px;}

  #status{color:var(--mute);font-family:'Space Mono';font-size:13px;margin-top:20px;}
  #result{display:none;margin-top:26px;}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px;
    display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start;}
  .card img{width:160px;border-radius:12px;flex-shrink:0;box-shadow:0 10px 34px rgba(0,0,0,.45);}
  .info{flex:1;min-width:200px;}
  .info .nm{font-family:'Space Grotesk';font-size:24px;font-weight:600;letter-spacing:-.4px;}
  .info .set{color:var(--mute);font-family:'Space Mono';font-size:13px;margin-top:5px;}
  .metas{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px;}
  .meta{font-family:'Space Mono';font-size:11px;color:var(--teal);border:1px solid var(--line);padding:3px 9px;border-radius:20px;}
  .price{font-family:'Space Mono';font-size:40px;font-weight:700;color:var(--gold);margin-top:16px;letter-spacing:-1px;}
  .price small{font-size:14px;color:var(--mute);font-weight:400;}
  .buy{display:inline-block;margin-top:14px;font-family:'Space Grotesk';font-size:13px;color:var(--ink);
    background:var(--teal);padding:9px 16px;border-radius:10px;text-decoration:none;font-weight:600;}
  .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px;}
  .stat{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;}
  .stat .k{font-family:'Space Mono';font-size:10px;color:var(--mute);letter-spacing:1px;text-transform:uppercase;}
  .stat .v{font-family:'Space Mono';font-size:19px;font-weight:700;margin-top:6px;}
  .chartcard{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:18px;margin-top:16px;}
  .chartcard .t{font-family:'Space Mono';font-size:11px;color:var(--mute);letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;}
  .demo{color:var(--mute);font-family:'Space Mono';font-size:11px;margin-top:10px;}
  @media(max-width:560px){ .stats{grid-template-columns:repeat(2,1fr);} }
</style></head>
<body>
<div class="ghost g1"></div><div class="ghost g2"></div><div class="ghost g3"></div><div class="ghost g4"></div>
<div class="spark" style="left:18%;top:22%"></div><div class="spark gold" style="left:82%;top:38%"></div>
<div class="spark" style="left:30%;top:72%"></div><div class="spark gold" style="left:66%;top:80%"></div>
<svg class="mascot l" viewBox="0 0 120 168" fill="none" stroke="#E7ECF6" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">
  <rect x="8" y="8" width="104" height="152" rx="12"/>
  <rect x="18" y="20" width="70" height="7" rx="3.5"/>
  <rect x="18" y="36" width="84" height="74" rx="6"/>
  <path d="M60 50 L66.5 70 L86 76 L66.5 82 L60 102 L53.5 82 L34 76 L53.5 70 Z"/>
  <circle cx="44" cy="56" r="1.6" fill="#E7ECF6" stroke="none"/>
  <circle cx="79" cy="94" r="1.6" fill="#E7ECF6" stroke="none"/>
  <rect x="18" y="122" width="60" height="6" rx="3"/>
  <rect x="18" y="134" width="44" height="6" rx="3"/>
</svg>
<svg class="mascot r" viewBox="0 0 120 168" fill="none" stroke="#E7ECF6" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">
  <rect x="8" y="8" width="104" height="152" rx="12"/>
  <rect x="18" y="20" width="70" height="7" rx="3.5"/>
  <rect x="18" y="36" width="84" height="74" rx="6"/>
  <path d="M60 50 L66.5 70 L86 76 L66.5 82 L60 102 L53.5 82 L34 76 L53.5 70 Z"/>
  <circle cx="44" cy="56" r="1.6" fill="#E7ECF6" stroke="none"/>
  <circle cx="79" cy="94" r="1.6" fill="#E7ECF6" stroke="none"/>
  <rect x="18" y="122" width="60" height="6" rx="3"/>
  <rect x="18" y="134" width="44" height="6" rx="3"/>
</svg>
<div class="wrap">
  <div class="brand"><span class="bolt"></span>CardTick</div>
  <div class="tagline">live Pokemon card prices</div>
  <div class="searchwrap">
    <div class="searchbar">
      <input id="q" placeholder="search a card... e.g. Charizard" autocomplete="off" />
      <button onclick="go()">Search</button>
    </div>
    <div id="suggest"></div>
  </div>
  <div class="chips" id="popular"><span class="lbl">popular</span></div>
  <div style="font-family:'Space Mono';font-size:11px;color:var(--mute);letter-spacing:1px;text-transform:uppercase;margin-top:22px">browse by type</div>
  <div class="groupgrid" id="groups"></div>
  <div id="gridhead" style="font-family:'Space Mono';font-size:11px;color:var(--mute);letter-spacing:1px;text-transform:uppercase;margin-top:26px;margin-bottom:2px"></div>
  <div id="grid"></div>
  <button id="more" onclick="loadMore()">Load more</button>
  <div id="status"></div>
  <div id="result">
    <div class="card">
      <img id="img" src="" alt="">
      <div class="info">
        <div class="nm" id="nm"></div>
        <div class="set" id="set"></div>
        <div class="metas" id="metas"></div>
        <div class="price" id="price"></div>
        <a class="buy" id="buy" href="#" target="_blank" style="display:none">View on TCGplayer</a>
      </div>
    </div>
    <div class="stats" id="stats"></div>
    <div class="chartcard">
      <div class="t">Price trend</div>
      <svg id="chart" viewBox="0 0 380 190" style="width:100%;height:auto;display:block"></svg>
      <div class="demo">dates span this card's release to now — price points are illustrative until we log real prices daily</div>
    </div>
  </div>
</div>
<script>
  const $ = id => document.getElementById(id);
  const pop=$('popular');
  ["Charizard","Pikachu","Umbreon","Mewtwo","Blastoise","Rayquaza"].forEach(n=>{
    const c=document.createElement('span'); c.className='chip'; c.textContent=n;
    c.onclick=()=>{ $('q').value=n; go(); }; pop.appendChild(c);
  });
  const gwrap=$('groups');
  const glist=[["GX","gx"],["EX","ex"],["V","v"],["VMAX","vmax"],["VSTAR","vstar"],["Tag Team","tagteam"],["Full Art","fullart"],["Trainer","trainer"]];
  const boxes=glist.map(g=>{ const box=document.createElement('div'); box.className='gbox';
    box.innerHTML='<div class="bg"></div><div class="lbl">'+g[0]+'</div>';
    box.onclick=()=>browse(g[1]); gwrap.appendChild(box); return [box,g[1]]; });
  (async()=>{ for(const bg of boxes){ try{ const r=await fetch('/thumb?group='+bg[1]); const j=await r.json();
    if(j.image) bg[0].querySelector('.bg').style.backgroundImage='url('+j.image+')'; }catch(e){} } })();
  browse('featured');
  const GLABEL={featured:"Latest cards",gx:"GX cards",ex:"EX cards",v:"V cards",vmax:"VMAX cards",vstar:"VSTAR cards",tagteam:"Tag Team cards",fullart:"Full Art cards",trainer:"Trainer cards"};
  let curGroup='featured', curPage=1;
  function addCards(cards){
    const grid=$('grid');
    cards.forEach(c=>{
      const d=document.createElement('div'); d.className='mini';
      const img=document.createElement('img'); img.src=c.image; img.loading='lazy'; img.alt=c.name;
      const mn=document.createElement('div'); mn.className='mn'; mn.textContent=c.name;
      const mp=document.createElement('div'); mp.className='mp'; mp.textContent=c.market?'$'+c.market:'';
      d.append(img,mn,mp);
      d.onclick=()=>{ $('q').value=c.name; window.scrollTo({top:0,behavior:'smooth'}); go(); };
      grid.appendChild(d);
    });
  }
  async function browse(key){
    curGroup=key; curPage=1; $('gridhead').textContent=GLABEL[key]||'';
    $('result').style.display='none'; $('status').textContent=''; $('more').style.display='none';
    const grid=$('grid'); grid.innerHTML='<div class="ld">loading...</div>';
    try{ const r=await fetch('/browse?group='+key+'&page=1'); const cards=await r.json();
      grid.innerHTML=''; addCards(cards);
      $('more').style.display=cards.length>=20?'block':'none';
    }catch(e){ grid.innerHTML=''; }
  }
  async function loadMore(){
    curPage++; $('more').textContent='Loading...';
    try{ const r=await fetch('/browse?group='+curGroup+'&page='+curPage); const cards=await r.json();
      addCards(cards); $('more').style.display=cards.length>=20?'block':'none';
    }catch(e){} $('more').textContent='Load more';
  }
  $('q').addEventListener('keydown', e=>{ if(e.key==='Enter'){ hideSug(); go(); } });
  let t;
  $('q').addEventListener('input',()=>{
    clearTimeout(t); const v=$('q').value.trim();
    if(v.length<2){ hideSug(); return; }
    t=setTimeout(async()=>{
      try{ const r=await fetch('/suggest?q='+encodeURIComponent(v)); const names=await r.json();
        if(!names.length){ hideSug(); return; }
        const s=$('suggest'); s.innerHTML='';
        names.forEach(n=>{ const d=document.createElement('div'); d.textContent=n;
          d.onclick=()=>{ $('q').value=n; hideSug(); go(); }; s.appendChild(d); });
        s.style.display='block';
      }catch(e){ hideSug(); }
    },220);
  });
  function hideSug(){ $('suggest').style.display='none'; }
  document.addEventListener('click', e=>{ if(!e.target.closest('.searchwrap')) hideSug(); });

  async function go(){
    const name=$('q').value.trim(); if(!name) return;
    $('status').textContent='searching...'; $('result').style.display='none';
    try{
      const res=await fetch('/price?name='+encodeURIComponent(name)); const d=await res.json();
      if(d.error){ $('status').textContent=d.error; return; }
      $('status').textContent='';
      $('img').src=d.image||''; $('nm').textContent=d.card||name;
      $('set').textContent=(d.set||'')+(d.number?' · #'+d.number:'');
      const metas=[]; if(d.rarity)metas.push(d.rarity); if(d.year)metas.push('released '+d.year); if(d.artist)metas.push('art: '+d.artist);
      $('metas').innerHTML=metas.map(m=>'<span class="meta">'+m+'</span>').join('');
      $('price').innerHTML=d.market?'$'+d.market+' <small>market</small>':'price unavailable';
      if(d.url){ $('buy').href=d.url; $('buy').style.display='inline-block'; } else $('buy').style.display='none';
      const stat=(k,v)=>'<div class="stat"><div class="k">'+k+'</div><div class="v">'+(v!=null?'$'+v:'—')+'</div></div>';
      $('stats').innerHTML=stat('Low',d.low)+stat('Market',d.market)+stat('High',d.high)+
        '<div class="stat"><div class="k">Variant</div><div class="v" style="font-size:12px;color:var(--teal)">'+(d.variant||'—')+'</div></div>';
      drawChart(d.market,d.year);
      $('result').style.display='block';
    }catch(e){ $('status').textContent='something went wrong, try again'; }
  }

  function drawChart(price,year){
    const svg=$('chart'); if(!price){ svg.innerHTML=''; return; }
    const W=380,H=190,L=38,R=12,T=14,B=26;
    let sy=parseInt(year)||2020; if(sy>2024) sy=2024;
    const ey=2026; let years=[]; for(let y=sy;y<=ey;y++) years.push(y);
    let v=price*0.55, pts=years.map(()=>{ v=v*(1+(Math.random()*0.12-0.035)); return v; });
    pts[pts.length-1]=price;
    const max=Math.max(...pts),min=Math.min(...pts);
    const x=i=>L+(i/(years.length-1))*(W-L-R);
    const y=val=>T+(1-((val-min)/((max-min)||1)))*(H-T-B);
    let line='M '+x(0)+' '+y(pts[0]); pts.forEach((p,i)=>line+=' L '+x(i)+' '+y(p));
    let area=line+' L '+x(years.length-1)+' '+(H-B)+' L '+x(0)+' '+(H-B)+' Z';
    let dots=pts.map((p,i)=>'<circle cx="'+x(i)+'" cy="'+y(p)+'" r="2.6" fill="#36E2C6"/>').join('');
    let step=years.length>8?2:1;
    let xl=years.map((yr,i)=> i%step===0?'<text x="'+x(i)+'" y="'+(H-8)+'" fill="#7C879E" font-size="9" font-family="monospace" text-anchor="middle">'+yr+'</text>':'').join('');
    const mid=(min+max)/2;
    let yl=[[max,y(max)],[mid,y(mid)],[min,y(min)]].map(a=>'<text x="4" y="'+(a[1]+3)+'" fill="#7C879E" font-size="9" font-family="monospace">$'+Math.round(a[0])+'</text>').join('');
    let last='<text x="'+x(years.length-1)+'" y="'+(y(price)-8)+'" fill="#F4B43C" font-size="10" font-family="monospace" text-anchor="end">$'+price+'</text>';
    svg.innerHTML='<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'+
      '<stop offset="0%" stop-color="#36E2C6" stop-opacity=".28"/>'+
      '<stop offset="100%" stop-color="#36E2C6" stop-opacity="0"/></linearGradient></defs>'+
      '<path d="'+area+'" fill="url(#g)"/><path d="'+line+'" fill="none" stroke="#36E2C6" stroke-width="2"/>'+
      dots+xl+yl+last;
  }
</script>
</body></html>"""


@app.route("/")
def home():
    return PAGE


@app.route("/suggest")
def suggest():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    headers = {"X-Api-Key": API_KEY} if API_KEY else {}
    try:
        r = requests.get(POKEMON_API, params={"q": f"name:{q}*", "pageSize": 8, "select": "name"},
                         headers=headers, timeout=8)
        names = [c.get("name") for c in r.json().get("data", [])]
    except Exception:
        return jsonify([])
    seen, out = set(), []
    for n in names:
        if n and n not in seen:
            seen.add(n); out.append(n)
    return jsonify(out[:6])


GROUPS = {
    "gx": "subtypes:GX", "ex": "subtypes:EX", "v": "subtypes:V",
    "vmax": "subtypes:VMAX", "vstar": "subtypes:VSTAR", "tagteam": 'subtypes:"TAG TEAM"',
    "fullart": 'rarity:"Rare Ultra"', "trainer": "supertype:Trainer",
}


@app.route("/thumb")
def thumb():
    group = request.args.get("group", "")
    q = "supertype:Pokémon" if group == "featured" else GROUPS.get(group)
    if not q:
        return jsonify({})
    headers = {"X-Api-Key": API_KEY} if API_KEY else {}
    try:
        r = requests.get(POKEMON_API, params={"q": q, "pageSize": 1, "orderBy": "-set.releaseDate"},
                         headers=headers, timeout=8)
        d = r.json().get("data", [])
    except Exception:
        return jsonify({})
    return jsonify({"image": (d[0].get("images") or {}).get("small") if d else None})


@app.route("/browse")
def browse():
    group = request.args.get("group", "")
    if group == "featured":
        q = "supertype:Pokémon"
    else:
        q = GROUPS.get(group)
    if not q:
        return jsonify([])
    page = request.args.get("page", "1")
    headers = {"X-Api-Key": API_KEY} if API_KEY else {}
    try:
        r = requests.get(POKEMON_API, params={"q": q, "pageSize": 40, "page": page, "orderBy": "-set.releaseDate"},
                         headers=headers, timeout=10)
        data = r.json().get("data", [])
    except Exception:
        return jsonify([])
    out = []
    for c in data:
        prices = ((c.get("tcgplayer") or {}).get("prices") or {})
        market = None
        for v in prices.values():
            if isinstance(v, dict) and v.get("market"):
                market = v["market"]; break
        if market is None:
            continue
        out.append({
            "name": c.get("name"),
            "image": (c.get("images") or {}).get("small"),
            "market": market,
        })
    return jsonify(out)


@app.route("/price")
def price():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "add ?name=CardName"}), 400
    headers = {"X-Api-Key": API_KEY} if API_KEY else {}
    try:
        r = requests.get(POKEMON_API, params={"q": f'name:"{name}"', "pageSize": 1},
                         headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception as e:
        return jsonify({"error": "data source unavailable", "detail": str(e)}), 502
    if not data:
        return jsonify({"error": f"no card found for '{name}'"}), 404

    card = data[0]
    tp = card.get("tcgplayer") or {}
    prices = tp.get("prices") or {}
    variant, p = None, {}
    for key, vals in prices.items():
        if isinstance(vals, dict) and vals.get("market"):
            variant, p = key, vals
            break
    if not variant and prices:
        variant = list(prices.keys())[0]
        p = prices[variant] or {}

    s = card.get("set") or {}
    release = s.get("releaseDate") or ""
    return jsonify({
        "card": card.get("name"),
        "set": s.get("name"),
        "number": card.get("number"),
        "rarity": card.get("rarity"),
        "artist": card.get("artist"),
        "year": release[:4] if release else None,
        "variant": variant,
        "market": p.get("market"),
        "low": p.get("low"),
        "high": p.get("high"),
        "url": tp.get("url"),
        "image": (card.get("images") or {}).get("large") or (card.get("images") or {}).get("small"),
        "source": "pokemontcg.io / tcgplayer",
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)

#!/usr/bin/env python3
"""Catalogo fotografico Wikimedia Commons: 30 fotografie HD per artista.
Non scarica immagini prive di licenza aperta e non dichiara raggiunta la quota se mancano risultati.
"""
import csv, html, json, pathlib, re, time, urllib.parse, urllib.request
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]
ARTISTS={
 "ville-valo-him-heartagram-italia":["Ville Valo","HIM band live"],
 "mylene-farmer-italia":["Mylène Farmer"],
 "sandra-music-italia":["Sandra Cretu singer"],
 "mesh-italia":["Mesh synthpop band Mark Hockings"],
 "assemblage23-italia":["Assemblage 23 Tom Shear"],
 "thebirthdaymassacre-italia":["The Birthday Massacre band"]
}
API="https://commons.wikimedia.org/w/api.php"
HEADERS={"User-Agent":"MusicArchivesItaliaResearch/1.0 (public Wikimedia metadata)"}
class Strip(HTMLParser):
 def __init__(self): super().__init__();self.s=[]
 def handle_data(self,d):self.s.append(d)
def plain(x):
 p=Strip();p.feed(x or "");return " ".join("".join(p.s).split())
def query(params):
 url=API+"?"+urllib.parse.urlencode({"action":"query","format":"json","formatversion":2,**params})
 req=urllib.request.Request(url,headers=HEADERS)
 with urllib.request.urlopen(req,timeout=35) as r:return json.load(r)
def search(term):
 results=[];cont={}
 for _ in range(4):
  data=query({"generator":"search","gsrsearch":term+" filetype:bitmap","gsrnamespace":6,"gsrlimit":50,
    "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","iiurlwidth":900,**cont})
  for p in data.get("query",{}).get("pages",[]):
   for i in p.get("imageinfo",[]):
    meta=i.get("extmetadata",{})
    def m(k):return plain(meta.get(k,{}).get("value",""))
    lic=m("LicenseShortName")
    if i.get("width",0)<1920 or i.get("height",0)<1080:continue
    if not re.search(r"CC[ -]?(BY|0)|public domain",lic,re.I):continue
    if m("NonFree").lower()=="true":continue
    results.append({"file":p["title"],"width":i["width"],"height":i["height"],
      "source":i.get("descriptionurl",""),"original":i.get("url",""),
      "preview":i.get("thumburl",i.get("url","")),"sha1":i.get("sha1",""),
      "author":m("Artist") or m("Attribution"),"license":lic,
      "license_url":meta.get("LicenseUrl",{}).get("value",""),"credit":m("Credit"),
      "restrictions":m("Restrictions"),"status":"candidato - verifica manuale"})
  cont=data.get("continue",{})
  if not cont:break
  time.sleep(.5)
 return results
def main():
 for slug,terms in ARTISTS.items():
  found=[];seen=set()
  for term in terms:
   try: candidates=search(term)
   except Exception as e:print(slug,term,"ERROR",e);continue
   for item in candidates:
    key=item["sha1"] or item["original"]
    if key in seen:continue
    seen.add(key);found.append(item)
   if len(found)>=30:break
  selected=found[:30]
  out=ROOT/slug/"fotografie";out.mkdir(parents=True,exist_ok=True)
  keys=["file","width","height","source","original","preview","sha1","author","license","license_url","credit","restrictions","status"]
  with (out/"catalogo.csv").open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(selected)
  (out/"catalogo.json").write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding="utf-8")
  cards="".join(f'<figure><a href="{html.escape(x["source"],quote=True)}"><img loading="lazy" src="{html.escape(x["preview"],quote=True)}" alt="{html.escape(x["file"],quote=True)}"></a><figcaption>{html.escape(x["author"])} · {html.escape(x["license"])} · {x["width"]}×{x["height"]} · <a href="{html.escape(x["source"],quote=True)}">Fonte e condizioni</a></figcaption></figure>' for x in selected)
  page=f'<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fotografie HD · {html.escape(slug)}</title><style>body{{background:#101115;color:#eee;font:16px system-ui;padding:3vw}}a{{color:#b9cfff}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}}figure{{margin:0;background:#222;padding:12px}}img{{width:100%;height:280px;object-fit:contain}}figcaption{{font-size:13px;line-height:1.6}}</style><a href="../">← Archivio</a><h1>Galleria fotografica HD</h1><p>{len(selected)} fotografie candidate su 30. Le licenze e i diritti di personalità vanno ricontrollati prima del riutilizzo. Le anteprime sono ospitate su Wikimedia Commons.</p><div class="grid">{cards}</div></html>'
  (out/"index.html").write_text(page,encoding="utf-8")
  print(slug,len(selected),"/30")
if __name__=="__main__":main()

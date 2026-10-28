"""Generate a dependency-free, script-free SVG from GitHub's public calendar."""
from html.parser import HTMLParser
from html import escape
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen
import random

ROOT = Path(__file__).resolve().parents[1]
class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.days = []; self.labels = {}; self.tip = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and a.get('data-date') and 'data-level' in a:
            self.days.append((a['data-date'], int(a['data-level']), a['id']))
        if tag == 'tool-tip': self.tip = a.get('for')
    def handle_data(self, data):
        if self.tip: self.labels[self.tip] = self.labels.get(self.tip, '') + data
    def handle_endtag(self, tag):
        if tag == 'tool-tip': self.tip = None

DEFS = '''<defs>
<symbol id="carrot" viewBox="0 0 24 32"><path d="M11 10Q0 2 5 1Q12 0 13 8Q12-2 17 0Q22 3 15 10Q25 2 24 8Q22 13 15 13" fill="#8cce79"/><path d="M6 11Q12 6 19 12L10 31Q8 34 7 29Z" fill="#ff9a45"/><path d="m7 16 5 2m1 4 3 1m-8 2 3 1" stroke="#df682d" stroke-width="1.5" stroke-linecap="round"/></symbol>
<symbol id="apple" viewBox="0 0 24 24"><path d="M12 8C1 1-2 17 7 22Q10 24 12 21Q18 26 22 16C26 5 18 3 12 8" fill="#ff7186"/><path d="m12 8 1-7" stroke="#b78359" stroke-width="2"/><path d="M13 5Q14-1 21 2Q19 7 13 5" fill="#97d984"/><path d="M6 10q-2 3-1 5" fill="none" stroke="#ffc5ce" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="orange" viewBox="0 0 24 24"><circle cx="12" cy="14" r="10" fill="#ffa54e"/><path d="M12 5Q14-1 22 2Q20 8 12 5" fill="#8cce79"/><path d="M5 11q-1 2-1 4" stroke="#ffdf99" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="lemon" viewBox="0 0 24 24"><path d="M2 18C-1 7 9-2 19 5L23 5L22 9C27 20 12 27 5 21L1 22Z" fill="#f8dc69"/><path d="M6 10q2-4 7-4" stroke="#fff3b8" stroke-width="2" fill="none" stroke-linecap="round"/></symbol>
<symbol id="berry" viewBox="0 0 24 24"><path d="M2 9Q1 3 12 6Q24 3 22 10Q20 18 12 24Q4 18 2 9" fill="#f46d8d"/><path d="m4 5 6 1 2-6 2 6 7-2-4 6-5-2-5 2Z" fill="#8cce79"/><path d="m6 12 1 2m5-2 1 2m5-2-1 2m-6 3 1 2" stroke="#ffe6a3" stroke-width="1.5"/></symbol>
<symbol id="grape" viewBox="0 0 24 24"><g fill="#b599ef"><circle cx="7" cy="9" r="5"/><circle cx="16" cy="9" r="5"/><circle cx="8" cy="16" r="4.5"/><circle cx="16" cy="16" r="4.5"/><circle cx="12" cy="21" r="3"/></g><path d="M12 5Q13-1 21 1Q19 7 12 5" fill="#8cce79"/></symbol>
<symbol id="melon" viewBox="0 0 24 24"><path d="M1 5H23Q23 24 12 24Q1 24 1 5" fill="#79ce9c"/><path d="M3 5H21Q20 20 12 21Q4 20 3 5" fill="#f97791"/><path d="m7 9 1 2m8-2-1 2m-3 4v2" stroke="#643c57" stroke-width="1.6" stroke-linecap="round"/></symbol>
<symbol id="cherry" viewBox="0 0 24 24"><path d="M5 15Q6 2 15 1Q12 8 19 16" fill="none" stroke="#8cce79" stroke-width="2"/><circle cx="5" cy="18" r="5" fill="#ff6c82"/><circle cx="19" cy="18" r="5" fill="#e8567f"/><path d="M14 2q5-4 10 1-5 5-10-1" fill="#8cce79"/></symbol>
<symbol id="pear" viewBox="0 0 24 24"><path d="M8 5Q12 1 16 5L17 11Q27 21 17 24H7Q-3 21 7 11Z" fill="#b8d97b"/><path d="m12 5 2-5" stroke="#b78359" stroke-width="2"/></symbol>
</defs>'''
def svg(w,h,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>ZiDiYao’s little contribution garden</title>{DEFS}{body}</svg>'
def text(x,y,value,size=14,color='#a4b6ad',extra=''):
    return f'<text x="{x}" y="{y}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="{size}" fill="{color}" {extra}>{escape(value)}</text>'
def generate(html=None):
    if html is None:
        req=Request('https://github.com/users/ZiDiYao/contributions',headers={'User-Agent':'ZiDiYao-profile-garden'})
        with urlopen(req,timeout=40) as r: html=r.read().decode()
    cal=Calendar(); cal.feed(html); days=sorted(cal.days)
    if len(days)<300 or len(set(d[0] for d in days))!=len(days):
        raise RuntimeError('Calendar format changed; keep the previous garden.')
    ROOT.joinpath('assets').mkdir(exist_ok=True)
    rng=random.Random(42)
    body='<rect width="1200" height="300" rx="24" fill="#101e1b"/><style>@keyframes fall{from{transform:translateY(-75px)}to{transform:translateY(380px)}}.rain{animation:fall linear infinite}@media(prefers-reduced-motion:reduce){.rain{animation:none}}</style>'
    for i in range(64):
        x=rng.randrange(10,1180); dur=rng.uniform(4,10); delay=-rng.uniform(0,dur); size=rng.randrange(16,33)
        body+=f'<g class="rain" style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s" opacity="{rng.uniform(.3,.7):.2f}"><use xlink:href="#carrot" x="{x}" y="0" width="{size}" height="{size*1.33}" transform="rotate({rng.randrange(-35,35)} {x} 0)"/></g>'
    body+='<rect x="275" y="65" width="650" height="172" rx="30" fill="#101e1b" fill-opacity=".94"/>'
    body+=text(600,101,'WELCOME TO MY LITTLE CORNER OF THE INTERNET',12,'#a9d69b','text-anchor="middle" letter-spacing="2"')
    body+=text(600,163,"Hi, I’m ZiDiYao.",48,'#fff2da','text-anchor="middle" font-weight="700"')
    body+=text(600,204,'A little code. A little creativity. A whole lot of carrots.',17,'#b6c7bc','text-anchor="middle"')
    ROOT.joinpath('assets/carrot-rain.svg').write_text(svg(1200,300,body))
    first=date.fromisoformat(days[0][0]); names=['apple','orange','lemon','berry','grape','melon','cherry','pear']
    body='<rect width="1200" height="330" rx="24" fill="#101e1b"/>'
    body+=text(34,40,'THE CONTRIBUTION ORCHARD',14,'#b9dda5','font-weight="700" letter-spacing="2"')
    body+=text(34,66,'Small commits. Sweeter harvests.',15)
    lastmonth=None
    for i,(dt,level,ident) in enumerate(days):
        d=date.fromisoformat(dt); col=(d-first).days//7; row=(d.weekday()+1)%7; x=36+col*21.25; y=103+row*24
        if row==0 and d.month!=lastmonth and (i > 6 or d.day <= 7):
            body+=text(x,91,d.strftime('%b'),11); lastmonth=d.month
        fruit=names[(col*3+row*5)%len(names)]; opacity=[.22,.55,.7,.85,1][level]
        label=cal.labels.get(ident,dt).strip()
        body+=f'<g opacity="{opacity}"><title>{escape(dt+": "+label)}</title><use xlink:href="#{fruit}" x="{x}" y="{y}" width="17" height="19"/></g>'
    body+=text(36,304,'Every fruit is a day · brighter fruit = more contributions',12)
    body+=text(1164,304,f'Public calendar · {days[-1][0]}',11,'#a4b6ad','text-anchor="end"')
    ROOT.joinpath('assets/fruit-garden.svg').write_text(svg(1200,330,body))
    print(f'Generated banner and garden from {len(days)} real contribution days.')
if __name__=='__main__':
    import sys
    generate(Path(sys.argv[1]).read_text() if len(sys.argv)>1 else None)

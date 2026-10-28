"""Render a public contribution calendar as a donkey eating carrots. Stdlib only."""
from html.parser import HTMLParser
from html import escape
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.days=[]; self.labels={}; self.tip=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and a.get('data-date') and 'data-level' in a:
            self.days.append((a['data-date'],int(a['data-level']),a['id']))
        if tag=='tool-tip': self.tip=a.get('for')
    def handle_data(self,s):
        if self.tip: self.labels[self.tip]=self.labels.get(self.tip,'')+s
    def handle_endtag(self,tag):
        if tag=='tool-tip': self.tip=None

def generate(source=None):
    if source is None:
        req=Request('https://github.com/users/ZiDiYao/contributions',headers={'User-Agent':'ZiDiYao-donkey-calendar'})
        with urlopen(req,timeout=45) as r: source=r.read().decode()
    cal=Calendar(); cal.feed(source); days=sorted(cal.days)
    if len(days)<300 or len(set(d[0] for d in days))!=len(days):
        raise ValueError('Unexpected calendar format; preserve previous animation.')
    first=date.fromisoformat(days[0][0]); positions={}
    for dt,level,ident in days:
        d=date.fromisoformat(dt); col=(d-first).days//7; row=(d.weekday()+1)%7
        positions[dt]=(col,row,level,ident)
    route=sorted(positions,key=lambda dt:(positions[dt][0],positions[dt][1] if positions[dt][0]%2==0 else -positions[dt][1]))
    # Continuous adjacent steps, including an initial off-grid entrance.
    points=[(60,132)]+[(80+positions[dt][0]*17,132+positions[dt][1]*23) for dt in route]
    active=sum(level>0 for _,level,_ in days)
    out=['''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1040" height="325" viewBox="0 0 1040 325" role="img" aria-labelledby="title desc">
<title id="title">A little donkey eating ZiDiYao’s contribution carrots</title>
<desc id="desc">A looping animation based on the real public GitHub contribution calendar. Each carrot is an active day. The donkey visits every day and eats the carrots. Brighter carrots mean more contributions.</desc>
<defs><symbol id="carrot" viewBox="0 0 18 22"><path d="M8 7Q1 0 5 0Q9 0 10 6Q11-2 14 1Q16 4 11 8" fill="#83ce70"/><path d="M3 8Q8 4 14 9L6 21Q4 23 4 19Z" fill="currentColor"/><path d="m5 11 4 2m-3 3 2 1" stroke="#b75e28" stroke-width="1" stroke-linecap="round"/></symbol></defs>
<style>
.bg{fill:#0d1117}.grid{fill:#171f27;stroke:#25303a;stroke-width:.6}.heading{fill:#e6edf3}.muted{fill:#8b949e}
text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}
@media(prefers-color-scheme:light){.bg{fill:#fff}.grid{fill:#f0f3f6;stroke:#d8dee4}.heading{fill:#24292f}.muted{fill:#656d76}}
@keyframes leg{0%,100%{transform:rotate(-15deg)}50%{transform:rotate(15deg)}}
@keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.8px)}}
.walk{animation:hop .32s ease-in-out infinite}.leg{transform-box:fill-box;transform-origin:50% 0;animation:leg .32s ease-in-out infinite}.back{animation-delay:-.16s}
@media(prefers-reduced-motion:reduce){.eaten{animation:none!important}.walk,.leg{animation:none}.traveler,.progress{display:none}}
</style>
<rect class="bg" x=".5" y=".5" width="1039" height="324" rx="14" stroke="#30363d"/>
<text x="28" y="34" class="heading" font-size="17" font-weight="600">A little donkey. A year of carrots.</text>''']
    lastmonth=None
    for dt,level,ident in days:
        col,row,_,_=positions[dt]; x=80+col*17; y=132+row*23; d=date.fromisoformat(dt)
        if row==0 and d.month!=lastmonth and (col>0 or d.day<=7):
            out.append(f'<text x="{x-7}" y="67" class="muted" font-size="10">{d:%b}</text>');lastmonth=d.month
        label=escape(dt+': '+cal.labels.get(ident,'').strip())
        out.append(f'<rect class="grid" x="{x-7}" y="{y-8}" width="14" height="17" rx="3"><title>{label}</title></rect>')
        if level:
            idx=route.index(dt)+1; t=idx/(len(points)-1)*90
            # The mouth reaches this carrot at the corresponding path keyframe.
            out.append(f'<style>@keyframes eat{idx}'+'{'+f'0%,{t:.5f}%'+'{opacity:1}'+f'{t+.001:.5f}%,97%'+'{opacity:0}100%{opacity:1}}</style>')
            color=['','#b97840','#db8c43','#f4a04a','#ffbf6b'][level]
            out.append(f'<g class="eaten" style="animation:eat{idx} 42s linear infinite;color:{color}"><title>{label}</title><use xlink:href="#carrot" x="{x-6}" y="{y-9}" width="13" height="18"/></g>')
    # Position donkey's muzzle on each cell. Keep a short pause before the loop resets.
    values=';'.join(f'{x-27.2} {y-2}' for x,y in points)
    times=';'.join(f'{i/(len(points)-1)*.9:.7f}' for i in range(len(points)))
    values+=';'+f'{points[-1][0]-27.2} {points[-1][1]-2}'
    times+=';1'
    out.append(f'''<g class="traveler"><animateTransform attributeName="transform" type="translate" dur="42s" repeatCount="indefinite" values="{values}" keyTimes="{times}" calcMode="linear"/>
<animate attributeName="opacity" dur="42s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;.91;.94;.98;1"/>
<g transform="scale(1.7)"><g class="walk" stroke-linecap="round" stroke-linejoin="round">
<!-- Rounded, expressive little donkey, with rosy cheeks and a carrot scarf. -->
<path d="M-14-2Q-23-12-22-4" fill="none" stroke="#8994ae" stroke-width="2.4"/>
<ellipse cx="-22" cy="-5" rx="2.5" ry="3.5" fill="#535e79"/>
<g class="leg back"><path d="M-10 3v10" stroke="#7a87a2" stroke-width="4.5"/><path d="M-12 14h5" stroke="#4c5872" stroke-width="3"/></g>
<g class="leg"><path d="M3 4 5 13" stroke="#9aa9c4" stroke-width="4.5"/><path d="M3 14h5" stroke="#53617b" stroke-width="3"/></g>
<ellipse cx="-4" cy="-2" rx="13" ry="9" fill="#aebed8"/>
<ellipse cx="-6" cy="1" rx="8" ry="4.5" fill="#cbd8e9"/>
<path d="M2 1 3-13 11-15 15-2" fill="#adbed9"/>
<path d="M5-13C-3-24-2-34 2-33S10-23 10-15M11-15C9-27 11-36 15-33S20-23 16-14" fill="#aebed8" stroke="#8293b2" stroke-width=".8"/>
<path d="M4-18Q0-27 2-29M14-19Q13-27 15-29" fill="none" stroke="#f4b9c9" stroke-width="2.5"/>
<path d="M3-16Q1-24 5-22L8-19 10-20 11-15" fill="#53617b"/>
<path d="M5-17C7-21 18-20 20-12L20-5Q13 3 6-4Q2-9 5-17" fill="#bacbe3"/>
<ellipse cx="15" cy="-4" rx="8" ry="5.5" fill="#f5e8dc"/>
<ellipse cx="12.5" cy="-12" rx="3.4" ry="4.1" fill="#fffaf3"/>
<ellipse cx="13.5" cy="-11.5" rx="2.2" ry="2.8" fill="#28364d"/>
<circle cx="14.2" cy="-12.6" r=".9" fill="white"/>
<ellipse cx="7.5" cy="-7" rx="2.7" ry="1.6" fill="#f0afbf"/>
<circle cx="19" cy="-5" r=".85" fill="#99877d"/>
<path d="M14-1Q17 1 19-1" fill="none" stroke="#9d8174" stroke-width=".8"/>
<path d="M3-7Q7-3 10-5" fill="none" stroke="#ffa35c" stroke-width="3"/>
<path d="M4-5 1 2 6 0 7-4" fill="#ffb16e"/>
</g></g></g>''')
    out.append('</svg>')
    ROOT.joinpath('assets').mkdir(exist_ok=True)
    ROOT.joinpath('assets/donkey-carrots.svg').write_text('\n'.join(out))
    # Route must visit every real day once using neighboring cells only.
    assert len(set(route))==len(days)
    assert all(abs(x2-x1)+abs(y2-y1)==1 for (x1,y1),(x2,y2) in zip([(positions[d][0],positions[d][1]) for d in route],[(positions[d][0],positions[d][1]) for d in route][1:]))
    print(f'{len(days)} real days, {active} carrots; continuous route verified.')
if __name__=='__main__':
    import sys
    generate(Path(sys.argv[1]).read_text() if len(sys.argv)>1 else None)

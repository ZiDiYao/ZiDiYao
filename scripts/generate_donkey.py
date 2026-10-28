"""Render a public contribution calendar as a donkey eating carrots. Stdlib only."""
from html.parser import HTMLParser
from html import escape
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
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
    today=datetime.now(ZoneInfo('America/Toronto')).date()
    year=today.year
    if source is None:
        req=Request(f'https://github.com/users/ZiDiYao/contributions?from={year}-01-01&to={year}-12-31',headers={'User-Agent':'ZiDiYao-donkey-calendar'})
        with urlopen(req,timeout=45) as r: source=r.read().decode()
    cal=Calendar(); cal.feed(source); days=sorted(d for d in cal.days if date.fromisoformat(d[0]).year==year)
    if sum(date.fromisoformat(d[0])<=today for d in days)!=(today-date(year,1,1)).days+1 or len(set(d[0] for d in days))!=len(days):
        raise ValueError('Unexpected calendar format; preserve previous animation.')
    jan=date(year,1,1); first=jan-timedelta(days=(jan.weekday()+1)%7); positions={}
    for dt,level,ident in days:
        d=date.fromisoformat(dt); col=(d-first).days//7; row=(d.weekday()+1)%7
        positions[dt]=(col,row,level,ident)
    route=sorted(positions,key=lambda dt:(positions[dt][0],positions[dt][1] if positions[dt][0]%2==0 else -positions[dt][1]))
    # Continuous adjacent steps, including an initial off-grid entrance.
    points=[(29,112+positions[route[0]][1]*22)]+[(52+positions[dt][0]*18,112+positions[dt][1]*22) for dt in route]
    active=sum(level>0 for _,level,_ in days)
    out=['''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1040" height="300" viewBox="0 0 1040 300" role="img" aria-labelledby="title desc">
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
<rect class="bg" x=".5" y=".5" width="1039" height="299" rx="14" stroke="#30363d"/>
''']
    out.append(f'<text x="28" y="34" class="heading" font-size="17" font-weight="600">{year}</text>')
    lastmonth=None
    for dt,level,ident in days:
        col,row,_,_=positions[dt]; x=52+col*18; y=112+row*22; d=date.fromisoformat(dt)
        if row==0 and d.month!=lastmonth and (col>0 or d.day<=7):
            out.append(f'<text x="{x-7}" y="70" class="muted" font-size="10">{d:%b}</text>');lastmonth=d.month
        label=escape(dt+': '+cal.labels.get(ident,'').strip())
        out.append(f'<rect class="grid" x="{x-7}" y="{y-8}" width="14" height="17" rx="3"><title>{label}</title></rect>')
        if level and d<=today:
            idx=route.index(dt)+1; t=idx/(len(points)-1)*90
            # The mouth reaches this carrot at the corresponding path keyframe.
            out.append(f'<style>@keyframes eat{idx}'+'{'+f'0%,{t:.5f}%'+'{opacity:1}'+f'{t+.001:.5f}%,97%'+'{opacity:0}100%{opacity:1}}</style>')
            color=['','#b97840','#db8c43','#f4a04a','#ffbf6b'][level]
            out.append(f'<g class="eaten" style="animation:eat{idx} 42s linear infinite;color:{color}"><title>{label}</title><use xlink:href="#carrot" x="{x-6}" y="{y-9}" width="13" height="18"/></g>')
    # Position donkey's muzzle on each cell. Keep a short pause before the loop resets.
    values=';'.join(f'{x-16} {y-2}' for x,y in points)
    times=';'.join(f'{i/(len(points)-1)*.9:.7f}' for i in range(len(points)))
    values+=';'+f'{points[-1][0]-16} {points[-1][1]-2}'
    times+=';1'
    out.append(f'''<g class="traveler"><animateTransform attributeName="transform" type="translate" dur="42s" repeatCount="indefinite" values="{values}" keyTimes="{times}" calcMode="linear"/>
<animate attributeName="opacity" dur="42s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;.91;.94;.98;1"/>
<g class="walk" stroke-linecap="round" stroke-linejoin="round">
<!-- Tiny hand-drawn donkey, facing the next carrot. -->
<path d="M-14-2q-8-8-8-1q3 3 6 3" fill="none" stroke="#727c91" stroke-width="2"/>
<path class="leg back" d="m-9 3-1 10h4l1-10" fill="#697487"/>
<path class="leg" d="m3 3 1 10h4L7 2" fill="#8994a8"/>
<ellipse cx="-3" cy="-1" rx="12" ry="7" fill="#9ca9bc"/>
<path d="M3-2 5-13 11-14 14-3" fill="#a8b5c8"/>
<path d="M6-13Q0-29 5-28Q10-25 10-14M11-14Q10-31 15-28Q18-24 15-13" fill="#9ca9bc" stroke="#65738a" stroke-width="1"/>
<path d="m5-25 3 9m6-10-1 10" stroke="#e5b4ba" stroke-width="1.5"/>
<path d="M3-13 5-20 8-17 9-13" fill="#485267"/>
<path d="M6-14Q16-18 18-9L19-4Q15 1 9-4L6-8" fill="#b3bfd1"/>
<ellipse cx="16" cy="-4" rx="6" ry="4" fill="#e0d9cc"/>
<circle cx="13" cy="-11" r="1.2" fill="#253041"/><circle cx="18" cy="-5" r=".8" fill="#6c6870"/>
<path d="m16-1 3-1" fill="none" stroke="#7e6c60" stroke-width=".8"/>
</g></g>''')
    out.append('</svg>')
    ROOT.joinpath('assets').mkdir(exist_ok=True)
    ROOT.joinpath('assets/donkey-current-year.svg').write_text('\n'.join(out))
    # Route must visit every real day once using neighboring cells only.
    assert len(set(route))==len(days)
    assert all(abs(x2-x1)+abs(y2-y1)==1 for (x1,y1),(x2,y2) in zip([(positions[d][0],positions[d][1]) for d in route],[(positions[d][0],positions[d][1]) for d in route][1:]))
    print(f'{len(days)} real days, {active} carrots; continuous route verified.')
if __name__=='__main__':
    import sys
    generate(Path(sys.argv[1]).read_text() if len(sys.argv)>1 else None)


"""A single animated donkey harvests last year and this year's public contributions."""
from html.parser import HTMLParser
from html import escape
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.request import Request, urlopen
import math

ROOT=Path(__file__).resolve().parents[1]
class Calendar(HTMLParser):
    def __init__(self):
        super().__init__();self.days=[];self.labels={};self.tip=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and a.get('data-date') and 'data-level' in a:
            self.days.append((a['data-date'],int(a['data-level']),a['id']))
        if tag=='tool-tip':self.tip=a.get('for')
    def handle_data(self,s):
        if self.tip:self.labels[self.tip]=self.labels.get(self.tip,'')+s
    def handle_endtag(self,tag):
        if tag=='tool-tip':self.tip=None

DONKEY='''<g class="walk" stroke-linecap="round" stroke-linejoin="round">
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
</g>'''

def generate(fixtures=None,today=None):
    today=today or datetime.now(ZoneInfo('America/Toronto')).date()
    years=[today.year-1,today.year];records={};positions={};route=[]
    for yi,year in enumerate(years):
        if fixtures:
            source=Path(fixtures[yi]).read_text()
        else:
            url=f'https://github.com/users/ZiDiYao/contributions?from={year}-01-01&to={year}-12-31'
            req=Request(url,headers={'User-Agent':'ZiDiYao-donkey-calendar'})
            with urlopen(req,timeout=45) as r:source=r.read().decode()
        cal=Calendar();cal.feed(source)
        fetched={dt:(level,cal.labels.get(ident,'').strip()) for dt,level,ident in cal.days if date.fromisoformat(dt).year==year}
        expected=(min(today,date(year,12,31))-date(year,1,1)).days+1
        if sum(date.fromisoformat(dt)<=today for dt in fetched)!=expected:
            raise ValueError(f'Incomplete {year} calendar; preserve existing animation.')
        jan=date(year,1,1);start=jan-timedelta(days=(jan.weekday()+1)%7)
        for n in range((date(year,12,31)-jan).days+1):
            d=jan+timedelta(days=n);dt=d.isoformat();col=(d-start).days//7;row=(d.weekday()+1)%7
            panel=yi*2+col//27;x=62+(col%27)*35;y=100+yi*730+(col//27)*330+row*36
            level,label=fetched.get(dt,(0,''))
            records[dt]=(d,level,label);positions[dt]=(col,row,panel,x,y)
        year_route=sorted((dt for dt in records if date.fromisoformat(dt).year==year and date.fromisoformat(dt)<=today),key=lambda dt:(positions[dt][0],positions[dt][1] if positions[dt][0]%2==0 else -positions[dt][1]))
        route.extend(year_route)
    # One route and one character, including visible walks through the gutters between panels.
    points=[(26,positions[route[0]][4])];distances=[0.0];arrivals={}
    def step(x,y):
        distances.append(distances[-1]+math.hypot(x-points[-1][0],y-points[-1][1]));points.append((x,y))
    previous=None
    for dt in route:
        col,row,panel,x,y=positions[dt]
        if previous is not None and panel!=positions[previous][2]:
            prev_panel=positions[previous][2];prev_top=100+(prev_panel//2)*730+(prev_panel%2)*330
            next_top=100+(panel//2)*730+(panel%2)*330;bridge=(prev_top+216+next_top)/2
            step(1010,points[-1][1]);step(1010,bridge);step(27,bridge);step(27,y)
        step(x,y);arrivals[dt]=distances[-1];previous=dt
    travel_end=.94;total=distances[-1];duration=110
    out=['''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1040" height="1430" viewBox="0 0 1040 1430" role="img" aria-labelledby="title desc">
<title id="title">One little donkey, two years of contribution carrots</title>
<desc id="desc">Last year's full GitHub contribution calendar followed by this year to date. A single donkey follows one continuous route and eats the carrots, then the entire animation loops. Future dates are empty.</desc>
<defs><symbol id="carrot" viewBox="0 0 18 22"><path d="M8 7Q1 0 5 0Q9 0 10 6Q11-2 14 1Q16 4 11 8" fill="#83ce70"/><path d="M3 8Q8 4 14 9L6 21Q4 23 4 19Z" fill="currentColor"/><path d="m5 11 4 2m-3 3 2 1" stroke="#b75e28" stroke-width="1" stroke-linecap="round"/></symbol></defs>
<style>
.bg{fill:#0d1117}.grid{fill:#171f27;stroke:#25303a;stroke-width:.6}.year{fill:#e6edf3}.muted{fill:#8b949e}text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}
@media(prefers-color-scheme:light){.bg{fill:#fff}.grid{fill:#f0f3f6;stroke:#d8dee4}.year{fill:#24292f}.muted{fill:#656d76}}
@keyframes leg{0%,100%{transform:rotate(-15deg)}50%{transform:rotate(15deg)}}@keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.8px)}}
.walk{animation:hop .32s ease-in-out infinite}.leg{transform-box:fill-box;transform-origin:50% 0;animation:leg .32s ease-in-out infinite}.back{animation-delay:-.16s}
@media(prefers-reduced-motion:reduce){.eaten,.walk,.leg{animation:none!important}.traveler{display:none}}
</style><rect class="bg" x=".5" y=".5" width="1039" height="1429" rx="14" stroke="#30363d"/>''']
    for yi,year in enumerate(years):out.append(f'<text x="38" y="{30+yi*730}" class="year" font-size="21" font-weight="600">{year}</text>')
    months=set()
    for dt,(d,level,label) in sorted(records.items()):
        col,row,panel,x,y=positions[dt];yi=years.index(d.year)
        if (d.year,d.month,panel) not in months:
            if (col%27)>0 and d.day==1 and row>0:month_x=x+7
            else:month_x=x-7
            out.append(f'<text x="{month_x}" y="{60+yi*730+(col//27)*330}" class="muted" font-size="14">{d:%b}</text>');months.add((d.year,d.month,panel))
        title=escape(dt+': '+(label if d<=today else 'Future date'))
        future=' opacity=".3"' if d>today else ''
        out.append(f'<rect class="grid" x="{x-14}" y="{y-14}" width="28" height="28" rx="5"{future}><title>{title}</title></rect>')
        if level and d<=today:
            t=arrivals[dt]/total*travel_end*100;idx=len(out)
            out.append(f'<style>@keyframes eat{idx}'+'{'+f'0%,{t:.6f}%'+'{opacity:1}'+f'{t+.0001:.6f}%,98%'+'{opacity:0}100%{opacity:1}}</style>')
            color=['','#b97840','#db8c43','#f4a04a','#ffbf6b'][level]
            out.append(f'<g class="eaten" style="animation:eat{idx} {duration}s linear infinite;color:{color}"><title>{title}</title><use xlink:href="#carrot" x="{x-11}" y="{y-14}" width="22" height="28"/></g>')
    values=';'.join(f'{x-16} {y-2}' for x,y in points)+f';{points[-1][0]-16} {points[-1][1]-2}'
    keytimes=';'.join(f'{d/total*travel_end:.8f}' for d in distances)+';1'
    out.append(f'<g class="traveler"><animateTransform attributeName="transform" type="translate" dur="{duration}s" repeatCount="indefinite" values="{values}" keyTimes="{keytimes}" calcMode="linear"/><animate attributeName="opacity" dur="{duration}s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;.95;.97;.99;1"/>'+DONKEY+'</g></svg>')
    assert len(set(route))==len(route)==sum(d<=today for d,_,_ in records.values())
    previous_year_days=(date(years[0]+1,1,1)-date(years[0],1,1)).days
    assert all(date.fromisoformat(dt).year==years[0] for dt in route[:previous_year_days])
    assert max(arrivals[d] for d in route if date.fromisoformat(d).year==years[0])<min(arrivals[d] for d in route if date.fromisoformat(d).year==years[1])
    xml='\n'.join(out)
    assert xml.count('class="traveler"')==1
    ROOT.joinpath('assets').mkdir(exist_ok=True)
    ROOT.joinpath('assets/donkey-two-years.svg').write_text(xml)
    print(f'{years}: {len(route)} real days, {sum(level>0 and d<=today for d,level,_ in records.values())} carrots; one donkey and year order verified.')
if __name__=='__main__':
    import sys
    generate(sys.argv[1:3] or None)

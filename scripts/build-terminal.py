from pathlib import Path
from html import escape
import sys
from collections import deque
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
SOURCES = [Path(value) for value in sys.argv[1:]]
if len(SOURCES) != 3:
    raise SystemExit('Pass the three anime reference images in display order.')
SLOGAN = 'Building weird shit you didn’t know you wanted.'
COLORS = {'bg': '#070c10', 'panel': '#0d151a', 'border': '#263a41', 'text': '#ddede7', 'green': '#88f7ae', 'cyan': '#66d9ed', 'muted': '#91a9ad', 'pink': '#eab0d0'}
TITLE = [
    '  _____ _      ______      ________ _____  ',
    ' / ____| |    / __ \\ \\    / /  ____|  __ \\ ',
    '| |    | |   | |  | |\\ \\  / /| |__  | |__) |',
    '| |    | |   | |  | | \\ \\/ / |  __| |  _  / ',
    '| |____| |___| |__| |  \\  /  | |____| | \\ \\ ',
    ' \\_____|______\\____/    \\/   |______|_|  \\_\\',
]

def text(x, y, value, size=22, color='text', attrs=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{COLORS.get(color, color)}" {attrs}>{escape(value)}</text>'

def svg(width, height, title, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">An animated hacker terminal for Clover Jam, with an ASCII portrait made from the profile's anime avatar. Animation stops when reduced motion is enabled.</desc>
<style>
text{{font-family:Consolas,'Liberation Mono',monospace;font-variant-ligatures:none}}
.type{{animation:typing 1.8s steps(34,end) both}}
.type-later{{animation:typing 1.5s steps(30,end) 1.8s both}}
.portrait{{animation:assemble 2s steps(48,end) .3s both}}
.cursor{{animation:blink 1.2s steps(1,end) infinite}}
.scan{{animation:scan 9s linear 2.4s infinite;opacity:0}}
@keyframes typing{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
@keyframes assemble{{from{{clip-path:inset(0 0 100% 0);opacity:.4}}to{{clip-path:inset(0 0 0 0);opacity:1}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes scan{{0%,65%{{transform:translateY(0);opacity:0}}66%{{opacity:.25}}91%{{transform:translateY(400px);opacity:.25}}92%,100%{{transform:translateY(400px);opacity:0}}}}
@media(prefers-reduced-motion:reduce){{.type,.type-later,.portrait,.cursor,.scan{{animation:none!important;clip-path:none!important}}.scan{{display:none}}}}
</style>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" fill="{COLORS['bg']}" stroke="{COLORS['border']}" stroke-width="2"/>
{content}
</svg>'''

def chrome(width, label):
    return (f'<path d="M13 1H{width-13}Q{width-1} 1 {width-1} 13V56H1V13Q1 1 13 1Z" fill="{COLORS["panel"]}"/>'
            + f'<path d="M1 56H{width-1}" stroke="{COLORS["border"]}"/>'
            + '<circle cx="26" cy="28" r="5" fill="#eab0d0"/><circle cx="45" cy="28" r="5" fill="#e5cf90"/><circle cx="64" cy="28" r="5" fill="#88f7ae"/>'
            + text(88,35,label,18,'muted'))

def ascii_rows(source):
    original = Image.open(source).convert('RGB')
    scaled = ImageOps.contain(original, (176,168), Image.Resampling.LANCZOS).convert('RGBA')
    canvas = Image.new('RGBA',(176,168),(0,0,0,0))
    canvas.paste(scaled,((176-scaled.width)//2,(168-scaled.height)//2))
    queue = deque([(x,y) for x in range(176) for y in [0,167]] + [(x,y) for y in range(168) for x in [0,175]])
    seen = set()
    while queue:
        x,y = queue.popleft()
        if (x,y) in seen or not (0 <= x < 176 and 0 <= y < 168):
            continue
        seen.add((x,y))
        r,g,b,a = canvas.getpixel((x,y))
        if a == 0 or (min(r,g,b) > 241 and max(r,g,b)-min(r,g,b) < 17):
            canvas.putpixel((x,y),(0,0,0,0))
            queue.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
    image = canvas.resize((88,49),Image.Resampling.LANCZOS)
    ramp = ' .,:;i1tfLCG08@'
    rows = []
    for y in range(image.height):
        row = []
        for x in range(image.width):
            r,g,b,a = image.getpixel((x,y))
            lum = (r*.2126+g*.7152+b*.0722)/255
            char = ' ' if a < 100 else ramp[min(len(ramp)-1,max(2,int(lum*(len(ramp)-1))))]
            if lum < .25:
                color = '#9686ae'
            elif g > r*1.08 and b > r*1.08:
                color = '#70dce6'
            elif r > g*1.25 and r > b*1.12:
                color = '#f299ba'
            elif r > g*1.05 and b > g*1.03:
                color = '#e4b5da' if lum > .65 else '#b096c5'
            elif lum > .83:
                color = '#f0deed'
            else:
                color = '#b3bada'
            row.append((char,color))
        rows.append(row)
    return rows

PORTRAITS = [ascii_rows(source) for source in SOURCES]
ASSETS.joinpath('avatar.txt').write_text('\n\n'.join(f'anime_{index+1:02d}\n'+'\n'.join(''.join(char for char,_ in row) for row in rows) for index,rows in enumerate(PORTRAITS))+'\n',encoding='utf8')

def portrait_frame(rows,x,y,width):
    unit=width/88
    size=unit/.60
    line=unit*1.72
    parts=[]
    for iy,row in enumerate(rows):
        runs=[]
        start=0
        while start<len(row):
            color=row[start][1]
            end=start+1
            while end<len(row) and row[end][1]==color:
                end+=1
            value=''.join(char for char,_ in row[start:end])
            runs.append(f'<tspan x="{x+start*unit:.2f}" fill="{color}">{escape(value)}</tspan>')
            start=end
        parts.append(f'<text y="{y+iy*line:.2f}" font-size="{size:.2f}" xml:space="preserve">{"".join(runs)}</text>')
    return '<g class="portrait">'+''.join(parts)+'</g>'

def portrait(x,y,width):
    return ''.join(f'<g class="frame frame-{index}" opacity="{1 if index == 0 else 0}">'+portrait_frame(rows,x,y,width)+'</g>' for index,rows in enumerate(PORTRAITS))

def hero(mobile=False):
    width,height=(600,1000) if mobile else (1200,590)
    parts=[chrome(width,'clover@github: ~')]
    parts.append(text(30,104,'clover@github:~$ neofetch',28 if mobile else 23,'green', 'class="type"'))
    if mobile:
        parts.append(portrait(76,145,448))
        parts.append(text(32,625,'Clover Jam',42,'green'))
        parts.append(text(32,665,'@clover1417',24,'cyan'))
        items=[('focus','code + 3D modeling'),('builds','games + full-stack web'),('learning','Unreal Engine 5')]
        for i,(key,value) in enumerate(items):
            parts.append(text(32,718+i*42,key,28,'cyan'))
            parts.append(text(185,718+i*42,value,28))
        palette_y=850
        prompt_y=948
    else:
        for i,line in enumerate(TITLE):
            parts.append(text(30,163+i*24,line,21,'green','xml:space="preserve"'))
        parts.append(text(33,335,'Clover Jam / clover1417',27,'text'))
        items=[('focus','code + 3D modeling'),('builds','games + full-stack web'),('learning','Unreal Engine 5')]
        for i,(key,value) in enumerate(items):
            parts.append(text(33,382+i*36,key,22,'cyan'))
            parts.append(text(170,382+i*36,value,22))
        parts.append(portrait(699,113,458))
        parts.append(f'<rect x="696" y="110" width="465" height="2" fill="{COLORS["green"]}" class="scan"/>')
        palette_y=489
        prompt_y=554
    for i,color in enumerate(['#47716b','#66d9bd','#88f7ae','#d0f5e6','#66d9ed','#eab0d0','#e5cf90','#91a9ad']):
        parts.append(f'<rect x="{33+i*31}" y="{palette_y}" width="31" height="15" fill="{color}"/>')
    parts.append(text(33,prompt_y,'clover@github:~$',23,'green'))
    parts.append(f'<rect x="257" y="{prompt_y-21}" width="13" height="25" fill="{COLORS["green"]}" class="cursor"/>')
    result = svg(width,height,'Clover Jam | animated terminal and three anime ASCII portraits',''.join(parts))
    frame_css = '''
.frame-0{animation:frame-one 24s linear infinite}
.frame-1{animation:frame-two 24s linear infinite}
.frame-2{animation:frame-three 24s linear infinite}
@keyframes frame-one{0%,30%{opacity:1}32%,97%{opacity:0}100%{opacity:1}}
@keyframes frame-two{0%,32%{opacity:0}34%,63%{opacity:1}65%,100%{opacity:0}}
@keyframes frame-three{0%,65%{opacity:0}67%,97%{opacity:1}99%,100%{opacity:0}}
@media(prefers-reduced-motion:reduce){.frame{animation:none!important}.frame-0{opacity:1!important}.frame-1,.frame-2{display:none}}
'''
    return result.replace('</style>',frame_css+'</style>').replace("made from the profile's anime avatar",'made from three supplied anime references')

def slogan(mobile=False):
    width,height=(600,230) if mobile else (1200,215)
    parts=[text(30,47,'clover@github:~$ cat /etc/motd',23,'cyan')]
    parts.append(f'<path d="M30 68H{width-30}" stroke="{COLORS["border"]}"/>')
    lines=['Building weird shit','you didn’t know you wanted.']
    for i,line in enumerate(lines):
        line_svg = text(31,116+i*44,line,32 if mobile else 34,'green' if i==0 else 'text',f'class="{"type" if i==0 else "type-later"}" font-weight="700"')
        if i == len(lines)-1:
            line_svg = line_svg.replace('</text>', '<tspan class="cursor" fill="#88f7ae"> █</tspan></text>')
        parts.append(line_svg)
    return svg(width,height,SLOGAN,''.join(parts))

for name,content in [('terminal.svg',hero()),('terminal-mobile.svg',hero(True)),('slogan.svg',slogan()),('slogan-mobile.svg',slogan(True))]:
    ASSETS.joinpath(name).write_text(content,encoding='utf8')
    static = content.replace('</style>', '.type,.type-later,.portrait,.cursor,.scan{animation:none!important;clip-path:none!important}.scan{display:none}</style>')
    if name.startswith('terminal'):
        static = static.replace('</style>','.frame{animation:none!important}.frame-0{opacity:1!important}.frame-1,.frame-2{display:none}</style>')
    ASSETS.joinpath(name.replace('.svg','-static.svg')).write_text(static,encoding='utf8')
    print(f'{name}: {len(content):,} characters')

from pathlib import Path
from html import escape
import math
import sys
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
SOURCE = Path(sys.argv[1])
SLOGAN = "I do the most stupid shit that you surely haven't seen before."
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

original = Image.open(SOURCE).convert('RGB')
image = ImageEnhance.Contrast(original).enhance(1.18).resize((88,49), Image.Resampling.LANCZOS)
ramp = ' .,:;i1tfLCG08@'
rows = []
for y in range(image.height):
    row = []
    for x in range(image.width):
        r,g,b = image.getpixel((x,y))
        lum = (r*.2126 + g*.7152 + b*.0722)/255
        outside = (b > r*1.2 and g > r*1.15) or ((x-43.5)/46)**2 + ((y-24)/27)**2 > 1.14
        char = ' ' if outside else ramp[min(len(ramp)-1, int(lum*(len(ramp)-1)))]
        if lum < .24:
            color = '#47716b'
        elif r > g*1.14 and r > b*1.20:
            color = '#88f7ae'
        elif r > b*1.28 and g > b*1.15:
            color = '#e5cf90'
        elif lum > .82:
            color = '#d0f5e6'
        else:
            color = '#66d9bd'
        row.append((char,color))
    rows.append(row)
ASSETS.joinpath('avatar.txt').write_text('\n'.join(''.join(char for char,_ in row) for row in rows)+'\n',encoding='utf8')

def portrait(x,y,width):
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
    return svg(width,height,'Clover Jam | animated terminal and anime ASCII portrait',''.join(parts))

def slogan(mobile=False):
    width,height=(600,285) if mobile else (1200,215)
    parts=[text(30,47,'clover@github:~$ cat /etc/motd',23,'cyan')]
    parts.append(f'<path d="M30 68H{width-30}" stroke="{COLORS["border"]}"/>')
    lines=['I do the most stupid shit',"that you surely haven't",'seen before.'] if mobile else ['I do the most stupid shit',"that you surely haven't seen before."]
    for i,line in enumerate(lines):
        line_svg = text(31,116+i*44,line,32 if mobile else 34,'green' if i==0 else 'text',f'class="{"type" if i==0 else "type-later"}" font-weight="700"')
        if i == len(lines)-1:
            line_svg = line_svg.replace('</text>', '<tspan class="cursor" fill="#88f7ae"> █</tspan></text>')
        parts.append(line_svg)
    return svg(width,height,SLOGAN,''.join(parts))

for name,content in [('terminal.svg',hero()),('terminal-mobile.svg',hero(True)),('slogan.svg',slogan()),('slogan-mobile.svg',slogan(True))]:
    ASSETS.joinpath(name).write_text(content,encoding='utf8')
    static = content.replace('</style>', '.type,.type-later,.portrait,.cursor,.scan{animation:none!important;clip-path:none!important}.scan{display:none}</style>')
    ASSETS.joinpath(name.replace('.svg','-static.svg')).write_text(static,encoding='utf8')
    print(f'{name}: {len(content):,} characters')

"""Create synthetic example images; requires Pillow; refuses existing outputs."""
import argparse
import csv
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

def font(size):
    for face in ['Arial.ttf', 'DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf']:
        try:
            return ImageFont.truetype(face, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    if out.exists():
        p.error('Choose a new output directory; no overwrite')
    out.mkdir(parents=True)
    rng = random.Random(20261012)
    base = Image.new('RGB', (720, 560), '#253c47')
    d = ImageDraw.Draw(base)
    for _ in range(400):
        x,y = rng.randrange(720), rng.randrange(560)
        d.ellipse((x,y,x+4,y+3),fill='#34515c')
    d.polygon([(0,400),(720,100),(720,150),(0,450)],fill='#586f78')
    objects = [(145,140),(350,270),(480,190),(580,410)]
    for x,y in objects:
        d.rectangle((x,y,x+15,y+9),fill='#dedbd0')
    for name, indices in [('gt',[0,1,2,3]),('baseline',[0,2]),('improved',[0,1,2])]:
        img = base.copy(); d = ImageDraw.Draw(img)
        for i in indices:
            x,y=objects[i]
            d.rectangle((x-8,y-8,x+23,y+17),outline='#2ce2aa' if name=='gt' else '#26b9ff',width=3)
        if name=='improved':
            d.rectangle((270,390,302,416),outline='#ffb035',width=3)
        d.rectangle((0,0,720,36),fill='#192c34')
        d.text((15,8),'SYNTHETIC DEMO - NOT A REAL IMAGE',font=font(24),fill='white')
        img.save(out/f'{name}.png')
    with Image.open(out/'improved.png') as img:
        img.crop((230,355,340,450)).resize((660,570)).save(out/'bad-case.png')
    csv_path = Path(__file__).resolve().parents[1]/'examples/experiment/data/demo-curve.csv'
    with csv_path.open(encoding='utf-8-sig',newline='') as f:
        rows = list(csv.DictReader(f))
    plot = Image.new('RGB',(1400,720),'white'); d = ImageDraw.Draw(plot)
    left,right,top,bottom=150,1270,100,530
    ymin,ymax=30,70
    for value in range(ymin,ymax+1,10):
        y=bottom-(value-ymin)/(ymax-ymin)*(bottom-top)
        d.line((left,y,right,y),fill='#d9d9d9',width=2); d.text((55,y-26),str(value),font=font(48),fill='#262626')
    d.line((left,top,left,bottom,right,bottom),fill='#262626',width=3)
    d.text((150,20),'SYNTHETIC DEMO: AP50 (%)',font=font(48),fill='#262626')
    for col,color,label_y in [('baseline','#0173B2',635),('detail','#029E73',695)]:
        points=[]
        for row in rows:
            x=left+float(row['epoch'])/50*(right-left)
            y=bottom-(float(row[col])-ymin)/(ymax-ymin)*(bottom-top)
            points.append((x,y)); d.ellipse((x-5,y-5,x+5,y+5),fill=color)
            if col=='baseline': d.text((x-20,bottom+10),row['epoch'],font=font(48),fill='#262626')
        d.line(points,fill=color,width=5)
        d.line((550,label_y,605,label_y),fill=color,width=5); d.text((620,label_y-27),col,font=font(48),fill='#262626')
    d.text((1100,595),'epoch',font=font(48),fill='#262626')
    plot.save(out/'curve.png')
    print(out)

if __name__ == '__main__':
    main()

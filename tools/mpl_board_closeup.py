import runpy,io,contextlib,sys
from PIL import Image, ImageDraw
with contextlib.redirect_stdout(io.StringIO()): g=runpy.run_path('/home/user/haifu-kaihen/tools/mpl_board.py')
V,R=g['V'],g['ROAD']
blocked=[1 for (x,z),y in R.items() if any((x,yy,z) in V and V[(x,yy,z)] not in ('air',) and not V[(x,yy,z)].startswith(('lantern',)) for yy in (y+1,y+2))]
miss=[1 for (x,z),y in R.items() if (x,y,z) not in V]
print('blocked',len(blocked),'missing',len(miss))
C=dict(g['C']); C.update({'white_concrete':(242,242,242),'prismarine_bricks':(90,175,160),'prismarine':(80,150,145),'blue_stained_glass':(60,90,210),'diorite_wall':(205,205,205),'iron_block':(220,220,220),'iron_bars':(170,170,170),'polished_andesite':(140,145,145),'andesite':(130,130,130),'cracked_stone_bricks':(115,115,115),'stripped_spruce_log':(140,110,70),'pink_wool':(240,150,180),'white_wool':(245,245,245),'red_concrete':(170,30,30),'spruce_planks':(110,85,50),'lightning_rod':(200,120,80),'lantern':(255,200,90)})
def col(b):
    k=b.split(' ')[0]
    if k in C: return C[k]
    return g['colr'](k)
x0,x1,z0,z1=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
S=24; W,Hh=1500,1500
img=Image.new('RGB',(W,Hh),(120,180,230)); d=ImageDraw.Draw(img)
def proj(x,y,z): return W/2+(x-(x0+x1)/2)*S*1.0+(z-z0)*S*0.35, Hh*0.98-(z-z0)*S*0.45-(y-6)*S*0.95
items=[(k,b) for k,b in V.items() if x0<=k[0]<=x1 and z0<=k[2]<=z1 and b!='air']
for (x,y,z),b in sorted(items,key=lambda kv:(-kv[0][2],kv[0][1],kv[0][0])):
    c=col(b); px,py=proj(x,y,z)
    d.polygon([(px,py-S*0.95),(px+S,py-S*0.95),(px+S*1.35,py-S*0.95-S*0.45),(px+S*0.35,py-S*0.95-S*0.45)],fill=tuple(min(255,int(v*1.08)) for v in c))
    d.polygon([(px,py),(px+S,py),(px+S,py-S*0.95),(px,py-S*0.95)],fill=c)
    d.polygon([(px+S,py),(px+S*1.35,py-S*0.45),(px+S*1.35,py-S*0.95-S*0.45),(px+S,py-S*0.95)],fill=tuple(int(v*0.75) for v in c))
img.save(sys.argv[5])

#!/usr/bin/env python3
"""
Section through the key turner's key axis (v2.1): key shaft, bearings, retainer,
washer, screw, plate, cap, key. Renders each part from key_turner_assembled.scad
and cuts it with trimesh at y = 0.

    python3 cad/tools/key_shaft_section.py   # -> cad/renders/key_turner_v2.1_bearing_stack.png
"""
import subprocess, os, tempfile, numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP
HERE = os.path.dirname(os.path.abspath(__file__))
asm = os.path.join(HERE, '..', 'key_turner_assembled.scad')
OUT = os.path.join(HERE, '..', 'renders', 'key_turner_v2.1_bearing_stack.png')
S = tempfile.mkdtemp()
parts=[('plate','#b0c4de','#556'),('bearings','#d0d0d0','#666'),('retainer','#f5a623','#a60'),('shaft','#6abf69','#264'),('washer','#ffd700','#a80'),('screw','#777','#333'),('cap','#f0a050','#a50'),('key','#ccc','#555')]
fig,ax=plt.subplots(figsize=(11,7),dpi=140)
for p,fc,ec in parts:
    out=f'{S}/sec_{p}.stl'
    subprocess.run(['openscad','-q','-o',out,'-D',f'part="{p}"',asm],check=True)
    m=trimesh.load(out); sec=m.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
    if sec is None: continue
    p2,T=sec.to_2D(to_2D=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float))
    for poly in p2.polygons_full:
        ax.add_patch(MP(np.asarray(poly.exterior.coords),closed=True,fc=fc,ec=ec,lw=0.7))
        for r in poly.interiors: ax.add_patch(MP(np.asarray(r.coords),closed=True,fc='white',ec=ec,lw=0.7))
ax.set_xlim(-32,32); ax.set_ylim(30,71); ax.set_aspect('equal'); ax.set_xlabel('x (mm), key axis at 0'); ax.set_ylabel('z from the door face (mm)')
def note(xy,t,xyt): ax.annotate(t,xy=xy,xytext=xyt,fontsize=8,arrowprops=dict(arrowstyle='-',lw=0.6))
note((12,66.2),'bearing retainer (v2.1): 0.3 mm lip on the\nouter ring, 4x M3x6 countersunk into the plate',(15,67.6))
note((0,62.5),'M3x6 countersunk (was M3x10): ~3 mm of thread',(-31,68.5))
note((-4.5,65.7),'washer on the inner ring',(-31,66))
note((7,47.3),'root fillet (v2.1), where the M3x10 snapped it',(10,43))
note((10.5,57),'608 x2',(18,55))
ax.set_title('Key turner v2.1: key shaft in its bearings, section through the key axis (revision ' + open(os.path.join(HERE, '..', '..', 'REVISION')).read().strip() + ')',fontsize=10)
fig.tight_layout(); fig.savefig(OUT); print('wrote', os.path.relpath(OUT))

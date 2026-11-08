#!/usr/bin/env python3
"""Convert a local still photo to its fixed website image name.
Usage: python scripts/prepare-image.py --slot home-hero --input C:/photos/new.jpg
Requires: pip install Pillow
"""
from pathlib import Path
import argparse,json
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description='Convert photo into an INCOGNITO fixed-name WebP slot')
parser.add_argument('--slot',required=True,help='ID in media-slots.json')
parser.add_argument('--input',required=True,help='Source photo (JPG, PNG, etc.)')
args=parser.parse_args()
registry=json.loads((ROOT/'media-slots.json').read_text(encoding='utf-8'))
slot=next((s for s in registry['slots'] if s['id']==args.slot),None)
if slot is None: parser.error('Unknown slot: '+args.slot)
source=Path(args.input)
if not source.is_file(): parser.error('File missing: '+str(source))
out=ROOT/slot['file']
with Image.open(source) as im:
    if getattr(im,'n_frames',1)>1: parser.error('Animated input: use an animated WebP export, or future MP4 workflow; this script only processes stills.')
    im=ImageOps.exif_transpose(im).convert('RGB')
    max_w=slot['maxSuggestedWidth']
    if im.width>max_w:
        im=im.resize((max_w,round(im.height*max_w/im.width)),Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,format='WEBP',quality=83,method=6)
print(f'Updated: {out.relative_to(ROOT)} ({out.stat().st_size/1024:.0f} KB; {im.width}x{im.height})')

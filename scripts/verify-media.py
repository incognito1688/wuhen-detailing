#!/usr/bin/env python3
"""Verify all media paths, DOM selectors, image formats, and PR MP4 audio-free structure."""
from pathlib import Path
import json
import subprocess
import sys
from bs4 import BeautifulSoup
from PIL import Image

root=Path(__file__).resolve().parent.parent
registry=json.loads((root/'media-slots.json').read_text(encoding='utf-8'))
errors=[]
warnings=[]


def inspect_webp(file, name):
    try:
        with Image.open(file) as im:
            if im.format != 'WEBP':
                errors.append(f'{name}: expected WebP, got {im.format}')
            if im.width < 300 or im.height < 180:
                warnings.append(f'{name}: small image {im.width}x{im.height}')
    except Exception as exc:
        errors.append(f'{name}: cannot decode WebP: {exc}')

for slot in registry['slots']:
    slot_id=slot['id']
    path=root/slot['file']
    page=root/slot['page']
    if not path.is_file():
        errors.append(f'{slot_id}: missing media {slot["file"]}')
        continue
    if not page.is_file():
        errors.append(f'{slot_id}: missing page {slot["page"]}')
        continue
    soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
    selector=soup.select_one(slot['selector'])
    if selector is None:
        errors.append(f'{slot_id}: selector not found {slot["selector"]}')
    elif slot.get('render')=='video':
        if selector.name!='video':
            errors.append(f'{slot_id}: expected video node')
        elif not selector.find('source',src=slot['file']):
            errors.append(f'{slot_id}: video source path mismatch')
        if not slot_id.endswith('-video') and slot_id.startswith('pr-'):
            if selector.has_attr('controls') or not selector.has_attr('muted') or not selector.has_attr('loop') or not selector.has_attr('playsinline'):
                errors.append(f'{slot_id}: PR video playback attributes incorrect')
    elif not selector.get('src')==slot['file']:
        errors.append(f'{slot_id}: image src/path mismatch')

    if slot.get('render')=='video':
        if path.suffix.lower()!='.mp4':
            errors.append(f'{slot_id}: video should be MP4')
        else:
            try:
                proc=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name',
                                    '-of','json',str(path)],capture_output=True,text=True,check=True)
                streams=json.loads(proc.stdout)['streams']
                videos=[s for s in streams if s['codec_type']=='video']
                audio=[s for s in streams if s['codec_type']=='audio']
                if not videos or videos[0]['codec_name']!='h264':
                    errors.append(f'{slot_id}: missing H.264 video stream')
                if slot.get('hasAudioTrack') is False and audio:
                    errors.append(f'{slot_id}: PR videos must contain no audio stream')
            except Exception as exc:
                errors.append(f'{slot_id}: cannot probe video: {exc}')
        if slot.get('posterFile'):
            poster=root/slot['posterFile']
            if not poster.is_file(): errors.append(f'{slot_id}: missing poster {slot["posterFile"]}')
            else: inspect_webp(poster, f'{slot_id} poster')
    elif path.suffix.lower()=='.webp':
        inspect_webp(path,slot_id)

    target=slot.get('targetFileKB')
    if target and path.stat().st_size / 1024 > target:
        warnings.append(f'{slot_id}: file above target size ({path.stat().st_size/1024:.0f} KB > {target} KB)')

# local href and resource references across the 4 pages
for page in root.glob('*.html'):
    soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
    for el in soup.select('[src], [href], [poster]'):
        for attr in ('src','href','poster'):
            ref=el.get(attr)
            if not ref or ref.startswith(('http://','https://','tel:','mailto:','#','data:')): continue
            ref=ref.split('?')[0].split('#')[0]
            if ref and not (root/ref).is_file():
                errors.append(f'{page.name}: missing {attr} -> {ref}')

print(f'Verified {len(registry["slots"])} media slots and {len(list(root.glob("*.html")))} pages')
for msg in warnings: print('WARNING:', msg)
for msg in errors: print('ERROR:', msg)
sys.exit(1 if errors else 0)

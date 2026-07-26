import cv2
from pathlib import Path
from scripts.make_ascii_svg import build_ascii_grid

image_path = Path('source-prepped.png')
svg_path = Path('avi-ascii.svg')
print('image exists', image_path.exists())
if image_path.exists():
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    print('shape', img.shape if img is not None else None)
    if img is not None:
        print('min max mean', int(img.min()), int(img.max()), float(img.mean()))
        rows = build_ascii_grid(img, width=100)
        print('rows', len(rows), 'cols', len(rows[0]) if rows else 0)
        print('first row repr', repr(rows[0][:80]) if rows else None)
        print('some chars', set(''.join(rows[:5])) if rows else None)
print('svg exists', svg_path.exists())
if svg_path.exists():
    txt = svg_path.read_text('utf-8')
    print('svg len', len(txt))
    print('contains text tag', '<text' in txt)
    print('contains clipPath', 'clipPath' in txt)

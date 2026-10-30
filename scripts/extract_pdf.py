"""Export an original PDF page/crop without rasterizing; record source location."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf', type=Path)
    p.add_argument('--page', type=int, required=True, help='1-based PDF page, not printed page')
    p.add_argument('--crop', type=float, nargs=4, metavar=('X0', 'Y0', 'X1', 'Y1'), help='PDF pt, bottom-left origin after rotation normalization')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import RectangleObject
    except ImportError:
        p.error('pypdf unavailable; use an existing PDF crop tool or the full-page graphicx viewport option')
    output = args.output.resolve()
    provenance = output.with_suffix('.provenance.json')
    if output.suffix.lower() != '.pdf' or output.exists() or provenance.exists():
        p.error('Output must be a new .pdf path; no overwrite')
    reader = PdfReader(args.pdf)
    if not 1 <= args.page <= len(reader.pages):
        p.error('Page outside PDF range')
    page = reader.pages[args.page-1]
    if page.rotation:
        page.transfer_rotation_to_content()
    if args.crop:
        x0, y0, x1, y1 = args.crop
        m = page.mediabox
        if not float(m.left) <= x0 < x1 <= float(m.right) or not float(m.bottom) <= y0 < y1 <= float(m.top):
            p.error('Invalid crop or crop outside normalized media box')
        page.mediabox = RectangleObject(args.crop)
        page.cropbox = RectangleObject(args.crop)
    writer = PdfWriter()
    writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('wb') as f:
        writer.write(f)
    record = {'source': str(args.pdf.resolve()), 'sha256': hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
              'pdf_page': args.page, 'crop_pt': args.crop, 'coordinate_origin': 'bottom-left, rotation normalized'}
    provenance.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()

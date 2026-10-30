"""Compile with local XeLaTeX; record checks and optionally render every page.

Standard library is sufficient for compilation. pypdf/pdfplumber/Pillow are
optional inspections, Poppler is required only for --render. No network use.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def tool_path(name, override=None):
    if override:
        path = Path(override).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return str(path)
    return shutil.which(name)


def inspect_pdf(pdf, summary):
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf)
        summary['pages'] = len(reader.pages)
        summary['page_sizes_pt'] = [[round(float(p.mediabox.width), 2), round(float(p.mediabox.height), 2)] for p in reader.pages]
    except ImportError:
        summary['pdf_structure_check'] = 'unavailable: pypdf'
    try:
        import pdfplumber
        geometry = []
        low_dpi = []
        with pdfplumber.open(pdf) as doc:
            summary['pages'] = len(doc.pages)
            for n, page in enumerate(doc.pages, 1):
                outside = [c for c in page.chars if c['x0'] < -0.5 or c['x1'] > page.width + 0.5 or c['top'] < -0.5 or c['bottom'] > page.height + 0.5]
                # Footer is expected in the last 11 pt; flag adjacent body text.
                near_footer = [c for c in page.chars if page.height - 20 < c['bottom'] and c['top'] < page.height - 11 and c['size'] >= 8]
                if outside or near_footer:
                    geometry.append({'page': n, 'outside_count': len(outside), 'near_footer_count': len(near_footer)})
                for img in page.images:
                    src = img.get('srcsize')
                    if not src or img['width'] <= 0 or img['height'] <= 0:
                        continue
                    dpi = min(src[0] / img['width'] * 72, src[1] / img['height'] * 72)
                    if dpi < 120:
                        low_dpi.append({'page': n, 'effective_dpi': round(dpi, 1)})
        summary['geometry_flags'] = geometry
        summary['low_resolution_images'] = low_dpi
    except ImportError:
        summary['geometry_check'] = 'unavailable: pdfplumber'


def render_pdf(pdf, destination, renderer, summary):
    if not renderer:
        summary['render_status'] = 'unavailable: pdftoppm (Poppler)'
        return
    destination.mkdir()
    r = subprocess.run([renderer, '-png', '-r', '150', str(pdf), str(destination/'page')], capture_output=True, timeout=180)
    (destination/'render-console.txt').write_bytes(r.stdout + r.stderr)
    if r.returncode:
        summary['render_status'] = 'failed; see render-console.txt'
        return
    paths = sorted(destination.glob('page-*.png'), key=lambda x: int(x.stem.split('-')[-1]))
    summary['render_status'] = 'completed'
    summary['rendered_pages'] = len(paths)
    try:
        from PIL import Image, ImageDraw
        columns = 3
        # Split contact sheets so long reports still have legible thumbnails.
        for start in range(0, len(paths), 12):
            batch = paths[start:start+12]
            sheet = Image.new('RGB', (columns*500, ((len(batch)+columns-1)//columns)*310), '#eeeeee')
            for i, path in enumerate(batch):
                with Image.open(path) as source:
                    tile = source.convert('RGB')
                    tile.thumbnail((480, 280))
                    x, y = (i%columns)*500, (i//columns)*310
                    sheet.paste(tile, (x+(500-tile.width)//2, y+22))
                    ImageDraw.Draw(sheet).text((x+10, y+5), path.stem, fill='black')
            sheet.save(destination/f'contact-{start//12+1:02}.png')
    except ImportError:
        summary['contact_sheet'] = 'unavailable: Pillow; individual pages exist'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tex', type=Path)
    p.add_argument('--output-dir', type=Path, help='Must not already exist')
    p.add_argument('--xelatex', help='Explicit local executable')
    p.add_argument('--pdftoppm', help='Explicit Poppler executable')
    p.add_argument('--render', action='store_true')
    args = p.parse_args()
    tex = args.tex.resolve()
    if not tex.is_file():
        p.error(f'Source not found: {tex}')
    engine = tool_path('xelatex', args.xelatex)
    if not engine:
        p.error('XeLaTeX unavailable. Add the existing TeX Live bin directory to PATH or pass --xelatex.')
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    output = (args.output_dir or tex.parent/'build'/stamp).resolve()
    if output.exists():
        p.error(f'Output exists; refuse to replace an old PDF: {output}')
    output.mkdir(parents=True)
    summary = {'source': str(tex), 'output_dir': str(output), 'engine': engine, 'compiled': False,
               'visual_review_required': True, 'warnings': {}, 'render_status': 'not requested'}
    exit_code = 0
    try:
        env = os.environ.copy()
        # Keep kpathsea's default lookup and add the project root explicitly.
        env['TEXINPUTS'] = str(tex.parent) + os.pathsep + env.get('TEXINPUTS', '') + os.pathsep
        for n in [1, 2]:
            result = subprocess.run([engine, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error',
                                     '-file-line-error', '-synctex=1', f'-output-directory={output}', tex.name],
                                    cwd=tex.parent, env=env, capture_output=True, timeout=120)
            (output/f'console-pass{n}.txt').write_bytes(result.stdout + result.stderr)
            if result.returncode:
                raise RuntimeError(f'XeLaTeX pass {n} failed; see console-pass{n}.txt')
        pdf = output / (tex.stem + '.pdf')
        if not pdf.is_file():
            raise RuntimeError('Compiler produced no PDF')
        log = (output / (tex.stem + '.log')).read_text(encoding='utf-8', errors='replace')
        patterns = {
            'overfull': r'Overfull \\[hv]box[^\n]*',
            'underfull': r'Underfull \\[hv]box[^\n]*',
            'missing_glyph': r'Missing character:[^\n]*',
            'unresolved_reference': r'[^\n]*(?:undefined references|Citation[^\n]*undefined|Reference[^\n]*undefined)[^\n]*',
            'rerun': r'[^\n]*(?:Rerun to get|Please rerun|Label\(s\) may have changed)[^\n]*',
            'missing_asset': r'[^\n]*GM-MISSING-ASSET[^\n]*',
            'font_warning': r'LaTeX Font Warning:[^\n]*',
        }
        summary['warnings'] = {k: re.findall(v, log, re.IGNORECASE) for k, v in patterns.items()}
        summary.update(compiled=True, pdf=str(pdf), pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
        inspect_pdf(pdf, summary)
        if args.render:
            render_pdf(pdf, output/'preview', tool_path('pdftoppm', args.pdftoppm), summary)
        flagged = any(summary['warnings'][k] for k in ['overfull', 'missing_glyph', 'unresolved_reference', 'rerun', 'missing_asset'])
        summary['automatic_check'] = 'needs review' if flagged or summary.get('geometry_flags') else 'no flagged issues'
        if flagged:
            exit_code = 2
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        summary['error'] = str(error)
        exit_code = 1
    finally:
        (output/'build-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())

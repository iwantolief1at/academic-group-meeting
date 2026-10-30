"""Convert explicitly selected CSV columns to a booktabs table, preserving values."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def escape(value):
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
                    '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(c, c) for c in value)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv', type=Path)
    p.add_argument('--columns', nargs='+', required=True, help='Exact CSV headers, in display order')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--limit', type=int, help='Explicitly select the first N rows; recorded in provenance')
    p.add_argument('--demo', action='store_true', help='Add a visible demo caption')
    args = p.parse_args()
    output = args.output.resolve()
    provenance = output.with_suffix('.provenance.json')
    if output.exists() or provenance.exists():
        p.error('Output or provenance exists; choose new paths')
    if args.limit is not None and args.limit < 1:
        p.error('--limit must be positive')
    with args.csv.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            p.error('Missing or duplicate CSV headers')
        missing = set(args.columns) - set(reader.fieldnames)
        if missing:
            p.error(f'Unknown columns: {sorted(missing)}')
        rows = list(reader)
    if any(None in row for row in rows):
        p.error('Some rows have extra cells; check CSV quoting/delimiter')
    selected = rows if args.limit is None else rows[:args.limit]
    if not selected:
        p.error('CSV has no result rows')
    lines = ['% Generated from CSV; no numeric aggregation or precision change.']
    if args.demo:
        lines.append(r'\textcolor{GMOrange}{演示数据，非真实实验结果}\par\medskip')
    lines += [r'\begin{tabular}{'+'l'*len(args.columns)+'}', r'\toprule',
              ' & '.join(escape(c) for c in args.columns) + r' \\', r'\midrule']
    for row in selected:
        values = [row.get(c) for c in args.columns]
        lines.append(' & '.join(escape(v) if v not in [None, ''] else '未提供' for v in values) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}', '']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(lines), encoding='utf-8')
    meta = {'source': str(args.csv.resolve()), 'source_sha256': hashlib.sha256(args.csv.read_bytes()).hexdigest(),
            'columns': args.columns, 'source_rows': len(rows), 'rendered_rows': len(selected), 'limit': args.limit,
            'demo': args.demo, 'transform': 'TeX escape only; empty cells labelled missing'}
    provenance.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()

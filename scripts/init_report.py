"""Create a self-contained report. Existing targets are never overwritten."""
import argparse
import json
from pathlib import Path
import shutil


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=['paper', 'experiment'], required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = args.output.resolve()
    if target.exists():
        p.error(f'Target already exists; choose a new version directory: {target}')
    target.mkdir(parents=True)
    for source in (root / 'assets/templates/common').iterdir():
        shutil.copy2(source, target / source.name)
    for folder in ['content', 'figures', 'data', 'qa']:
        (target / folder).mkdir()
    shutil.copy2(root / f'assets/templates/{args.mode}-slides.tex', target / 'content/slides.tex')
    report = {
        'schema_version': 1, 'mode': args.mode, 'status': 'draft',
        'title': None, 'date': None, 'focus': [],
        'missing_information': ['User source materials and report metadata'],
        'slides': [],
    }
    (target / 'data/report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (target / 'data/sources.json').write_text('[]\n', encoding='utf-8')
    print(f'Created {target}\nEdit report.tex and content/slides.tex; maintain data/report.json and data/sources.json.')


if __name__ == '__main__':
    main()

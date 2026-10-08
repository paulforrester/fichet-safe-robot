#!/usr/bin/env python3
"""
Checks that every project document carries the current project revision
(the ID in REVISION at the repo root; see docs/revisions.md).

    python3 tools/check_revision.py

Markdown files need a line starting '> **Revision <ID>**'. Generated drawings
are checked for the ID anywhere in the file (they print it in their title
block). Exit code 1 if anything is missing or stale.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = open(os.path.join(ROOT, 'REVISION')).read().strip()
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'runs'}
DRAWINGS = ['control/harness/schematic.pdf', 'control/harness/harness.svg',
            'control/harness/overview.svg', 'control/harness/hub_board.svg']


def main():
    bad = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if not f.endswith('.md'):
                continue
            p = os.path.join(d, f)
            rel = os.path.relpath(p, ROOT)
            head = open(p, encoding='utf-8').read().splitlines()[:12]
            m = [l for l in head if l.startswith('> **Revision ') or l.startswith('> **Project revision ')]
            if not m:
                bad.append(f'{rel}: no revision line')
            elif REV not in m[0]:
                bad.append(f'{rel}: stale ({m[0][:46]}...)')
    for rel in DRAWINGS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            bad.append(f'{rel}: missing')
            continue
        raw = open(p, 'rb').read()
        text = raw.decode('utf-8', 'ignore')
        if p.endswith('.svg'):
            import html
            text = html.unescape(text)
        if REV not in text and REV.encode() not in raw:
            bad.append(f'{rel}: revision {REV} not found (regenerate it)')
    print(f'project revision {REV}')
    for b in bad:
        print('  ' + b)
    print('RESULT:', 'OK' if not bad else f'{len(bad)} document(s) to update')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

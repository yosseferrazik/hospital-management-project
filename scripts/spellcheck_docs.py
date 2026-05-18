#!/usr/bin/env python3
# Spellcheck documentation files.
# Usage: python3 scripts/spellcheck_docs.py

import re
import os
from collections import Counter, defaultdict
from spellchecker import SpellChecker

DOCS_DIR = 'docs'
spell = SpellChecker(language='en')

md_files = [os.path.join(root, f) for root, dirs, files in os.walk(DOCS_DIR) for f in files if f.lower().endswith('.md')]

report = defaultdict(Counter)
for path in md_files:
    in_code = False
    for line in open(path, encoding='utf-8'):
        if line.strip().startswith('```'):
            in_code = not in_code; continue
        if in_code: continue
        line = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line)
        line = re.sub(r'`[^`]*`', '', line)
        for w in spell.unknown([w.lower() for w in re.findall(r"[A-Za-z]{2,}", line) if not w.isupper()]):
            report[path][w] += 1

print(f'# Spellcheck report ({len(md_files)} files)')
print()
total = sum(report.values(), Counter())
print('Top misspellings:')
for word, n in total.most_common(50):
    print(f'  {word}: {n}')

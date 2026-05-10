import re
import os
from collections import Counter, defaultdict
from spellchecker import SpellChecker

DOCS_DIR = 'docs'

spell = SpellChecker(language='en')

md_files = []
for root, dirs, files in os.walk(DOCS_DIR):
    for f in files:
        if f.lower().endswith('.md'):
            md_files.append(os.path.join(root, f))

report = defaultdict(Counter)

for path in md_files:
    code_block = False
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            if line.strip().startswith('```'):
                code_block = not code_block
                continue
            if code_block:
                continue
            # Remove Markdown links and inline code
            line = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line)
            line = re.sub(r'`[^`]*`', '', line)
            # extract words (simple)
            words = re.findall(r"[A-Za-z]{2,}", line)
            words = [w for w in words if not w.isupper()]
            miss = spell.unknown([w.lower() for w in words])
            for m in miss:
                report[path][m] += 1

# Summarize
total = Counter()
for p, cnt in report.items():
    total.update(cnt)

print('# Spellcheck report (english dictionary, code blocks ignored)')
print()
print('Files scanned:', len(md_files))
print()
print('Top global misspellings:')
for word, n in total.most_common(50):
    print(f'{word}: {n}')

print('\nPer-file highlights:')
for p, cnt in report.items():
    if not cnt:
        continue
    print('\n==', p)
    for w, n in cnt.most_common(20):
        print(f'  {w}: {n}')

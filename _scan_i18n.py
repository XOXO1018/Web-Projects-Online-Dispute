import re

with open(r'c:\Users\30742\Desktop\ZJFLv1.1\frontend\src\i18n\index.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all string values with special chars
for i, line in enumerate(lines, 1):
    for m in re.finditer(r":\s*'([^']+)'", line):
        val = m.group(1)
        if '@' in val or '|' in val or '{' in val:
            print(f'{i}: {line.strip()[:150]}')

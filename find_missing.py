import re
import os

with open(r'base\api\views.py', encoding='utf-8') as f:
    views_content = f.read()

with open(r'base\api\serializers.py', encoding='utf-8') as f:
    serializers_content = f.read()

with open(r'locale\ar\LC_MESSAGES\django.po', encoding='utf-8') as f:
    po_content = f.read()

words = re.findall(r'_\([\s\n]*[\"\'](.*?)[\"\'][\s\n]*\)', views_content + serializers_content)
all_po = re.findall(r'msgid [\"\'](.*?)[\"\']', po_content)

missing = set()
for w in words:
    if w not in all_po:
        missing.add(w)

for m in missing:
    print(f"MISSING: {m}")

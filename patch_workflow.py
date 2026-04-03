import sys

with open('/tmp/okna-plus-opt/.github/workflows/freelancer-guard.yml', 'r') as f:
    content = f.read()

old = "  push:\n    branches: ['**']\n  delete:"
new = "  push:\n    branches: ['**']\n    paths-ignore:\n      - '**.md'\n      - '**.txt'\n      - '**.png'\n      - '**.jpg'\n      - '**.gif'\n  delete:"

if old not in content:
    print("ERROR: pattern not found")
    sys.exit(1)

patched = content.replace(old, new, 1)

with open('/tmp/okna-plus-opt/.github/workflows/freelancer-guard.yml', 'w') as f:
    f.write(patched)

print("OK: paths-ignore added")

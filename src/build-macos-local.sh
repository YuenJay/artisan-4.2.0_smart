#!/bin/bash
set -e
python3 -V

echo "************* build derived files **************"
# ./build-derived.sh macos

rm -rf build dist
sleep .3

echo "************* generate signature **************"
python generate_signature.py

echo "************* pyinstaller **************"
pyinstaller -y --log-level=INFO artisan-mac.spec

# 检查 dmg
version=$(python3 -c "import artisanlib; print(artisanlib.__version__)")
dmg_file=$(ls *.dmg 2>/dev/null | head -n1)
if [ -z "$dmg_file" ]; then
    echo "No .dmg found"
    exit 1
fi
size=$(($(du -k "$dmg_file" | cut -f1) * 1024))
echo "$dmg_file size: $size bytes"

#!/bin/sh

best_version=""
best_exe=""

for version in "" 3 3.{8..13}; do
    exe="python$version"
    ver_info=$($exe -c 'import sys; print(sys.version_info[:])' 2>/dev/null)
    if [ $? -eq 0 ]; then
        major_minor=$(echo $ver_info | tr -d '(), ')
        if [ -z "$best_version" ] || [ "$major_minor" \> "$best_version" ]; then
            best_version=$major_minor
            best_exe=$exe
        fi
    fi
done

if [ -n "$best_exe" ]; then
    echo "Best Python executable: $best_exe (version $best_version)"
else
    echo "No suitable Python version found."
fi

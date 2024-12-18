bv=""
bx=""

for version in "" 3 3.{8..13}; do
    x="python$version"
    v=$($x -c "import sys; print(sys.version_info[:])" 2>/dev/null)
    if [ $? -eq 0 ]; then
        cv=$(echo $v | tr -d "(), ")
        if [ -z "$bv" ] || [ "$cv" \> "$bv" ]; then
            bv=$cv
            bx=$x
        fi
    fi
done

if [ -z "$bx" ]; then
    echo "no python" >&2
    exit 1
fi

exec "$bx" "$@"

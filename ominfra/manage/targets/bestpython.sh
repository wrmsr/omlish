bv=""
bx=""

for v in "" 3 3.{8..13}; do
    x="python$v"
    v=$($x -c "import sys; print((\"%02d\" * 3) % sys.version_info[:3])" 2>/dev/null)
    if [ $? -eq 0 ] && [ "$v" \> 030799 ] && ([ -z "$bv" ] || [ "$v" \> "$bv" ]); then
        bv=$v
        bx=$x
    fi
done

if [ -z "$bx" ]; then
    echo "no python" >&2
    exit 1
fi

exec "$bx" "$@"

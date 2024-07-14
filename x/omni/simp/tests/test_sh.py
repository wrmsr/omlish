"""
https://github.com/docker-library/busybox/blob/844e23eae6a28fd1faf9b25f8ed977ae4b168a0f/stable/uclibc/Dockerfile
https://git.busybox.net/busybox/tree/shell/ash.c

ARRAY=( "cow:moo"
        "dinosaur:roar"
        "bird:chirp"
        "bash:rock" )

for animal in "${ARRAY[@]}" ; do
    KEY=${animal%%:*}
    VALUE=${animal#*:}
    printf "%s likes to %s.\n" "$KEY" "$VALUE"
done

echo -e "${ARRAY[1]%%:*} is an extinct animal which likes to ${ARRAY[1]#*:}\n"
"""
import ast
import inspect

from ..pyasts import translate


def barf():
    a = 'hi'
    b = 'why'
    c = a + b
    print(c)


def test_sh():
    a = translate(ast.parse(inspect.getsource(barf)))
    print(a)

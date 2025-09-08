"""
https://docs.python.org/3.14/library/concurrent.interpreters.html#module-concurrent.interpreters
"""
import concurrent.interpreters  # noqa
import resource
import textwrap


def get_memory_usage():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    memory_usage_kb = usage.ru_maxrss
    return memory_usage_kb


def do_interp_stuff(interp):
    ##
    # Run in the current OS thread.

    interp.exec('print("spam!")')

    interp.exec(textwrap.dedent("""
    if True:
        print('spam!')
    """))

    interp.exec(textwrap.dedent("""
        print('spam!')
    """))

    def run(arg):
        return arg

    res = interp.call(run, 'spam!')
    print(res)

    def run():
        print('spam!')

    interp.call(run)

    ##
    # Run in new OS thread.

    t = interp.call_in_thread(run)
    t.join()


def _main() -> None:
    interp = concurrent.interpreters.create()  # noqa
    do_interp_stuff(interp)
    interp.close()

    start_mem = get_memory_usage()
    n_interps = 5
    interps = [
        concurrent.interpreters.create()  # noqa
        for _ in range(n_interps)
    ]
    end_mem = get_memory_usage()
    print(f'{(end_mem-start_mem)//n_interps=:_} B')
    for i in interps:
        i.close()


if __name__ == '__main__':
    _main()

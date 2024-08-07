def new_function_wrapper(func_name, disp_dispatch):
    def inner(*args, **kwargs):
        if not args:
            raise TypeError(f'{func_name} requires at least 1 positional argument')
        if (impl := disp_dispatch(type(args[0]))) is not None:
            return impl(*args, **kwargs)
        raise RuntimeError(f'No dispatch: {type(args[0])}')
    return inner

from .imports.proxy import auto_proxy_init as _auto_proxy_init


with _auto_proxy_init(globals(), update_exports=True):
    ##

    from .asyncs import (  # noqa
        as_async,

        AsyncGeneratorWithReturn,
        async_generator_with_return,

        sync_await,
    )

    from .attrstorage import (  # noqa
        AttributePresentError,
        SetAttrIfPresent,
        set_attr,

        AttrStorage,

        StdAttrStorage,
        STD_ATTR_STORAGE,

        DictAttrStorage,

        TransientDict,
        TransientAttrStorage,
        TRANSIENT_ATTR_STORAGE,
        transient_delattr,
        transient_getattr,
        transient_setattr,
    )

    from .cached.function import (  # noqa
        cached_function,
        static_init,
    )

    from .cached.property import (  # noqa
        cached_property,
    )

    from .casing import (  # noqa
        StringCasingError,
        ImproperStringCasingError,
        UnknownStringCasingError,
        AmbiguousStringCasingError,

        StringCasing,
        CamelCase,
        LowCamelCase,
        SnakeCase,
        UpSnakeCase,

        STRING_CASINGS,
        CAMEL_CASE,
        LOW_CAMEL_CASE,
        SNAKE_CASE,
        UP_SNAKE_CASE,

        camel_case,
        low_camel_case,
        snake_case,
        up_snake_case,

        camel_to_snake,
        snake_to_camel,

        get_string_casing,
        split_string_casing,
    )

    from .classes.abstract import (  # noqa
        is_abstract_method,

        is_abstract_class,
        is_abstract,

        get_abstracts,
        make_abstract,
    )

    from .classes.bindable import (  # noqa
        BindableClass,
    )

    from .classes.namespaces import (  # noqa
        GenericNamespaceMeta,
        NamespaceMeta,
        Namespace,
    )

    from .classes.protocols import (  # noqa
        ProtocolForbiddenAsBaseClass,
        ProtocolForbiddenAsBaseClassTypeError,
    )

    from .classes.restrict import (  # noqa
        FinalTypeError,
        Final,

        SealedError,
        Sealed,
        PackageSealed,

        NotInstantiable,
        NotPicklable,

        NoBool,
        no_bool,

        SENSITIVE_ATTR,
        Sensitive,
        AnySensitive,
    )

    from .classes.simple import (  # noqa
        SimpleMetaDict,

        Marker,

        Singleton,
        LazySingleton,
    )

    from .classes.virtual import (  # noqa
        Virtual,
        virtual_check,

        Descriptor,
        Picklable,

        Callable,
    )

    from .clsdct import (  # noqa
        is_possibly_cls_dct,
        get_caller_cls_dct,

        ClassDctFn,
        cls_dct_fn,
    )

    from .collections import (  # noqa
        yield_dict_init,
        merge_dicts,

        empty_map,
    )

    from .comparison import (  # noqa
        cmp,

        InfinityType,
        Infinity,
        NegativeInfinityType,
        NegativeInfinity,
    )

    from .contextmanagers import (  # noqa
        ContextManaged,
        SelfContextManaged,
        ValueContextManager,
        NOP_CONTEXT_MANAGER,

        AsyncContextManaged,
        SelfAsyncContextManaged,
        ValueAsyncContextManager,
        NOP_ASYNC_CONTEXT_MANAGER,

        AsyncContextManager,

        ContextManager,

        maybe_managing,
        async_maybe_managing,
        async_or_sync_maybe_managing,

        disposing,
        breakpoint_on_exception,
        context_var_setting,

        ContextWrappable,
        ContextWrapped,
        context_wrapped,

        Lockable,
        DefaultLockable,
        default_lock,

        AsyncLockable,
        DefaultAsyncLockable,
        default_async_lock,

        Timer,

        double_check_setdefault,

        call_with_exit_stack,
        call_with_async_exit_stack,

        with_exit_stack,
        with_async_exit_stack,
    )

    from .datetimes import (  # noqa
        ISO_FMT,
        ISO_FMT_US,
        ISO_FMT_NTZ,
        ISO_FMT_US_NTZ,

        utcnow,
        utcfromtimestamp,
    )

    from .descriptors import (  # noqa
        attr_property,
        item_property,

        is_method_descriptor,
        unwrap_method_descriptors,

        unwrap_func_with_partials,
        unwrap_func,

        unwrap_callable_with_partials,
        unwrap_callable,

        update_wrapper,

        decorator,

        AccessForbiddenError,
        access_forbidden,

        classonly,
    )

    from .enums import (  # noqa
        enum_name_repr,
    )

    from .errors import (  # noqa
        DuplicateKeyError,
    )

    from .functions import (  # noqa
        is_lambda,

        call_with,
        opt_call,
        opt_fn,
        recurse,

        raise_,
        raising,
        try_,
        finally_,

        identity,
        constant,
        nullary_constant,

        is_none,
        is_not_none,
        isinstance_of,
        issubclass_of,
        strict_eq,

        VoidError,
        Void,
        void,

        periodically,

        opt_getattr,
        coalesce,
        opt_coalesce,

        cond_kw,
        opt_kw,
        truthy_kw,

        new_function,
        new_function_kwargs,
        copy_function,
    )

    from .generators import (  # noqa
        nextgen,
        autostart,

        GeneratorLike,

        capture_generator,
        capture_coroutine,

        GeneratorMappedIterator,
        genmap,
    )

    from .imports.capture import (  # noqa
        ImportCaptureError,
        ImportCaptureErrors,
        ImportCapture,
    )

    from .imports.conditional import (  # noqa
        register_conditional_import,
        trigger_conditional_imports,
    )

    from .imports.lazy import (  # noqa
        lazy_import,
    )

    from .imports.proxy import (  # noqa
        proxy_import,
        auto_proxy_import,

        proxy_init,
        auto_proxy_init,
    )

    from .imports.resolving import (  # noqa
        can_import,
        get_real_module_name,
        resolve_import_name,
        try_import,
    )

    from .imports.traversal import (  # noqa
        import_all,
        yield_import_all,
        yield_importable,
    )

    from .iterables import (  # noqa
        ilen,
        take,
        consume,
        peek,
        chunk,
        interleave,
        renumerate,
        common_prefix_len,

        readiter,

        itergen,

        flatten,
        flatmap,

        asrange,
        prodrange,

        IteratorWithReturn,
    )

    from .lazyglobals import (  # noqa
        AmbiguousLazyGlobalsFallbackError,
        LazyGlobals,
    )

    from .maybes import (  # noqa
        empty,
        just,
    )

    from .maysync import (  # noqa
        make_maysync_fn,
        make_maysync_generator_fn,
        make_maysync,

        make_maysync_from_sync,
    )

    from .objects import (  # noqa
        arg_repr,
        opt_repr,

        can_weakref,

        new_type,
        super_meta,

        deep_subclasses,

        SimpleProxy,

        anon_object,

        Identity,
    )

    from .outcomes import (  # noqa
        OutcomeAlreadyUnwrappedError,

        capture,
        acapture,

        Outcome,

        Value,
        value,

        Error,
        error,

        Either,
    )

    from .overrides import (  # noqa
        needs_override,

        is_override,

        RequiresOverrideError,
        RequiresOverride,
    )

    from .params import (  # noqa
        CanParamSpec,

        Param,

        VarParam,
        ArgsParam,
        KwargsParam,

        ValParam,
        PosOnlyParam,
        KwOnlyParam,

        ParamSeparator,

        ParamSpec,

        param_render,
    )

    from .recursion import (  # noqa
        LimitedRecursionError,
        recursion_limiting_context,

        recursion_limiting,
    )

    from .resolving import (  # noqa
        ResolvableClassNameError,
        get_cls_fqcn,
        get_fqcn_cls,
        Resolvable,
    )

    from .resources import (  # noqa
        ReadableResource,
        get_package_resources,
        get_relative_resources,
    )

    from .sequences import (  # noqa
        iterslice,
        iterrange,

        SeqView,
    )

    from .strings import (  # noqa
        prefix_delimited,
        prefix_lines,
        indent_lines,

        strip_prefix,
        strip_suffix,

        replace_many,

        find_any,
        rfind_any,

        is_dunder,
        is_sunder,

        is_ident_start,
        is_ident_cont,
        is_ident,

        BOOL_STRINGS,
        BOOL_FALSE_STRINGS,
        BOOL_TRUE_STRINGS,
        STRING_BOOL_VALUES,

        iter_pat,
    )

    from .sys import (  # noqa
        REQUIRED_PYTHON_VERSION,
        check_runtime_version,
        is_gil_enabled,
    )

    from .typing import (  # noqa
        BytesLike,

        static_check_isinstance,
        static_check_issubclass,
        copy_type,

        protocol_check,

        typed_lambda,
        typed_partial,

        SequenceNotStr,
    )

    ##

    from ..lite.abstract import (  # noqa
        is_abstract_method,
        update_abstracts,

        AbstractTypeError,
        Abstract,
    )

    from ..lite.args import (  # noqa
        Args,
    )

    from ..lite.asyncs import (  # noqa
        opt_await,
        async_list,
        async_enumerate,

        SyncAwaitCoroutineNotTerminatedError,

        sync_aiter,
        sync_async_list,

        SyncAwaitContextManager,
        sync_async_with,

        SyncToAsyncContextManager,
        as_async_context_manager,
    )

    from ..lite.attrops import (  # noqa
        AttrOps,
        attr_ops,

        attr_repr,
    )

    from ..lite.contextmanagers import (  # noqa
        AsyncExitStacked,
        ExitStacked,
        adefer,
        attr_setting,
        defer,
    )

    from ..lite.imports import (  # noqa
        import_attr,
        import_module,
        import_module_attr,
    )

    from ..lite.maybes import (  # noqa
        Maybe,
    )

    from ..lite.maysync import (  # noqa
        AnyMaysyncFn,

        MaywaitableAlreadyConsumedError,
        AnyMaywaitable,

        MaysyncFn,
        Maywaitable,

        MaysyncGeneratorFn,
        MaysyncGenerator,

        is_running_maysync,

        run_maysync,

        RunMaysyncContextManager,
        run_maysync_context_manager,

        mark_maysync,
        is_maysync,
    )

    from ..lite.objects import (  # noqa
        mro_dict,
        mro_owner_dict,
        dir_dict,
    )

    from ..lite.timeouts import (  # noqa
        DeadlineTimeout,
        InfiniteTimeout,
        Timeout,
        TimeoutLike,
    )

    from ..lite.types import (  # noqa
        BUILTIN_SCALAR_ITERABLE_TYPES,
    )

    from ..lite.typing import (  # noqa
        AnyFunc,
        Func0,
        Func1,
        Func2,
        Func3,

        typing_annotations_attr,
    )

    from ..lite.wrappers import (  # noqa
        update_wrapper_no_annotations,
    )

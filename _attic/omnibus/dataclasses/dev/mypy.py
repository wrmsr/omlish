import typing as ta

import mypy.nodes as mn
import mypy.plugin as mp
import mypy.plugins.common as mpc
import mypy.types as mt
import mypy.server.trigger as mst

from ... import check


# The set of decorators that generate dataclasses.
dataclass_makers = {
    'dataclass',
    'dataclasses.dataclass',
}

SELF_TVAR_NAME = '_DT'

PREFIX = '.'.join(__package__.split('.')[:2])


class DataclassAttribute:

    def __init__(
            self,
            name: str,
            is_in_init: bool,
            is_init_var: bool,
            has_default: bool,
            line: int,
            column: int,
            type: ta.Optional[mt.Type],
    ) -> None:
        super().__init__()

        self.name = name
        self.is_in_init = is_in_init
        self.is_init_var = is_init_var
        self.has_default = has_default
        self.line = line
        self.column = column
        self.type = type

    def to_argument(self) -> mn.Argument:
        return mn.Argument(
            variable=self.to_var(),
            type_annotation=self.type,
            initializer=None,
            kind=mn.ARG_OPT if self.has_default else mn.ARG_POS,
        )

    def to_var(self) -> mn.Var:
        return mn.Var(self.name, self.type)

    def serialize(self) -> mn.JsonDict:
        check.not_none(self.type)
        return {
            'name': self.name,
            'is_in_init': self.is_in_init,
            'is_init_var': self.is_init_var,
            'has_default': self.has_default,
            'line': self.line,
            'column': self.column,
            'type': self.type.serialize(),
        }

    @classmethod
    def deserialize(
            cls, info: mn.TypeInfo, data: mn.JsonDict, api: mp.SemanticAnalyzerPluginInterface
    ) -> 'DataclassAttribute':
        data = data.copy()
        typ = mpc.deserialize_and_fixup_type(data.pop('type'), api)
        return cls(type=typ, **data)


class _NotYetReady(Exception):
    pass


class DataclassTransformer:

    def __init__(self, ctx: mp.ClassDefContext) -> None:
        super().__init__()

        self._ctx = ctx

    def transform(self) -> None:
        """Apply all the necessary transformations to the underlying dataclass so as to ensure it is fully type checked
        according to the rules in PEP 557.
        """

        ctx = self._ctx
        info = self._ctx.cls.info
        attributes = self.collect_attributes()
        if attributes is None:
            # Some definitions are not ready, defer() should be already called.
            return
        for attr in attributes:
            if attr.type is None:
                ctx.api.defer()
                return

        decorator_arguments = {
            'init': mpc._get_decorator_bool_argument(self._ctx, 'init', True),
            'eq': mpc._get_decorator_bool_argument(self._ctx, 'eq', True),
            'order': mpc._get_decorator_bool_argument(self._ctx, 'order', False),
            'frozen': mpc._get_decorator_bool_argument(self._ctx, 'frozen', False),
        }

        # If there are no attributes, it may be that the semantic analyzer has not processed them yet. In order to work
        # around this, we can simply skip generating __init__ if there are no attributes, because if the user truly did
        # not define any, then the object default __init__ with an empty signature will be present anyway.
        if (
                decorator_arguments['init'] and
                ('__init__' not in info.names or info.names['__init__'].plugin_generated) and
                attributes
        ):
            mpc.add_method(
                ctx,
                '__init__',
                args=[attr.to_argument() for attr in attributes if attr.is_in_init],
                return_type=mt.NoneType(),
            )

        if decorator_arguments['eq'] and info.get('__eq__') is None or decorator_arguments['order']:
            # Type variable for self types in generated methods.
            obj_type = ctx.api.named_type('__builtins__.object')
            self_tvar_expr = mn.TypeVarExpr(SELF_TVAR_NAME, info.fullname + '.' + SELF_TVAR_NAME, [], obj_type)
            info.names[SELF_TVAR_NAME] = mn.SymbolTableNode(mn.MDEF, self_tvar_expr)

        # Add <, >, <=, >=, but only if the class has an eq method.
        if decorator_arguments['order']:
            if not decorator_arguments['eq']:
                ctx.api.fail('eq must be True if order is True', ctx.cls)

            for method_name in ['__lt__', '__gt__', '__le__', '__ge__']:
                # Like for __eq__ and __ne__, we want "other" to match the self type.
                obj_type = ctx.api.named_type('__builtins__.object')
                order_tvar_def = mt.TypeVarDef(SELF_TVAR_NAME, info.fullname + '.' + SELF_TVAR_NAME, -1, [], obj_type)
                order_other_type = mt.TypeVarType(order_tvar_def)
                order_return_type = ctx.api.named_type('__builtins__.bool')
                order_args = [
                    mn.Argument(mn.Var('other', order_other_type), order_other_type, None, mn.ARG_POS)
                ]

                existing_method = info.get(method_name)
                if existing_method is not None and not existing_method.plugin_generated:
                    check.no_empty(existing_method.node)
                    ctx.api.fail(
                        'You may not have a custom %s method when order=True' % method_name,
                        existing_method.node,
                    )

                mpc.add_method(
                    ctx,
                    method_name,
                    args=order_args,
                    return_type=order_return_type,
                    self_type=order_other_type,
                    tvar_def=order_tvar_def,
                )

        if decorator_arguments['frozen']:
            self._freeze(attributes)

        self.reset_init_only_vars(info, attributes)

        info.metadata['dataclass'] = {
            'attributes': [attr.serialize() for attr in attributes],
            'frozen': decorator_arguments['frozen'],
        }

    def reset_init_only_vars(self, info: mn.TypeInfo, attributes: ta.List[DataclassAttribute]) -> None:
        """Remove init-only vars from the class and reset init var declarations."""

        for attr in attributes:
            if attr.is_init_var:
                if attr.name in info.names:
                    del info.names[attr.name]
                else:
                    # Nodes of superclass InitVars not used in __init__ cannot be reached.
                    check.state(attr.is_init_var)
                for stmt in info.defn.defs.body:
                    if isinstance(stmt, mn.AssignmentStmt) and stmt.unanalyzed_type:
                        lvalue = stmt.lvalues[0]
                        if isinstance(lvalue, mn.NameExpr) and lvalue.name == attr.name:
                            # Reset node so that another semantic analysis pass will recreate a symbol node for this
                            # attribute.
                            lvalue.node = None

    def collect_attributes(self) -> ta.Optional[ta.List[DataclassAttribute]]:
        """Collect all attributes declared in the dataclass and its parents.

        All assignments of the form

          a: SomeType
          b: SomeOtherType = ...

        are collected.
        """

        attrs: ta.List[DataclassAttribute] = []
        for stmt in self._ctx.cls.defs.body:
            try:
                attr = self._build_stmt_attr(stmt)
            except _NotYetReady:
                return None
            if attr is not None:
                attrs.append(attr)

        known_attrs: ta.Set[str] = {a.name for a in attrs}

        # Next, collect attributes belonging to any class in the MRO as long as those attributes weren't already
        # collected.  This makes it possible to overwrite attributes in subclasses. # copy() because we potentially
        # modify all_attrs below and if this code requires debugging we'll have unmodified attrs laying around.
        all_attrs = attrs.copy()
        for info in self._ctx.cls.info.mro[1:-1]:
            if 'dataclass' not in info.metadata:
                continue

            super_attrs = []
            # Each class depends on the set of attributes in its dataclass ancestors.
            self._ctx.api.add_plugin_dependency(mst.make_wildcard_trigger(info.fullname))

            for data in info.metadata['dataclass']['attributes']:
                name = data['name']  # type: str
                if name not in known_attrs:
                    attr = DataclassAttribute.deserialize(info, data, self._ctx.api)
                    known_attrs.add(name)
                    super_attrs.append(attr)
                elif all_attrs:
                    # How early in the attribute list an attribute appears is determined by the reverse MRO, not simply
                    # MRO. See https://docs.python.org/3/library/dataclasses.html#inheritance for details.
                    for attr in all_attrs:
                        if attr.name == name:
                            all_attrs.remove(attr)
                            super_attrs.append(attr)
                            break
            all_attrs = super_attrs + all_attrs

        # Ensure that arguments without a default don't follow arguments that have a default.
        found_default = False
        for attr in all_attrs:
            # If we find any attribute that is_in_init but that doesn't have a default after one that does have one,
            # then that's an error.
            if found_default and attr.is_in_init and not attr.has_default:
                # If the issue comes from merging different classes, report it at the class definition point.
                context = mn.Context(line=attr.line, column=attr.column) if attr in attrs else self._ctx.cls
                self._ctx.api.fail(
                    'Attributes without a default cannot follow attributes with one',
                    context,
                )

            found_default = found_default or (attr.has_default and attr.is_in_init)

        return all_attrs

    def _build_stmt_attr(self, stmt: mn.Statement) -> ta.Optional[DataclassAttribute]:
        # Any assignment that doesn't use the new type declaration syntax can be ignored out of hand.
        if not (isinstance(stmt, mn.AssignmentStmt) and stmt.new_syntax):
            return None

        # a: int, b: str = 1, 'foo' is not supported syntax so we don't have to worry about it.
        lhs = stmt.lvalues[0]
        if not isinstance(lhs, mn.NameExpr):
            return None

        sym = self._ctx.cls.info.names.get(lhs.name)
        if sym is None:
            # This name is likely blocked by a star import. We don't need to defer because defer() is already called by
            # mark_incomplete().
            return None

        node = sym.node
        if isinstance(node, mn.PlaceholderNode):
            # This node is not ready yet.
            raise _NotYetReady
        check.isinstance(node, mn.Var)

        # x: ClassVar[int] is ignored by dataclasses.
        if node.is_classvar:
            return None

        # x: InitVar[int] is turned into x: int and is removed from the class.
        is_init_var = False
        node_type = mt.get_proper_type(node.type)
        if (
                isinstance(node_type, mt.Instance) and
                node_type.type.fullname in (PREFIX + '.InitVar', 'dataclasses.InitVar')
        ):
            is_init_var = True
            node.type = node_type.args[0]

        has_field_call, field_args = _collect_field_args(stmt.rvalue)

        is_in_init_param = field_args.get('init')
        if is_in_init_param is None:
            is_in_init = True
        else:
            is_in_init = bool(self._ctx.api.parse_bool(is_in_init_param))

        has_default = False
        # Ensure that something like x: int = field() is rejected after an attribute with a default.
        if has_field_call:
            has_default = 'default' in field_args or 'default_factory' in field_args

        # All other assignments are already type checked.
        elif not isinstance(stmt.rvalue, mn.TempNode):
            has_default = True

        if not has_default:
            # Make all non-default attributes implicit because they are de-facto set on self in the generated
            # __init__(), not in the class body.
            sym.implicit = True

        return DataclassAttribute(
            name=lhs.name,
            is_in_init=is_in_init,
            is_init_var=is_init_var,
            has_default=has_default,
            line=stmt.line,
            column=stmt.column,
            type=sym.type,
        )

    def _freeze(self, attributes: ta.List[DataclassAttribute]) -> None:
        """Converts all attributes to @property methods in order to emulate frozen classes."""

        info = self._ctx.cls.info
        for attr in attributes:
            sym_node = info.names.get(attr.name)
            if sym_node is not None:
                var = sym_node.node
                check.isinstance(var, mn.Var)
                var.is_property = True
            else:
                var = attr.to_var()
                var.info = info
                var.is_property = True
                var._fullname = info.fullname + '.' + var.name
                info.names[var.name] = mn.SymbolTableNode(mn.MDEF, var)


def dataclass_class_maker_callback(ctx: mp.ClassDefContext) -> None:
    """Hooks into the class typechecking process to add support for dataclasses."""

    transformer = DataclassTransformer(ctx)
    transformer.transform()


def _collect_field_args(expr: mn.Expression) -> ta.Tuple[bool, ta.Dict[str, mn.Expression]]:
    """Returns a tuple where the first value represents whether or not the expression is a call to dataclass.field and
    the second is a dictionary of the keyword arguments that field() was called with.
    """

    if (
            isinstance(expr, mn.CallExpr) and
            isinstance(expr.callee, mn.RefExpr) and
            expr.callee.fullname in (PREFIX + '.field', 'dataclasses.field')
    ):
        # field() only takes keyword arguments.
        args = {}
        for i, (name, arg) in enumerate(zip(expr.arg_names, expr.args)):
            if i == 1 and name is None:
                name = 'default'
            else:
                check.not_none(name)
            args[name] = arg
        return True, args
    return False, {}


class DataclassPlugin(mp.Plugin):

    def get_class_decorator_hook(self, fullname: str) -> ta.Optional[ta.Callable[[mp.ClassDefContext], None]]:
        if fullname in [
            PREFIX + '.api.dataclass',
        ]:
            return dataclass_class_maker_callback

        return None

    def get_base_class_hook(self, fullname: str) -> ta.Optional[ta.Callable[[mp.ClassDefContext], None]]:
        stn = self.lookup_fully_qualified(fullname)
        if stn is not None:
            if isinstance(stn.node, mn.TypeInfo):
                mro = check.isinstance(stn.node, mn.TypeInfo).mro
                if any(bc.fullname == PREFIX + '.metaclass.Data' for bc in mro):
                    return dataclass_class_maker_callback

        return None

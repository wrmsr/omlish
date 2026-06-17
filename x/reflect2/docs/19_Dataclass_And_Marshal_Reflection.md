# Dataclass And Marshal Reflection

This checkpoint follows a review of the concrete old-system users that matter most for replacement: the custom
dataclasses package and the marshal package.

## Dataclass Usage

The old dataclass integration uses reflection primarily to make generic dataclass field annotations concrete in subclass
contexts.

The important path is `FieldsInspection.generic_replaced_field_type`. It:

- finds all dataclass fields and records the runtime class that owns each field;
- builds a generic-aware MRO for the inspected class;
- looks up the owner's substituted generic type in that MRO;
- computes replacements from the owner's type variables to the concrete reflected arguments;
- reflects the original field annotation;
- substitutes those replacements into the field type.

This is used by generated `__init__` methods when `generic_init` is enabled. For a base like `Box[T]` and a subclass
like `IntBox(Box[int])`, the generated initializer can expose `v: int` instead of `v: T`. That behavior is a central
replacement target, not a convenience feature.

The new system already has the core machinery needed for much of this: runtime reflection into `Instance`, substituted
MRO entries, base-argument lookup, and core type substitution. What is still missing is the dataclass-specific runtime
surface that ties those pieces together around fields and field owners.

## Marshal Usage

The marshal package uses the old reflection system as a small runtime dispatch IR. Factories inspect reflected type
shape and then recursively request marshalers or unmarshaler for contained types.

The high-value patterns are:

- unions: optionals, primitive unions, literal unions, and polymorphic unions;
- literals: finite value extraction and same-runtime-type checks for validation;
- generics: concrete class plus argument extraction for iterables, mappings, `Maybe`, and typed-value containers;
- dataclasses: generic field replacement before recursively building field marshalers;
- newtypes: unwrap to the underlying type;
- plain runtime classes: enums, dataclasses, namedtuples, metadata lookup, subclass polymorphism;
- recursive/type caches: reflected types are used as keys.

This confirms that the new reflection surface should not expose only raw mypy-like nodes. It should also provide small,
explicit runtime helper APIs for common dispatch questions, so downstream systems do not need to duplicate internal IR
knowledge.

## Direction

The next reflection work should steer toward replacing these concrete old-system affordances in small slices:

- add a dataclass field reflection helper that returns fields, owning classes, raw reflected field types, and
  generically substituted field types;
- prove `Box[T]` / `IntBox(Box[int])` field replacement at the IR level first;
- add runtime annotation emission for the subset needed by generated signatures and marshal recursion;
- add marshal-facing classifiers/extractors for optional unions, finite literals, literal unions, generic collection
  base args, runtime class recovery, and newtype unwrapping;
- keep fail-closed behavior for unsupported forms, especially when converting IR back to runtime annotations;
- revisit equality/hash/canonical key behavior before reflected nodes are broadly used as cache keys.

TypedDict coverage can sit for now. The practical path to replacing the old reflection system runs through dataclasses,
generic field substitution, literal extraction, class recovery, and collection/base argument helpers.

package marshal

import (
	stu "github.com/wrmsr/bane/core/structs"
)

func NewDefaultManager(reg *Registry) *Manager {
	sic := stu.NewStructInfoCache()

	var mfs = []MarshalerFactory{
		NewRegistryMarshalerFactory(),
		NewPrimitiveMarshalerFactory(),
		NewPointerMarshalerFactory(),
		NewIndexMarshalerFactory(),
		NewMapMarshalerFactory(),
		NewBase64MarshalerFactory(),
		NewTimeMarshalerFactory(DefaultTimeMarshalLayout),
		NewOptionalMarshalerFactory(),
		NewRegistryPolymorphismMarshalerFactory(),
		NewStructMarshalerFactory(sic),
		NewConvertUserPrimitiveMarshalerFactory(),
	}

	mf := NewTypeCacheMarshalerFactory(
		NewRecursiveMarshalerFactory(
			NewCompositeMarshalerFactory(
				FirstComposite,
				mfs...,
			)))

	var ufs = []UnmarshalerFactory{
		NewRegistryUnmarshalerFactory(),
		NewConvertPrimitiveUnmarshalerFactory(),
		NewPointerUnmarshalerFactory(),
		NewIndexUnmarshalerFactory(),
		NewMapUnmarshalerFactory(),
		NewBase64UnmarshalerFactory(),
		NewTimeUnmarshalerFactory(DefaultTimeUnmarshalLayouts()),
		NewOptionalUnmarshalerFactory(),
		NewRegistryPolymorphismUnmarshalerFactory(),
		NewStructUnmarshalerFactory(sic),
		NewConvertUserPrimitiveUnmarshalerFactory(),
	}

	uf := NewTypeCacheUnmarshalerFactory(
		NewRecursiveUnmarshalerFactory(
			NewCompositeUnmarshalerFactory(
				FirstComposite,
				ufs...,
			)))

	return &Manager{
		sic: sic,

		reg: reg,

		mf: mf,
		uf: uf,
	}
}

import typing as ta


##


ModelName = ta.NewType('ModelName', str)
FieldName = ta.NewType('FieldName', str)

TableName = ta.NewType('TableName', str)
ColumnName = ta.NewType('ColumnName', str)

#

MapperName: ta.TypeAlias = ModelName | FieldName
StoreName: ta.TypeAlias = TableName | ColumnName

ObjectName: ta.TypeAlias = ModelName | TableName
AttributeName: ta.TypeAlias = FieldName | ColumnName

#

MapperNameT = ta.TypeVar('MapperNameT', bound=MapperName)
StoreNameT = ta.TypeVar('StoreNameT', bound=StoreName)

ObjectNameT = ta.TypeVar('ObjectNameT', bound=ObjectName)
AttributeNameT = ta.TypeVar('AttributeNameT', bound=AttributeName)

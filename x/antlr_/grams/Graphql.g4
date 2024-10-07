/*
The MIT License (MIT)

Copyright (c) 2015 Joseph T. McBride

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

GraphQL grammar derived from:

GraphQL Draft Specification - July 2015

http://facebook.github.io/graphql/ https://github.com/facebook/graphql

AB:10-sep19: replaced type with type_ to resolve conflict for golang generator

AB: 13-oct-19: added type system as per June 2018 specs
AB: 26-oct-19: added ID type
AB: 30-Oct-19: description, boolean, schema & Block string fix.
    now parses: https://raw.githubusercontent.com/graphql-cats/graphql-cats/master/scenarios/validation/validation.schema.graphql
*/
grammar Graphql;


// https://spec.graphql.org/June2018/#sec-Language.Document
document
    : definition+
    ;

definition
    : executableDefinition
    | typeSystemDefinition
    | typeSystemExtension
    ;

// https://spec.graphql.org/June2018/#ExecutableDefinition
executableDefinition
    : operationDefinition
    | fragmentDefinition
    ;

// https://spec.graphql.org/June2018/#sec-Language.Operations
operationDefinition
    : operationType name? variableDefinitions? directives? selectionSet
    | selectionSet
    ;

operationType
    : QUERY_
    | MUTATION_
    | SUBSCRIPTION_
    ;

// https://spec.graphql.org/June2018/#sec-Selection-Sets
selectionSet
    : '{' selection+ '}'
    ;

selection
    : field
    | fragmentSpread
    | inlineFragment
    ;

// https://spec.graphql.org/June2018/#sec-Language.Fields
field
    : alias? name arguments? directives? selectionSet?
    ;

// https://spec.graphql.org/June2018/#sec-Language.Arguments
arguments
    : '(' argument+ ')'
    ;

argument
    : name ':' value
    ;

// https://spec.graphql.org/June2018/#sec-Field-Alias
alias
    : name ':'
    ;

// https://spec.graphql.org/June2018/#sec-Language.Fragments
fragmentSpread
    : '...' fragmentName directives?
    ;

fragmentDefinition
    : FRAGMENT_ fragmentName typeCondition directives? selectionSet
    ;

fragmentName
    : name
    ; // except on

// https://spec.graphql.org/June2018/#sec-Type-Conditions
typeCondition
    : ON_ namedType
    ;

// https://spec.graphql.org/June2018/#sec-Inline-Fragments
inlineFragment
    : '...' typeCondition? directives? selectionSet
    ;

// https://spec.graphql.org/June2018/#sec-Input-Values
value
    : variable
    | intValue
    | floatValue
    | stringValue
    | booleanValue
    | nullValue
    | enumValue
    | listValue
    | objectValue
    ;

// https://spec.graphql.org/June2018/#sec-Int-Value
intValue
    : INT
    ;

// https://spec.graphql.org/June2018/#sec-Float-Value
floatValue
    : FLOAT
    ;

// https://spec.graphql.org/June2018/#sec-Boolean-Value
booleanValue
    : TRUE_
    | FALSE_
    ;

// https://spec.graphql.org/June2018/#sec-String-Value
stringValue
    : STRING
    | BLOCK_STRING
    ;

// https://spec.graphql.org/June2018/#sec-Null-Value
nullValue
    : NULL_
    ;

// https://spec.graphql.org/June2018/#sec-Enum-Value
enumValue
    : name
    ; //{ not (nullValue | booleanValue) };

// https://spec.graphql.org/June2018/#sec-List-Value
listValue
    : '[' ']'
    | '[' value+ ']'
    ;

// https://spec.graphql.org/June2018/#sec-Input-Object-Values
objectValue
    : '{' '}'
    | '{' objectField* '}'
    ;

objectField
    : name ':' value
    ;

// https://spec.graphql.org/June2018/#sec-Language.Variables
variable
    : '$' name
    ;

variableDefinitions
    : '(' variableDefinition+ ')'
    ;

variableDefinition
    : variable ':' type_ defaultValue?
    ;

defaultValue
    : '=' value
    ;

// https://spec.graphql.org/June2018/#sec-Type-References
type_
    : namedType '!'?
    | listType '!'?
    ;

namedType
    : name
    ;

listType
    : '[' type_ ']'
    ;

// https://spec.graphql.org/June2018/#sec-Language.Directives
directives
    : directive+
    ;

directive
    : '@' name arguments?
    ;

// https://graphql.github.io/graphql-spec/June2018/#TypeSystemDefinition
typeSystemDefinition
    : schemaDefinition
    | typeDefinition
    | directiveDefinition
    ;

// https://spec.graphql.org/June2018/#TypeSystemExtension
typeSystemExtension
    : schemaExtension
    | typeExtension
    ;

// https://graphql.github.io/graphql-spec/June2018/#sec-Schema
schemaDefinition
    : SCHEMA_ directives? '{' rootOperationTypeDefinition+ '}'
    ;

rootOperationTypeDefinition
    : operationType ':' namedType
    ;

// https://spec.graphql.org/June2018/#sec-Schema-Extension
schemaExtension
    : EXTEND_ SCHEMA_ directives? '{' operationTypeDefinition+ '}'
    | EXTEND_ SCHEMA_ directives
    ;

// https://spec.graphql.org/June2018/#OperationTypeDefinition
operationTypeDefinition
    : operationType ':' namedType
    ;

// https://spec.graphql.org/June2018/#sec-Descriptions
description
    : stringValue
    ;

// https://spec.graphql.org/June2018/#sec-Types
typeDefinition
    : scalarTypeDefinition
    | objectTypeDefinition
    | interfaceTypeDefinition
    | unionTypeDefinition
    | enumTypeDefinition
    | inputObjectTypeDefinition
    ;

// https://spec.graphql.org/June2018/#sec-Type-Extensions
typeExtension
    : scalarTypeExtension
    | objectTypeExtension
    | interfaceTypeExtension
    | unionTypeExtension
    | enumTypeExtension
    | inputObjectTypeExtension
    ;

// https://spec.graphql.org/June2018/#sec-Scalars
scalarTypeDefinition
    : description? SCALAR_ name directives?
    ;

// https://spec.graphql.org/June2018/#sec-Scalar-Extensions
scalarTypeExtension
    : EXTENDS_ SCALAR_ name directives
    ;

// https://graphql.github.io/graphql-spec/June2018/#sec-Objects
objectTypeDefinition
    : description? TYPE_ name implementsInterfaces? directives? fieldsDefinition?
    ;

implementsInterfaces
    : IMPLEMENTS_ '&'? namedType
    | implementsInterfaces '&' namedType
    ;

fieldsDefinition
    : '{'  fieldDefinition+ '}'
    ;

fieldDefinition
    : description? name argumentsDefinition? ':' type_ directives?
    ;

// https://spec.graphql.org/June2018/#sec-Field-Arguments
argumentsDefinition
    : '(' inputValueDefinition+ ')'
    ;

inputValueDefinition
    : description? name ':' type_ defaultValue? directives?
    ;

// https://spec.graphql.org/June2018/#sec-Object-Extensions
objectTypeExtension
    : EXTEND_ TYPE_ name implementsInterfaces? directives? fieldsDefinition
    | EXTEND_ TYPE_ name implementsInterfaces? directives
    | EXTEND_ TYPE_ name implementsInterfaces
    ;

// https://spec.graphql.org/June2018/#sec-Interfaces
interfaceTypeDefinition
    : description? INTERFACE_ name directives? fieldsDefinition?
    ;

// https://spec.graphql.org/June2018/#sec-Interface-Extensions
interfaceTypeExtension
    : EXTEND_ INTERFACE_ name directives? fieldsDefinition
    | EXTEND_ INTERFACE_ name directives
    ;

// https://graphql.github.io/graphql-spec/June2018/#sec-Unions
unionTypeDefinition
    : description? UNION_ name directives? unionMemberTypes?
    ;

unionMemberTypes
    : '=' '|'?  namedType ('|'namedType)*
    ;

// https://spec.graphql.org/June2018/#sec-Union-Extensions
unionTypeExtension
    : EXTEND_ UNION_ name directives? unionMemberTypes
    | EXTEND_ UNION_ name directives
    ;

// https://spec.graphql.org/June2018/#sec-Enums
enumTypeDefinition
    : description? ENUM_ name directives? enumValuesDefinition?
    ;

enumValuesDefinition
    : '{' enumValueDefinition+  '}'
    ;

enumValueDefinition
    : description? enumValue directives?
    ;

// https://spec.graphql.org/June2018/#sec-Enum-Extensions
enumTypeExtension
    : EXTEND_ ENUM_ name directives? enumValuesDefinition
    | EXTEND_ ENUM_ name directives
    ;

// https://spec.graphql.org/June2018/#sec-Input-Objects
inputObjectTypeDefinition
    : description? INPUT_ name directives? inputFieldsDefinition?
    ;

inputFieldsDefinition
    : '{' inputValueDefinition+ '}'
    ;

// https://spec.graphql.org/June2018/#sec-Input-Object-Extensions
inputObjectTypeExtension
    : EXTEND_ INPUT_ name directives? inputFieldsDefinition
    | EXTEND_ INPUT_ name directives
    ;

// https://spec.graphql.org/June2018/#sec-Type-System.Directives
directiveDefinition
    : description? DIRECTIVE_ '@' name argumentsDefinition? ON_ directiveLocations
    ;

directiveLocations
    : directiveLocation ('|' directiveLocation)*
    ;

directiveLocation
    : executableDirectiveLocation
    | typeSystemDirectiveLocation
    ;

executableDirectiveLocation
    : QUERY
    | MUTATION
    | SUBSCRIPTION
    | FIELD
    | FRAGMENT_DEFINITION
    | FRAGMENT_SPREAD
    | INLINE_FRAGMENT
    ;

typeSystemDirectiveLocation
    : SCHEMA
    | SCALAR
    | OBJECT
    | FIELD_DEFINITION
    | ARGUMENT_DEFINITION
    | INTERFACE
    | UNION
    | ENUM
    | ENUM_VALUE
    | INPUT_OBJECT
    | INPUT_FIELD_DEFINITION
    ;

name
    : NAME
    | ARGUMENT_DEFINITION
    | DIRECTIVE_
    | ENUM
    | ENUM_
    | ENUM_VALUE
    | EXTEND_
    | EXTENDS_
    | FALSE_
    | FIELD
    | FIELD_DEFINITION
    | FRAGMENT_
    | FRAGMENT_DEFINITION
    | FRAGMENT_SPREAD
    | IMPLEMENTS_
    | INLINE_FRAGMENT
    | INPUT_
    | INPUT_FIELD_DEFINITION
    | INPUT_OBJECT
    | INTERFACE
    | INTERFACE_
    | MUTATION
    | MUTATION_
    | NULL_
    | OBJECT
    | ON_
    | QUERY
    | QUERY_
    | SCALAR
    | SCALAR_
    | SCHEMA
    | SCHEMA_
    | SUBSCRIPTION
    | SUBSCRIPTION_
    | TRUE_
    | TYPE_
    | UNION
    | UNION_
    ;

ARGUMENT_DEFINITION: 'ARGUMENT_DEFINITION';
DIRECTIVE_: 'directive';
ENUM: 'ENUM';
ENUM_: 'enum';
ENUM_VALUE: 'ENUM_VALUE';
EXTEND_: 'extend';
EXTENDS_: 'extends';
FALSE_: 'false';
FIELD: 'FIELD';
FIELD_DEFINITION: 'FIELD_DEFINITION';
FRAGMENT_: 'fragment';
FRAGMENT_DEFINITION: 'FRAGMENT_DEFINITION';
FRAGMENT_SPREAD: 'FRAGMENT_SPREAD';
IMPLEMENTS_: 'implements';
INLINE_FRAGMENT: 'INLINE_FRAGMENT';
INPUT_: 'input';
INPUT_FIELD_DEFINITION: 'INPUT_FIELD_DEFINITION';
INPUT_OBJECT: 'INPUT_OBJECT';
INTERFACE: 'INTERFACE';
INTERFACE_: 'interface';
MUTATION: 'MUTATION';
MUTATION_: 'mutation';
NULL_: 'null';
OBJECT: 'OBJECT';
ON_: 'on';
QUERY: 'QUERY';
QUERY_: 'query';
SCALAR: 'SCALAR';
SCALAR_: 'scalar';
SCHEMA: 'SCHEMA';
SCHEMA_: 'schema';
SUBSCRIPTION: 'SUBSCRIPTION';
SUBSCRIPTION_: 'subscription';
TRUE_: 'true';
TYPE_: 'type';
UNION: 'UNION';
UNION_: 'union';

NAME: [_A-Za-z] [_0-9A-Za-z]*;

fragment CHARACTER
    : (ESC | ~ ["\\])
    ;

STRING: '"' CHARACTER* '"';

BLOCK_STRING: '"""' .*? '"""';

ID: STRING;

fragment ESC
    : '\\' (["\\/bfnrt] | UNICODE)
    ;

fragment UNICODE
    : 'u' HEX HEX HEX HEX
    ;

fragment HEX
    : [0-9a-fA-F]
    ;

fragment NONZERO_DIGIT
    : [1-9]
    ;

fragment DIGIT
    : [0-9]
    ;

fragment FRACTIONAL_PART
    : '.' DIGIT+
    ;

fragment EXPONENTIAL_PART
    : EXPONENT_INDICATOR SIGN? DIGIT+
    ;

fragment EXPONENT_INDICATOR
    : [eE]
    ;

fragment SIGN
    : [+-]
    ;

fragment NEGATIVE_SIGN
    : '-'
    ;

FLOAT
    : INT FRACTIONAL_PART
    | INT EXPONENTIAL_PART
    | INT FRACTIONAL_PART EXPONENTIAL_PART
    ;

INT
    : NEGATIVE_SIGN? '0'
    | NEGATIVE_SIGN? NONZERO_DIGIT DIGIT*
    ;

PUNCTUATOR
    : '!'
    | '$'
    | '('
    | ')'
    | '...'
    | ':'
    | '='
    | '@'
    | '['
    | ']'
    | '{'
    | '}'
    | '|'
    ;

fragment EXP
    : [Ee] [+\-]? INT
    ;

WS: [ \t\n\r]+ -> skip;

COMMA: ',' -> skip;

LineComment: '#' ~[\r\n]* -> skip;

UNICODE_BOM: (UTF8_BOM | UTF16_BOM | UTF32_BOM) -> skip;

UTF8_BOM: '\uEFBBBF';
UTF16_BOM: '\uFEFF';
UTF32_BOM: '\u0000FEFF';

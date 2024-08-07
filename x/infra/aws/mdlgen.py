from omlish import lang

from botocore import model as bcm
import botocore.session


def _main():
    session = botocore.session.get_session()
    loader = session.get_component('data_loader')

    service_name = 'ec2'

    json_model = loader.load_service_model(service_name, 'service-2')
    service_model = bcm.ServiceModel(json_model, service_name=service_name)

    shape = service_model.shape_for(
        # 'Instance',
        'VCpuInfo',
        # 'CoreCount',
        # 'CoreCountList',
    )

    print(f'class {shape.name}(_base.Model):')

    # type_name: integer, list
    # bcm.ListShape, bcm.StructureShape

    for mn, ms in shape.members.items():
        fn = lang.snake_case(mn)
        fd = f'_dc.field({{_base.MEMBER_NAME: {mn!r}, _base.SHAPE_NAME: {ms.name!r}}})'
        dct = {
            'Integer': 'int',
            'String': 'str',
            'TagList': '_base.Tags',
        }
        try:
            mt = dct[ms.name]
        except KeyError:
            print(f'    # {fn}: {ms.name} = {fd}')
        else:
            print(f'    {fn}: {mt} = {fd}')

    # for shape_name in service_model.shape_names:
    #     shape = service_model.shape_for(shape_name)
    #     print((shape_name, shape))

    # for operation_name in service_model.operation_names:
    #     operation_model = service_model.operation_model(operation_name)
    #     print((operation_name, operation_model))


if __name__ == '__main__':
    _main()

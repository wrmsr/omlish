from collections import OrderedDict

from .. import newable
from .. import record


def test_all():
    @record.record()
    class Point:
        x = record.record.field(int, coerce_=int)
        y = record.record.field(int)

    @newable.newable()
    class Thing:
        point = newable.newable.arg(Point)

    @newable.newable()
    class OtherThing:
        thing = newable.newable.arg((Thing, None), default=None)

    newable.new(Thing, {'point': {'x': 1, 'y': 2}})
    newable.new(OtherThing, {'thing': {'point': {'x': 1, 'y': 2}}})
    newable.new(OtherThing, {'thing': None})
    newable.new(OtherThing, {})

    class SomeService:
        pass

    @newable.newable()
    class SomeServiceImpl(SomeService):
        name = newable.newable.arg(str)

    @newable.newable()
    class SomeDefaultingServiceImpl(SomeService):
        name = newable.newable.arg(str, default='the default')

    @newable.newable()
    class SomeOtherServiceImpl(SomeService):
        number = newable.newable.arg(int)

    @newable.newable()
    class SomeDependent:
        some_service = newable.newable.arg(newable.newable.ref(SomeService))
        some_nullable_service = newable.newable.arg((newable.newable.ref(SomeService), None), default=None)

    @newable.newable()
    class SomeSubDependent(SomeDependent):
        some_additional_service = newable.newable.arg((newable.newable.ref(SomeService), None), default=None)

    SomeDependent(SomeServiceImpl('hi'))

    namespace = {
        'some_service_impl': SomeServiceImpl,
        'some_defaulting_service_impl': SomeDefaultingServiceImpl,
        'some_other_service_impl': SomeOtherServiceImpl,
    }

    args = {
        'some_service': {
            'some_service_impl': {
                'name': 'hi',
            }
        }
    }
    newable.new(SomeDependent, args, namespace)

    args = {
        'some_service': {
            'some_other_service_impl': {
                'number': 1,
            }
        }
    }
    newable.new(SomeDependent, args, namespace)

    args = {
        'some_service': {
            'some_other_service_impl': {
                'number': 1,
            }
        },
        'some_nullable_service': {
            'some_service_impl': {
                'name': 'wow',
            }
        }
    }
    newable.new(SomeDependent, args, namespace)

    args = {
        'some_service': {
            'some_other_service_impl': {
                'number': 1,
            }
        },
        'some_additional_service': {
            'some_service_impl': {
                'name': 'wow',
            }
        }
    }
    newable.new(SomeSubDependent, args, namespace)

    newable.new(SomeDependent, {'some_service': 'some_defaulting_service_impl'}, namespace)

    args = OrderedDict([
        ('some_service', OrderedDict([
            ('some_other_service_impl$my_service', {'number': 1})])),
        ('some_additional_service', {'$': 'my_service'})])
    newable.new(SomeSubDependent, args, namespace)

    # need oyaml

    #     import yaml
    #     args = yaml.load("""
    # some_service:
    #   some_other_service_impl$my_service:
    #     number: 1
    # some_additional_service:
    #   $: my_service
    # """)
    #     print(new(SomeSubDependent, args, namespace))

    #     args = yaml.load("""
    # some_service:
    #   some_other_service_impl$my_service:
    #     number: 1
    # some_additional_service: $my_service
    # """)
    #     print(new(SomeSubDependent, args, namespace))

    @newable.newable()
    class SomeListDependent:
        services = newable.newable.arg([newable.newable.ref(SomeService)])

    args = {
        'services': [
            {'some_other_service_impl$f': {'number': 1}},
            {'some_other_service_impl': {'number': 2}},
            {'$': 'f'},
        ],
    }
    newable.new(SomeListDependent, args, namespace)

    @newable.newable()
    class A:
        pass

    @newable.newable()
    class B:
        a = newable.newable.arg(newable.newable.ref(A), new=lambda: newable.new(A))

    newable.new(B)

    @newable.newable()
    class C:
        bs = newable.newable.arg([newable.newable.ref(B)])

    args = OrderedDict([
        ('bs', [
            {'b$the_b': {}},
            {'b': {'a': '$the_b.a'}}])])
    ns = {'a': A, 'b': B, 'c': C}
    newable.new('c', args, ns)

    args = OrderedDict([
        ('bs', [
            {'b$the_b': {}},
            {'b': {'a': {'$': 'the_b.a'}}}])])
    ns = {'a': A, 'b': B, 'c': C}
    newable.new('c', args, ns)

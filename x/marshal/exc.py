from .specs import Spec


class UnhandledSpecException(Exception):
    spec: Spec

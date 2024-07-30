from ..sessions import SessionMarshal
from ..sessions import Signer


def test_sessions():
    session_marshal = SessionMarshal(
        signer=Signer(Signer.Config(
            secret_key='secret-key-goes-here',  # noqa
        )),
    )

    obj = {'_fresh': False}

    print(obj)
    for _ in range(3):
        sv = session_marshal.dump(obj)
        print(sv)
        obj = session_marshal.load(sv)
        print(obj)

from . import runhack as rh


DEBUGGER_PARAMS = rh.ParamDefs([
    rh.StrParamDef('port'),
    rh.StrParamDef('vm_type'),
    rh.StrParamDef('client'),

    rh.StrParamDef('qt-support'),

    rh.FinalParamDef('file'),

    rh.BoolParamDef('server'),
    rh.BoolParamDef('DEBUG_RECORD_SOCKET_READS'),
    rh.BoolParamDef('multiproc'),
    rh.BoolParamDef('multiprocess'),
    rh.BoolParamDef('save-signatures'),
    rh.BoolParamDef('save-threading'),
    rh.BoolParamDef('save-asyncio'),
    rh.BoolParamDef('print-in-debugger-startup'),
    rh.BoolParamDef('cmd-line'),
    rh.BoolParamDef('module'),
    rh.BoolParamDef('help'),
    rh.BoolParamDef('DEBUG'),
])


TEST_RUNNER_PARAMS = rh.ParamDefs([
    rh.StrParamDef('path'),
    rh.StrParamDef('offset'),
    rh.StrParamDef('target'),
])


def test_params():
    for argv in [
        [
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
            '--multiprocess',
            '--client',
            '127.0.0.1',
            '--port',
            '56431',
            '--file',
            '/Users/spinlock/src/wrmsr/omlish/x/llm/cli/main.py',
        ]
    ]:
        pa = rh.parse_args(DEBUGGER_PARAMS, argv)
        print(pa)

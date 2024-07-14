from .. import cron


def test_cron():
    for s in [
        '* 0 * * *',
    ]:
        print(cron.Spec.parse(s))

"""  # noqa
POSS:
 - common, typed node hierarchy?
  - general purpose, higher-level 'alias'? or pushed down into serde?
   - hocon has 'aliases', need to take it over? or push it down? interop/share?

TODO:
 - * dc's *:
  - frozen? updatable? dc.Enum compat? ??
 - *DECREE* NOW BUILT ON TOP OF / IN TERMS OF DATACLASSES.
  - DIFFS:
   - non-local, non-inherited, injected defaults: db.timeout = global.defualt
    - dep on global config? ... InitVar -> ValidationVar?
     - inject defaulters with initvars?
      - global_config: dc.InitVar[GlobalConfig] = None
      - dc.default('timeout', lambda global_config: global_config.timeout if global_config is not None else None)
       - https://www.python.org/dev/peps/pep-0505/ ugh
 - ** usable without but fully integrated with inj **
  - config.inject *not imported in init*
 - polled sources: file (+url, git), sql, redis
  - atomicity - class UsernameAndPassword etc
 - pushed sources: zk, etcd
  - omnibus 'coord' iface
 - callbacks only on 'winning' value change
 - dc stuff - validate, coerce, etc
 - config_cls->cls registry pattern?
 - flat: .ini
 - fat: xml
 - yaml forest
  - search_path (registry?), pkg:// prefix, origin tracking
  - yamls pointing at other yamls..
  - https://github.com/facebookresearch/hydra
 - pyo3 adapter (serde?)
 - newable-style object graphs, refs
 - cmdline overrides (+env-var? +dict?)
  - argparse ala record?
  - env extends dict w/ cfgable handling for 'empty means None' and shit, plus more str-coercion than dict
   - hm - csv serde handling escaping
    - just use builtin csv
    - is this 'stringly typed' shit more appropriate in serde - is it useful for csv?
 - * fqon (fully-qualified object name) resolver
  - train_fn.optimizer_cls = @tf.train.GradientDescentOptimizer
  - build_model.network_fn = @DNN()
  - newable style..
  - https://github.com/google/gin-config#4-configuring-the-same-function-in-different-ways-scopes
 - callbacks are dc-level - both field-lvl and inst-lvl
 - look at:
  - kubernetes
  - envoy https://www.envoyproxy.io/docs/envoy/latest/configuration/overview/examples
 - pluggable interpolation ala commons-cfg
  - dns lookup (polled/dynamic?)
  - JNDI equiv? (actor interop - Namespace abstr? jmx?)
  - env, intra-cfg (hocon)
  - exprs? safe_eval?
  - inline include and extract? jmespath lol. hit url?
 - LAZINESS.
 - 'mounting' sys-level shit (procfs)
 - datetime.timedelta vs foo_s, friendly (hocon?) parsing
 - *inherited defaults* - mysqldb.timeout inherits global.timeout
  - example isn't mysqldb inherits db cuz prob subclass
 - secrets: https://github.com/hashicorp/envconsul
 - docs: https://github.com/willkg/everett/blob/master/everett/sphinxext.py

https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/
https://blog.twitter.com/engineering/en_us/topics/infrastructure/2018/dynamic-configuration-at-twitter.html
https://news.ycombinator.com/item?id=22964910
https://github.com/alexandru/scala-best-practices/blob/master/sections/3-architecture.md#35-must-not-use-parameterless-configfactoryload-or-access-a-config-object-directly
https://github.com/google/gin-config - ghetto injection
https://github.com/spf13/viper - merging
 / https://gitlab.com/dashwav/gila
"""
from .. import dataclasses as dc


def _confer_confer(att, sub, sup, bases):
    return sub['confer'] if sub['confer'] is not dc.MISSING else sup['confer']


class Config(
    dc.Data,
    abstract=True,
    frozen=True,
    reorder=True,
    confer={
        'frozen': dc.SUPER,
        'reorder': dc.SUPER,
        'confer': dc.Conferrer(_confer_confer, weak=True),
    },
):
    pass

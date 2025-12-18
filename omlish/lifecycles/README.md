Lifecycle management, inspired by [governator](https://github.com/Netflix/governator/tree/master/governator-core/).

A central idea is to 'hide the guts' of a given class's lifecycle management from code interacting with it.

The main classes are as follows:

- Lifecycle / AsyncLifecycle - the code 'managed by' the rest of the lifecycle machinery. In general, user code will
  hide its implementations of these from the code that otherwise interacts with it. Being the lowest level / unit of
  management callbacks, it intentionally provides no additional machinery, existing solely as a skeleton of methods
  which will be called by lifecycle internals - this is to reduce friction with more functional / less OO code. However,
  it still chooses to be a class with multiple nullary methods, rather than a more functional-style single unary free
  function: the operations present in each method are generally intended to have no overlap in practice, and their
  explicit division is a conscious choice.

- LifecycleManaged / AsyncLifecycleManaged - a mixin which can be used to add lifecycle management behavior to a class.
  This removes the need for manual subclassing of Lifecycle / AsyncLifecycle, providing private '\_lifecycle_<state>'
  callback methods (with default no-op implementations) which subclasses may override.

- LifecycleListener / AsyncLifecycleListener - callback interfaces whose methods will be called when a lifecycle object
  goes through a lifecycle state transition.

- LifecycleController / AsyncLifecycleController - these classes run the state machine for any single Lifecycle /
  AsyncLifecycle instance. They are also responsible for maintaining a registry of lifecycle listeners and calling their
  methods as necessary. Unlike user code, these classes are openly subclasses of Lifecycle / AsyncLifecycle, allowing
  them to be called as application state dictates - they will internally ensure correct state transitions.

- LifecycleManager / AsyncLifecycleManager - these classes are responsible for construction and operation of (acyclic)
  graphs of lifecycle objects. They will ensure that, as necessary according to registered dependencies, lifecycle
  objects are started in the correct order, and that they are stopped in the correct order. This class is itself a
  LifecycleManaged / AsyncLifecycleManaged. Notably, AsyncLifecycleManager can also manage sync Lifecycles.

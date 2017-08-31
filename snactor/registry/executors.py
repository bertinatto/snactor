def _get_executors(cls=None, executors=None):
    executors = executors if executors else {}

    if cls is None:
        from snactor.executors.default import Executor
        cls = Executor
        _register_executor(cls, executors)

    for sub_cls in cls.__subclasses__():
        _register_executor(sub_cls, executors)
        _get_executors(sub_cls, executors)

    return executors


def _register_executor(cls, executors):
    if cls.name in executors:
        raise LookupError("Executor '{}' has been already registered previously".format(cls.name))
    executors[cls.name] = cls


def get_executor(executor):
    return _REGISTERED_EXECUTORS.get(executor)


_REGISTERED_EXECUTORS = _get_executors()

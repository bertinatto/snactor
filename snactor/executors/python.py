from snactor.executors.payload import PayloadExecutor


class PythonExecutorDefinition(PayloadExecutor.Definition):
    def __init__(self, init):
        super(PythonExecutorDefinition, self).__init__(init)
        self.executable = "/usr/bin/python"


class PythonExecutor(PayloadExecutor):
    Definition = PythonExecutorDefinition
    name = 'python'

    def __init__(self, definition):
        super(PythonExecutor, self).__init__(definition)

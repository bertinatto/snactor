import snactor.output_processors  # noqa
from snactor.executors.payload import PayloadExecutor
from snactor.registry.output_processors import get_output_processor


class BashExecutorDefinition(PayloadExecutor.Definition):
    def __init__(self, init):
        super(BashExecutorDefinition, self).__init__(init)
        self.executable = "/bin/bash"
        self.output_processor = get_output_processor(init.get('output-processor', None))


class BashExecutor(PayloadExecutor):
    Definition = BashExecutorDefinition
    name = 'bash'

    def handle_stdout(self, stdout, data):
        self.log.debug("handle_stdout(%s)", stdout)
        if self.definition.executor.output_processor:
            self.definition.executor.output_processor.process(stdout, data)

    def __init__(self, definition):
        super(BashExecutor, self).__init__(definition)

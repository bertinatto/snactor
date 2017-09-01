from snactor.executors.default import Executor


class AnsibleModuleExecutorDefinition(Executor.Definition):
    def __init__(self, init):
        super(AnsibleModuleExecutorDefinition, self).__init__(init)
        self.module = init.get('module', {})
        self.host = init.get('host', None)
        self.user = init.get('user', 'root')
        self.target = init.get('output', '__drop')


class AnsibleModuleExecutor(Executor):
    Definition = AnsibleModuleExecutorDefinition
    name = 'ansible-module'

    def handle_stdout(self, stdout, data):
        print("STDOUT: ", stdout)
        if stdout.strip():
            _, stdout = stdout.split('|', 1)
            result, stdout = stdout.split('=>', 1)
            self.result = result.strip().upper() == 'SUCCESS'
            stdout = '{"%s": %s}' % (self.definition.executor.target, stdout)
        else:
            stdout = "{}"
        return super(AnsibleModuleExecutor, self).handle_stdout(stdout, data)

    def __init__(self, definition):
        super(AnsibleModuleExecutor, self).__init__(definition)
        self.result = False

    def execute(self, data):
        self.result = False
        self.definition.executor.executable = 'ansible'

        self.definition.executor.arguments = [
            '-C', '-cssh',
            '-m', self.definition.executor.module['name'] or 'setup',
            '-u', self.definition.executor.user]
        if self.definition.executor.host and self.definition.executor.host != 'localhost':
            self.definition.executor.arguments.extend([
                '-i', self.definition.executor.host + ',', 'all'
            ])
        else:
            self.definition.executor.arguments.append('localhost')

        if self.definition.executor.module.get('arguments'):
            self.definition.executor.arguments.append('--args')
            args = self.definition.executor.module.get('arguments', ())
            if not isinstance(args, (tuple, list)):
                args = (args,)
            self.definition.executor.arguments.extend(args)

        self.log.debug('Executing: %s %s',
                       self.definition.executor.executable,
                       ' '.join(self.definition.executor.arguments))
        super(AnsibleModuleExecutor, self).execute(data)
        return self.result

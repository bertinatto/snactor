from snactor.executors.default import Executor, filter_by_channel
from snactor.registry.actors import must_get_actor


class GroupExecutorDefinition(Executor.Definition):
    def __init__(self, init):
        super(GroupExecutorDefinition, self).__init__(init)
        self.actors = map(must_get_actor, init.get('actors', ()))


class GroupExecutor(Executor):
    Definition = GroupExecutorDefinition
    name = 'group'

    def __init__(self, definition):
        super(GroupExecutor, self).__init__(definition)

    def execute(self, data):
        restricted = filter_by_channel(self.definition.inputs, data)

        ret = True
        for actor in self.definition.executor.actors:
            ret = actor.execute(restricted)
            if not ret:
                break

        data.update(filter_by_channel(self.definition.outputs, restricted))

        return ret

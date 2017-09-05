import imp
import logging
import os
import sys

import jsl
import yaml

from snactor.definition import Definition
from snactor.loader.extends import ExtendsActor
from snactor.registry import register_actor, get_executor, get_actor, register_schema, get_registered_actors,\
    get_schema


def _load(actor_name, specs_file, tags, post_resolve):
    _log = logging.getLogger('snactor.loader')
    with open(specs_file) as f:
        _log.debug("Loading %s ...", specs_file)
        specs = yaml.load(f)

        if tags:
            actor_tags = set(specs.get('tags', ()))
            if not actor_tags or not actor_tags.intersection(tags):
                _log.debug("Skipping %s due to missing selected tags", specs_file)
                return

        if specs.get('extends') and specs.get('executor'):
            raise ValueError("Conflicting extends and executor specification found in {}".format(actor_name))

        if not specs.get('extends'):
            if not specs.get('executor'):
                raise ValueError("Missing executor specification in {}".format(actor_name))
            specs['executor']['$location'] = os.path.abspath(specs_file)

        if specs.get('extends') or not all(map(get_actor, specs.get('executor', {}).get('actors', ()))):
            specs['$location'] = os.path.abspath(specs_file)
            post_resolve[actor_name] = {'definition': specs, 'name': actor_name, 'resolved': False}
            return

        create_actor(actor_name, specs)


def create_actor(name, specs):
    executor_name = specs.get('executor', {}).get('type')
    executor = get_executor(executor_name)
    if not executor:
        raise LookupError("Unknown executor {}".format(executor_name))

    specs.update({
        'executor': executor.Definition(specs.get('executor'))})

    register_actor(name, Definition(name, specs), executor)


def _apply_extension_resolve(to_extent_actor, base_actor):
    specs = to_extent_actor['definition']
    specs['extended'] = base_actor.definition
    register_actor(to_extent_actor['name'], ExtendsActor.Definition(to_extent_actor['name'], specs), ExtendsActor)


def _try_resolve(current_actor, to_resolve_actor):
    if current_actor['resolved']:
        return

    specs = current_actor['definition']

    pending = specs.get('executor', {}).get('actors', ())
    if specs.get('extends'):
        pending = (specs['extends'].get('name'),)

    for name in pending:
        actor = get_actor(name)

        if not actor and name in to_resolve_actor:
            if not to_resolve_actor[name]['resolved']:
                _try_resolve(to_resolve_actor[name], to_resolve_actor)
            actor = get_actor(name)

        if not actor:
            raise LookupError("Failed to resolve dependency '{}' for {}".format(name, current_actor['name']))

    if specs.get('extends'):
        _apply_extension_resolve(current_actor, get_actor(specs['extends'].get('name')))
    else:
        create_actor(current_actor['name'], specs)

    current_actor['resolved'] = True


def load(location, tags=()):
    post_resolve = {}
    tags = set(tags)
    for root, dirs, files in os.walk(location):
        if '_actor.yaml' in files:
            if "schema" in dirs:
                load_schemas(os.path.join(root, "schema"))

            _load(os.path.basename(root), os.path.join(root, '_actor.yaml'), tags, post_resolve)
        else:
            for f in files:
                filename, ext = os.path.splitext(f)
                if not filename.startswith('.') and ext.lower() == '.yaml':
                    _load(filename, os.path.join(root, f), tags, post_resolve)

    for item in post_resolve.values():
        _try_resolve(item, post_resolve)


def _validate_type(actor_name, direction, typename):
    _log = logging.getLogger('snactor.loader')
    if not get_schema(typename):
        _log.warning("Could not resolve schema for type %s on %s in actor %s", typename, direction, actor_name)
        return False, (typename, direction, actor_name)
    return True, None


class ActorTypeValidationError(LookupError):
    def __init__(self, message, data):
        super(ActorTypeValidationError, self).__init__(message)
        self.data = data


def validate_actor_types():
    result = []
    for name, (definition, _) in get_registered_actors().items():
        result.extend((_validate_type(name, 'inputs', current['type']) for current in definition.inputs))
        result.extend((_validate_type(name, 'outputs', current['type']) for current in definition.outputs))
    if not all((item[0] for item in result)):
        raise ActorTypeValidationError("Failed to lookup schema definitions", (x[1] for x in result if not x[0]))


def load_schemas(location):
    _log = logging.getLogger('snactor.loader')
    sys.path.append(location)

    for root, dirs, files in os.walk(location):
        for schema_file in files:
            module_name, ext = os.path.splitext(schema_file)
            if not module_name.startswith('.') and ext.lower() == '.py':
                f, path, description = imp.find_module(module_name, [root])

                mod = imp.load_module(module_name, f, path, description)
                for symbol in dir(mod):
                    item = getattr(mod, symbol)
                    if isinstance(item, type) and issubclass(item, jsl.Document) and item is not jsl.Document:
                        _log.debug("Loading schema %s from %s...", symbol, os.path.join(root, schema_file))
                        register_schema(symbol, item.get_schema())
    sys.path.pop()

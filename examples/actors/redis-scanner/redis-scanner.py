import os
import re
import json
import shlex
from subprocess import Popen, PIPE


def _execute(cmd):
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    out, _ = proc.communicate()
    return out


def get_version():
    out = _execute('redis-server --version')
    m = re.match(r'Redis server v=(.+?) +', out)
    return m.group(1) if m else None


def get_db_path():
    out_dir = _execute('redis-cli -h localhost config get dir')
    out_file = _execute('redis-cli -h localhost config get dbfilename')

    try:
        parsed_dir = out_dir.split()[1]
        parsed_file = out_file.split()[1]
    except (TypeError, IndexError):
        return None

    return os.path.join(parsed_dir, parsed_file)


def get_config_file():
    out = _execute('redis-cli -h localhost info')
    m = re.search(r'config_file:(.+?)\r', out)
    return m.group(1) if m else None


if __name__ == "__main__":
    raw = {
        'version': get_version(),
        'config_file': get_config_file(),
        'db_file_path': get_db_path(),
    }
    outputs = {k: [{'value': v}] for k, v in raw.items() if v is not None}
    print(json.dumps(outputs))

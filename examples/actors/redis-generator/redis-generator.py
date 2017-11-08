import os
import sys
import json
import shlex
import shutil
from subprocess import Popen, PIPE


def _execute(cmd):
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    sys.stderr.write(err)
    return out


if __name__ == "__main__":
    inputs = json.load(sys.stdin)

    version = inputs['version'][0]['value']
    config_file = inputs['config_file'][0]['value']
    db_file_path = inputs['db_file_path'][0]['value']

    # with tempfile.NamedTemporaryFile(delete=False) as fd:
    try:
        os.mkdir('container')
        os.mkdir('container/data')
    except OSError:
        pass

    # copy files
    shutil.copy(config_file, 'container/data/')
    shutil.copy(db_file_path, 'container/data/')

    # stop redis
    # _execute('systemctl stop redis')
    # sys.stderr.write('\n---> '+config_file+'\n')
    # sys.exit(1)

    with open('container/Dockerfile', 'w') as fd:
        fd.write('FROM redis:{0}-alpine\n'.format(version))
        fd.write('EXPOSE 6379\n')
        fd.write('COPY data/redis.conf /etc/redis.conf\n'.format(config_file))
        fd.write('COPY data/dump.rdb /data/dump.rdb\n'.format(db_file_path))

    # create container
    _execute('docker build container/ -t leapp/redis')

    # start container
    container_id = _execute('docker run -d -p 6380:6379 leapp/redis')

    # stop and delete
    # _execute('docker stop {}'.format(container_id))
    # _execute('docker rm {}'.format(container_id))

    # Start redis
    # _execute('systemctl start redis')

    # clean up
    try:
        os.unlink('container/Dockerfile')
        os.rmdir('container')
    except OSError:
        pass

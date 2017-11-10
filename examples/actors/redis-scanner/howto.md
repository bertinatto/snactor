# Information gathering

In order to migrate a running Redis installation we need to gather some important information first.

* Redis version; because we don't want to install an incompatible version;
* Redis configuration file; because we want to keep 
* RDB file; because we want to keep persistence

Fortunately, all this information can be easily gathered using standard tools that ship with the standard Redis setup.

## Redis Version

Finding out the Redis version is as difficult as running the command

`redis-server --version`.

## Redis configuration file

The configuration file can be discovered using the `INFO` command, available through `redis-cli`. The command

`redis-cli -h localhost info`

will print some information and statistics about the Redis server. Among thoese, it's possible to find a `config_file` options.

## Redis the database file

The database file, aka RDB file, can be found out in two steps. First, we can get the configuration directory with the command

`redis-cli -h localhost config get dir`

and then the database file name with the command

`redis-cli -h localhost config get dbfilename`.

If joined, the results of both commands will give the the path of the RDB file.

# Scanner actor

With this information in hand, it's relatively easy to create a scanning actor for Redis.

First of all, let's create a basic directory structure that will contain our actor.

`$ mkdir -p myactors/actors/redis myactors/schemas`

Now, let's create a schema that represents the data we are interested in:

```
cat > myactors/schemas/redis.py <<EOF

import jsl
from snactor.registry.schemas import registered_schema


@registered_schema('1.0')
class RedisInstallation(jsl.Document):
    version = jsl.StringField(required=True)
    config_file_path = jsl.StringField()
    db_file_path = jsl.StringField()

EOF
```

The next step is to create the definition for the scanner actor. This definition will use the schema we just created:

```
cat > myactors/actors/redis/_actor.yml <<EOF

---
outputs:
  - name: redis
    type:
      name: RedisInstallation

description: |
  Redis scanner actor.

  Outputs:
    redis             - Redis installation data

execute:
  script-file: redis-scanner.py
  executable: /usr/bin/python

EOF
```

As we can see, we delegated part of the actor's job to an external script. This script will print to the standard output the data according the out defined schema:

```
```

# Container-generator actor

Now tt's relatively easy to create another actor that will generate a container out of the information gathered by the scanner actor.

We will use **buildah** to create and push the image to an eexternal registry. We could easily use **docker** instead, however, that would require us to have an instance of **docker-daemon** running.

copy files to a directory
buildah from redis-alpine


from patchwork.transfers import rsync
from fabric import task

hosts = [
    'root@xx.xxx.xxx'  # paytaca-gifts server
]


@task(hosts=hosts)
def sync(c):
    c.config.run['replace_env'] = False
    rsync(
        c,
        '.',
        '/root/paytaca-gifts',
        exclude=[
            '.git',
            './static',
            '.DS_Store',
            '.env',
            '__pycache__'
        ]
    )


@task(hosts=hosts)
def build(c):
    with c.cd('/root/api'):
        c.run('docker-compose -p paytaca_gifts -f compose/prod.yml build')


@task(hosts=hosts)
def up(c):
    with c.cd('/root/api'):
        c.run('docker-compose -p paytaca_gifts -f compose/prod.yml up -d')


@task(hosts=hosts)
def down(c):
    with c.cd('/root/api'):
        c.run('docker-compose -p paytaca_gifts -f compose/prod.yml down')


@task(hosts=hosts)
def deploy(c):
    sync(c)
    build(c)
    down(c)
    up(c)


@task(hosts=hosts)
def logs(c):
    with c.cd('/root/api'):
        c.run('docker-compose -f compose/prod.yml logs api')
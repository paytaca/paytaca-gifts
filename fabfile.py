from patchwork.transfers import rsync
from fabric import task

hosts = [
    'root@65.108.219.175'  # paytaca-gifts server
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
            'static',
            '.DS_Store',
            '.env',
            '__pycache__',
            'postgres-data'
        ]
    )


@task(hosts=hosts)
def build(c):
    with c.cd('/root/paytaca-gifts/deployment'):
        c.run('docker-compose -p paytaca_gifts -f docker-compose_prod.yml build')


@task(hosts=hosts)
def up(c):
    with c.cd('/root/paytaca-gifts/deployment'):
        c.run('docker-compose -p paytaca_gifts -f docker-compose_prod.yml up -d')


@task(hosts=hosts)
def down(c):
    with c.cd('/root/paytaca-gifts/deployment'):
        c.run('docker-compose -p paytaca_gifts -f docker-compose_prod.yml down')


@task(hosts=hosts)
def deploy(c):
    sync(c)
    build(c)
    down(c)
    up(c)


@task(hosts=hosts)
def logs(c):
    with c.cd('/root/paytaca-gifts/deployment'):
        c.run('docker-compose -f deployment/docker-compose_prod.yml logs backend')

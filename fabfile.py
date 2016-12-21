from fabric.api import *
from fabric.contrib.files import *

ip = []

with open("hosts.txt") as file:
    host_lines = file.readlines()
for i in host_lines:
    ip.append(i.strip())

env.hosts = ip
env.user = 'root'
env.password = ''

env.roledefs = {
    'install': [''],
    'zk': ['']
}


@task()
def show():
    """
    显示主机列表
    :return:
    """
    print("available hosts are %s" % ip)


@task()
def adduser():
    """
    为所有主机添加analytics用户
    :return:
    """
    run('useradd analytics')

@task()
def initial():
    """
    环境初始化
    :return:
    """
    run('mkdir /nfs')
    adduser()
    run('chown -R analytics:analytics /nfs')
    run('yum install nfs-utils -y')
    def user_create():

        if exists("/home/analytics/.ssh/id_rsa.pub"):
            print("id_rsa.pub is existing pleas make sure to continue")
            is_ok = input("press Y to continue:")
            if is_ok == "Y" | is_ok == "y":
                sudo("ssh-keygen -t rsa -f /home/oracle/.ssh/id_rsa -q -P "" ", user='analytics')
            elif is_ok == "N" | is_ok == "n":
                pass
            else:
                return user_create()
    user_create()
    with open('localhosts.txt') as localhost:
        localhost = localhost.read()
    append('/etc/hosts',localhost)

@task()
@roles('install')
def master_init():
    """
    主控节点初始化
    :return:
    """
    run('yum install -y nfs-utils rpcbind')
    with open('exports') as exports:
        exports = exports.read()
    append('/etc/exports',exports)
    run('service rpcbind start')
    run('service nfs start')
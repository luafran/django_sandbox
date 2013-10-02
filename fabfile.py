import fabric.api
from collections import OrderedDict
from ConfigParser import SafeConfigParser
import time

from fabenvs import *

SITES_DIR = '/var/sites'
ROOT_DIR = os.path.dirname(__file__)
PACKAGES_ROOT_DIR = os.path.join(ROOT_DIR)
DEPLOY_DIR = os.path.join(ROOT_DIR, 'deploy')
ARTIFACTS_DIR = os.path.join(ROOT_DIR, 'artifacts')
ENABLE_UNITTEST = False
RESTART_SERVICES = True

###################
# Entry functions #
###################

def deploy():
    """
    Deploy site
    """

    print '*' * 70
    print 'DEPLOY'
    print 'Environment =', get_env_name()
    print '*' * 70

    fabric.api.local('mkdir -p ' + ARTIFACTS_DIR)

    packages = OrderedDict()
    packages.update( build_package('sandboxsite', ARTIFACTS_DIR) )

    target_roles = ['app_server']
    fabric.api.execute(upload_and_setup, packages, roles=target_roles)

def sync_db():
    """
    Synchronize DB
    """
    if fabric.api.env.use_bastion:
        fabric.api.execute(bastion_up)

    fabric.api.execute(synchronize_db, roles=['app_server'])

def synchronize_db():
    """
    Synchronize django db
    """

    if not fabric.api.env.host_string:
        return

    with fabric.api.cd(TARGET_DIR + PACKAGE_INFO["portal"]["dir"]):
        fabric.api.sudo("scripts/syncdb.sh")

@fabric.api.roles('bastion')
def bastion_up():

    if not fabric.api.env.host_string:
        return

    #Clean previous rules
    fabric.api.sudo('sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"')
    fabric.api.sudo("sudo iptables -t nat -F")
    fabric.api.sudo("sudo iptables -t raw -F")
    fabric.api.sudo("sudo iptables -t filter -F")

    #push iptables rules
    if not fabric.api.env.iptables_file:
        rules_file = 'bastion_'+get_env_name()+'.iptable'
    else:
        rules_file = fabric.api.env.iptables_file

    fabric.api.put(DEPLOY_DIR + "/" + rules_file, "/tmp/forward_table")

    #load the iptables rulez
    fabric.api.sudo("cat /tmp/forward_table")
    fabric.api.sudo("sudo iptables-restore /tmp/forward_table")

@fabric.api.roles('bastion')
def bastion_down():

    if not fabric.api.env.host_string:
        return

    #Clean previous rules
    fabric.api.sudo("sudo iptables -t nat -F")
    fabric.api.sudo("sudo iptables -t raw -F")
    fabric.api.sudo("sudo iptables -t filter -F")
    fabric.api.sudo('sudo sh -c "echo 0 > /proc/sys/net/ipv4/ip_forward"')


####################
# Helper functions #
####################

def build_package(package_name, dest_dir):
    # Precondition: dest_dir exists

    print "---> Preparing package",package_name

    package_src_dir = PACKAGES_ROOT_DIR + '/' + package_name
    config_file = package_src_dir + '/make_package.info'
    print 'config_file =', config_file

    parser = SafeConfigParser()
    parser.optionxform = str
    parser.read(config_file)
    config = dict()
    for name, value in parser.items('install'):
        print "Loading: ", config_file, name, value
        config[name] = eval(value)

    suffix = str(time.time()).split('.')[0]
    file_name = "{0}_{1}.tgz".format(package_name, suffix)

    with fabric.api.lcd(package_src_dir):
            res = fabric.api.local(ROOT_DIR + "/make_package.sh {0} {1}".format(file_name, dest_dir), capture=True)

    if res.failed:
        abort("Cannot make tarball")

    install = config['INSTALL']
    install_dir = "{0}/{1}".format(SITES_DIR, package_name)
    remove_install_dir = 'yes'

    return { package_name : { 'package_name': package_name,
                              'file_name': file_name,
                              'file_path': dest_dir+'/'+file_name,
                              'install': install,
                              'install_dir': install_dir,
                              'remove_install_dir': remove_install_dir
                            }
           }

def upload_and_setup(packages_info = {}):

    for (package_name,package_info) in packages_info.items():
        print "---> Processing package:", package_name
        print package_info

        file_name = package_info['file_name']
        file_path = package_info['file_path']
        install = package_info['install']
        if install == 'yes':
            install_dir = package_info['install_dir']
        else:
            install_dir = '/tmp/install_' + package_name
        remove_install_dir = package_info['remove_install_dir']

        remote_file_name = file_name + '_remote'
        fabric.api.put(file_path, '/tmp/' + remote_file_name)

        if remove_install_dir == 'yes':
            fabric.api.sudo("rm -rf {0}".format( install_dir ))
            fabric.api.sudo("mkdir -p {0}".format( install_dir ))

        fabric.api.sudo('tar xzpf /tmp/{0} -C {1}'.format(remote_file_name, install_dir))
        #fabric.api.sudo("chown www-data.www-data -R {0}".format(install_dir))

        with fabric.api.cd("{0}".format(install_dir)):
            fabric.api.sudo("./setup.sh")

def handle_services( services_list = [], action = "start"):
    if not RESTART_SERVICES:
        return
    """
    Remember to stop monit first is running
    """

    if not services_list:
        return

    print ("Going to do {0} on {1}".format(action, services_list ) )
    nservices = list(services_list)
    if action == "start" or action == "restart":
        nservices.reverse()
    for x in nservices:
        sudo("/etc/init.d/{0} {1}".format(x, action) )

def get_env_name():
    if fabric.api.env.get('env_name'):
        environment = fabric.api.env.env_name
    elif "environment" in os.environ:
        environment = os.environ["environment"]
    else:
        environment = None

    return environment

def _get_current_role():
    for role in env.roledefs.keys():
        if env.host_string in env.roledefs[role]:
            return role
    return None


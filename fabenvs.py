import fabric.api
import os

HOME = os.getenv('HOME')

def local_dev():
    fabric.api.env.env_name = 'local'
    fabric.api.env.roledefs = {
        'bastion': [],
        'app_server': ['127.0.0.1'],
        'application': ['127.0.0.1'],
        'db_mongo': ['127.0.0.1'],
    }

    fabric.api.env.user = "ubuntu"
    fabric.api.env.key_filename = ['%s/.ssh/localhost-key' % HOME, ]
    fabric.api.env.use_bastion = False
    fabric.api.env.iptables_file = None

def sandbox():
    fabric.api.env.env_name = 'sandbox'
    fabric.api.env.roledefs = {
        'bastion': [],
        'app_server': ['.compute-1.amazonaws.com'],
        'application': ['.compute-1.amazonaws.com'],
        'db_mongo': ['.compute-1.amazonaws.com'],
    }

    fabric.api.env.user = "ubuntu"
    fabric.api.env.key_filename = ['%s/.ssh/amazon.priv' % HOME, ]
    fabric.api.env.use_bastion = False
    fabric.api.env.iptables_file = None


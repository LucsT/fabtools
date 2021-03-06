"""
Fabric tools for managing OpenVZ containers

The remote host needs a patched kernel with OpenVZ support
"""
from __future__ import with_statement

from fabric.api import *


def create(ctid, ostemplate=None, config=None, private=None,
           root=None, ipadd=None, hostname=None, **kwargs):
    """
    Create OpenVZ container
    """
    return _vzctl('create', ctid, ostemplate=ostemplate, config=config,
        private=private, root=root, ipadd=ipadd, hostname=hostname, **kwargs)


def destroy(ctid_or_name):
    """
    Destroy OpenVZ container
    """
    return _vzctl('destroy', ctid_or_name)


def set(ctid_or_name, save=True, **kwargs):
    """
    Set OpenVZ container parameters
    """
    return _vzctl('set', ctid_or_name, save=save, **kwargs)


def start(ctid_or_name, wait=False, force=False, **kwargs):
    """
    Start OpenVZ container

    Warning: wait=True is broken with vzctl 3.0.24 on Debian 6.0 (squeeze)
    """
    return _vzctl('start', ctid_or_name, wait=wait, force=force, **kwargs)


def stop(ctid_or_name, fast=False, **kwargs):
    """
    Stop OpenVZ container
    """
    return _vzctl('stop', ctid_or_name, fast=fast, **kwargs)


def restart(ctid_or_name, wait=True, force=False, fast=False, **kwargs):
    """
    Restart OpenVZ container
    """
    return _vzctl('restart', ctid_or_name, wait=wait, force=force, fast=fast, **kwargs)


def status(ctid_or_name):
    """
    Show status of OpenVZ container
    """
    with settings(warn_only=True):
        return _vzctl('status', ctid_or_name)


def running(ctid_or_name):
    """
    Is the container running?
    """
    return status(ctid_or_name).split(' ')[4] == 'running'


def exists(ctid_or_name):
    """
    Does the container exist?
    """
    with settings(hide('running', 'stdout', 'warnings'), warn_only=True):
        return status(ctid_or_name).succeeded


def exec2(ctid_or_name, command):
    """
    Run command inside OpenVZ container
    """
    return sudo('vzctl exec2 %s %s' % (ctid_or_name, command))


def _vzctl(command, ctid_or_name, **kwargs):
    args = _expand_args(**kwargs)
    return sudo('vzctl %s %s %s' % (command, ctid_or_name, args))


def _expand_args(**kwargs):
    args = []
    for k, v in kwargs.items():
        if isinstance(v, bool):
            if v is True:
                args.append('--%s' % k)
        elif isinstance(v, (list, tuple)):
            for elem in v:
                args.append('--%s %s' % (k, elem))
        elif v is not None:
            args.append('--%s %s' % (k, v))
    return ' '.join(args)


def download_template(name=None, url=None):
    """
    Download an OpenVZ template
    """
    if url is None:
        url = 'http://download.openvz.org/template/precreated/%s.tar.gz' % name

    with cd('/var/lib/vz/template/cache'):
        sudo('wget --progress=dot "%s"' % url)


def list_ctids():
    """
    Get the list of currently used CTIDs
    """
    with settings(hide('running', 'stdout')):
        res = sudo('vzlist -a -1')
    return map(int, res.splitlines())


def get_available_ctid():
    """
    Get an available CTID
    """
    current_ctids = list_ctids()
    if current_ctids:
        return max(current_ctids) + 1
    else:
        return 1000

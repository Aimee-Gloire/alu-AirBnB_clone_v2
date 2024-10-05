#!/usr/bin/python3
"""
Fabric script based on the file 1-pack_web_static.py that distributes an
archive to the web servers
"""

from fabric.api import put, run, env, settings
from os.path import exists

env.hosts = ['54.162.155.7', '54.146.226.149']
env.user = 'ubuntu'
env.key_filename = 'path/to/your/private/key'

def do_deploy(archive_path):
    """Distributes an archive to the web servers."""
    if not exists(archive_path):
        print("Archive path does not exist: {}".format(archive_path))
        return False

    try:
        file_name = archive_path.split("/")[-1]
        base_name = file_name.split(".")[0]
        release_path = "/data/web_static/releases/{}/".format(base_name)
        tmp_path = "/tmp/{}".format(file_name)

        with settings(warn_only=True):
            # Upload the archive
            print("Uploading archive...")
            put(archive_path, tmp_path)

            # Create the target directory
            print("Creating target directory...")
            run('mkdir -p {}'.format(release_path))

            # Uncompress the archive
            print("Uncompressing archive...")
            run('tar -xzf {} -C {}'.format(tmp_path, release_path))

            # Remove the archive from the server
            print("Removing archive from server...")
            run('rm {}'.format(tmp_path))

            # Move contents out of the web_static folder
            print("Moving contents...")
            run('mv {}web_static/* {}'.format(release_path, release_path))

            # Remove the now-empty web_static directory
            print("Removing empty web_static directory...")
            run('rm -rf {}web_static'.format(release_path))

            # Delete the current symbolic link
            print("Deleting current symbolic link...")
            run('rm -rf /data/web_static/current')

            # Create a new symbolic link to the new version
            print("Creating new symbolic link...")
            run('ln -s {} /data/web_static/current'.format(release_path))

        print("New version deployed!")
        return True
    except Exception as e:
        print("Deployment failed:", e)
        return False

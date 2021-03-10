.. _rootless_docker:

Rootless docker
===============

If not done already install docker 20.10. If docker was already installed disable the docker daemon if needed::

    $ systemctl disable --now docker.service

First install uidmap::

    $ apt install uidmap

Set up the docker daemon::

    $ dockerd-rootless-setuptool.sh install

Enable the docker daemon::

    $ systemctl --user enable docker
    $ sudo loginctl enable-linger $(whoami)

Specify the socket path for docker::

    $ export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock

Test docker::

    $ docker images

This should return an empty list of images without an error message. If it did docker is ready to be used.
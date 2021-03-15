.. _rootless_docker:

Rootless docker
===============

If not done already install docker 20.10. If docker was already installed disable the docker daemon if needed::

    systemctl disable --now docker.service

First install uidmap::

    apt install uidmap

Set up the docker daemon::

    dockerd-rootless-setuptool.sh install

Enable the docker daemon on startup::

    systemctl --user enable docker
    sudo loginctl enable-linger $(whoami)

Specify the socket path for docker. Use the first command to enable docker in the current terminal.
You'll have to re-enter the command every time a new terminal is opened. Optionally enter the second command to
enter the line in to the *.bashrc*. Docker will then be enable anytime a new terminal is opened::

    export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock

    echo "export DOCKER_HOST=unix:///run/user/1000/docker.sock" >> .bashrc

Test docker::

    docker images

This should return an empty list of images without an error message. If it did docker is ready to be used.
#!/bin/sh
# Start the API as an unprivileged user that can still use the mounted Docker
# socket: give it the socket's group (which differs between hosts).
set -e
SOCK=/var/run/docker.sock
if [ "$(id -u)" = "0" ] && [ -S "$SOCK" ]; then
    exec setpriv --reuid=1000 --regid=1000 --groups="$(stat -c %g "$SOCK")" --inh-caps=-all "$@"
fi
exec "$@"

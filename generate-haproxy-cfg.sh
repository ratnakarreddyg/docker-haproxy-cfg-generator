#!/bin/bash

/usr/local/bin/docker_proxy.py > /tmp/haproxy.cfg-docker
diff /tmp/haproxy.cfg-docker /etc/haproxy/haproxy.cfg >& /dev/null

if [ $? -ne 0 ]
then
  cp -f /tmp/haproxy.cfg-docker /etc/haproxy/haproxy.cfg
  /sbin/service haproxy reload
  logger Generated new HAProxy config from Docker and reloaded HAProxy
fi


#!/usr/bin/env python

# Requires airspeed, docker-py

from docker import Client
from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader

# Path to HAProxy config template
haproxy_template_path = "/etc/haproxy/haproxy.cfg.template"

cli = Client(base_url='unix://var/run/docker.sock')

container_host_portmap = dict()

# Get all containers
containers = cli.containers()

# Get port mapping if available for each container
for container in containers:
  container_id = container['Id']
  inspect_output = cli.inspect_container( container_id )
  labels = inspect_output['Config']['Labels']

  proxy_container_port = labels.get("docker-proxy-container-port")
  proxy_external_port  = labels.get("docker-proxy-external-port")
  proxy_host_port      = None

  # If the container has the docker-proxy-* labels, then get the host port
  if proxy_container_port is not None and proxy_external_port is not None:
    port_key = "%s/tcp" % proxy_container_port
    host_ports = inspect_output['NetworkSettings']['Ports'][port_key]
    for host_port in host_ports:
      host_ip = host_port['HostIp']
      if host_ip == '0.0.0.0':
        proxy_host_port = host_port['HostPort']

  # If ports were found, add it to container_host_portmap
  if proxy_host_port is not None:
    port_list = container_host_portmap.get(proxy_external_port)
    if port_list is None:
      port_list = []
      container_host_portmap[proxy_external_port] = port_list
    container_name_hostport = dict()
    container_name_hostport['name']      = inspect_output['Name'].replace('/', '')
    container_name_hostport['host_port'] = proxy_host_port
    port_list.append(container_name_hostport)

#print container_host_portmap

j2_env = Environment(loader=FileSystemLoader('/'), trim_blocks=True)
template = j2_env.get_template(haproxy_template_path, None, None)
print template.render(map=container_host_portmap)
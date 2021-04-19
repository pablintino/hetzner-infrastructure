
output "server_ips" {
  value = {
    for server in hcloud_server.server :
    server.name => server.ipv4_address
  }
}

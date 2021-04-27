terraform {
  required_providers {
    hcloud = {
      source = "hetznercloud/hcloud"
      version = "1.26.0"
    }
  }
}

# Set the variable value in *.tfvars file
# or using the -var="hcloud_token=..." CLI option
variable "hcloud_token" {}

# Configure the Hetzner Cloud Provider
provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_ssh_key" "default" {
  name = var.ssh_public_key_name
  public_key = file(var.ssh_public_key)
}

resource "hcloud_network" "default" {
  name = var.private_network_name
  ip_range = var.private_ip_range
}

resource "hcloud_network_subnet" "default" {
  network_id = hcloud_network.default.id
  type = "server"
  network_zone = var.private_network_zone
  ip_range = var.private_ip_range
}

resource "hcloud_server" "server" {
  for_each = var.servers
  name = each.key
  server_type = each.value.server_type
  image = var.server_image
  location = var.hcloud_location
  ssh_keys = [
    var.ssh_public_key_name]
  labels = {
      for node_type in each.value.node_type :
      "k8sgen.rol.${node_type}" => true
    }

}

resource "hcloud_server_network" "server_network" {
  for_each = var.servers

  network_id = hcloud_network.default.id
  server_id = hcloud_server.server[each.key].id
}
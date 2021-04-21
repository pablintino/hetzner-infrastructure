variable "servers" {
  type = map(object({
    server_type = string
    location = string
    node_type = set(string)
  }))
}

variable "ssh_public_key" {
  default= "~/.ssh/id_rsa.pub"
}

variable "hcloud_location" {
  default = "nbg1"
}

variable "server_image"{
  default = "ubuntu-20.04"
}

variable "private_ip_range" {
  default = "10.0.0.0/16"
}

variable "ssh_public_key_name" {
  default = "default"
}

variable "private_network_name" {
  default = "default"
}

variable "private_network_zone" {
  default = "eu-central"
}


import hcl2
from configuration import config_parser
from generator.terraform.terraform_interface import Terraform

config = config_parser.parse_configuration('../config/k8s-config.json')

tf = Terraform()
tf.plan('../terraform/hetzner-k8s-cluster.tf')


with open('../terraform/config.tfvars', 'r') as file:
    dict = hcl2.load(file)
    print(dict)

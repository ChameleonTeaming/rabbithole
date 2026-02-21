# RabbitHole OCI Terraform Configuration
# This file automatically builds the Network, Firewall, and Server.

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 4.0.0"
    }
  }
}

# --- Variables (YOU MUST EDIT THESE) ---
variable "compartment_ocid" {
  description = "OCID of the Compartment where resources will be created"
  type        = string
  default     = "ocid1.compartment.oc1..aaaaaaaaxxxxx..." # REPLACE THIS
}

variable "region" {
  description = "OCI Region (e.g., us-ashburn-1)"
  type        = string
  default     = "us-ashburn-1" # REPLACE THIS
}

variable "ssh_public_key" {
  description = "Public SSH Key for accessing the VM"
  type        = string
  default     = "ssh-rsa AAAAB3Nza..." # REPLACE THIS with your actual public key content
}

variable "instance_shape" {
  description = "Instance Shape (VM.Standard.A1.Flex is Free Tier eligible)"
  default     = "VM.Standard.A1.Flex"
}

# --- Networking ---

resource "oci_core_vcn" "rabbithole_vcn" {
  cidr_block     = "10.0.0.0/16"
  compartment_id = var.compartment_ocid
  display_name   = "rabbithole-vcn"
  dns_label      = "rabbithole"
}

resource "oci_core_internet_gateway" "rabbithole_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.rabbithole_vcn.id
  display_name   = "rabbithole-igw"
  enabled        = true
}

resource "oci_core_route_table" "rabbithole_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.rabbithole_vcn.id
  display_name   = "rabbithole-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.rabbithole_igw.id
  }
}

resource "oci_core_security_list" "rabbithole_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.rabbithole_vcn.id
  display_name   = "rabbithole-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  # SSH (Admin)
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # Honeypot FTP
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 2121
      max = 2121
    }
  }

  # Honeypot SSH
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 2222
      max = 2222
    }
  }

  # Honeypot HTTP
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 8080
      max = 8080
    }
  }
  
  # Metrics
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 8000
      max = 8000
    }
  }
}

resource "oci_core_subnet" "rabbithole_subnet" {
  cidr_block        = "10.0.0.0/24"
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.rabbithole_vcn.id
  display_name      = "rabbithole-public-subnet"
  route_table_id    = oci_core_route_table.rabbithole_rt.id
  security_list_ids = [oci_core_security_list.rabbithole_sl.id]
}

# --- Compute ---

# Get the latest Ubuntu 22.04 Image
data "oci_core_images" "ubuntu" {
  compartment_id   = var.compartment_ocid
  operating_system = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape            = var.instance_shape
  sort_by          = "TIMECREATED"
  sort_order       = "DESC"
}

resource "oci_core_instance" "rabbithole_server" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  display_name        = "RabbitHole-Honeypot"
  shape               = var.instance_shape

  shape_config {
    memory_in_gbs = 12
    ocpus         = 2
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.rabbithole_subnet.id
    assign_public_ip = true
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu.images[0].id
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/user_data.sh"))
  }
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

output "server_public_ip" {
  value = oci_core_instance.rabbithole_server.public_ip
}

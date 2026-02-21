# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Use a stable Ubuntu 22.04 LTS box
  config.vm.box = "bento/ubuntu-22.04"

  # VirtualBox specific configuration
  config.vm.provider "virtualbox" do |vb|
    vb.name = "RabbitHole-Honeypot"
    vb.memory = "4096" # 4GB RAM recommended for AI/Docker operations
    vb.cpus = 2
    # Enable nested virtualization if available (useful for Docker inside VM)
    vb.customize ["modifyvm", :id, "--nested-hw-virt", "on"]
  end

  # Forward ports used by RabbitHole
  # Host Port -> Guest Port
  config.vm.network "forwarded_port", guest: 2121, host: 2121, auto_correct: true # FTP
  config.vm.network "forwarded_port", guest: 2222, host: 2222, auto_correct: true # SSH
  config.vm.network "forwarded_port", guest: 8000, host: 8000, auto_correct: true # Prometheus Metrics
  config.vm.network "forwarded_port", guest: 8080, host: 8080, auto_correct: true # Web Dashboard

  # Sync the current project directory to /app in the VM
  config.vm.synced_folder ".", "/app"

  # Provisioning script to set up the environment
  config.vm.provision "shell", inline: <<-SHELL
    # Disable interactive prompts during installation
    export DEBIAN_FRONTEND=noninteractive

    echo "Updating system packages..."
    apt-get update
    
    echo "Installing system dependencies..."
    apt-get install -y \
      python3-pip \
      python3-venv \
      docker.io \
      docker-compose \
      libssl-dev \
      libffi-dev \
      python3-dev \
      build-essential

    echo "Configuring Docker..."
    # Enable Docker service
    systemctl enable docker
    systemctl start docker
    # Allow 'vagrant' user to run Docker commands without sudo
    usermod -aG docker vagrant

    echo "Setting up Python environment..."
    # Create a virtual environment to avoid PEP 668 conflicts
    python3 -m venv /home/vagrant/rabbithole_env
    chown -R vagrant:vagrant /home/vagrant/rabbithole_env

    # Install Python requirements inside the virtual environment
    # We run this as the vagrant user to ensure permissions are correct
    sudo -u vagrant /home/vagrant/rabbithole_env/bin/pip install --upgrade pip
    sudo -u vagrant /home/vagrant/rabbithole_env/bin/pip install -r /app/requirements.txt

    echo "Pre-pulling Docker images for the Simulacrum..."
    docker pull alpine:latest

    echo "========================================================"
    echo "RabbitHole VirtualBox setup complete!"
    echo "To start the honeypot:"
    echo "  1. vagrant ssh"
    echo "  2. cd /app"
    echo "  3. /home/vagrant/rabbithole_env/bin/python rabbithole.py"
    echo "========================================================"
  SHELL
end

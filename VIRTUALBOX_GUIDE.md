# Running RabbitHole in VirtualBox

This guide explains how to safely deploy the RabbitHole AI Honeypot inside a VirtualBox environment using Vagrant. This isolates the honeypot from your host machine while allowing you to interact with it safely.

## Prerequisites

1.  **VirtualBox**: Download and install from [virtualbox.org](https://www.virtualbox.org/).
2.  **Vagrant**: Download and install from [vagrantup.com](https://www.vagrantup.com/).

## Quick Start

1.  **Initialize the VM:**
    Open your terminal in this project directory and run:
    ```bash
    vagrant up
    ```
    This command will:
    *   Download an Ubuntu 22.04 virtual machine image.
    *   Set up networking (forwarding ports 2121, 2222, 8000, 8080).
    *   Install Docker, Python, and all necessary dependencies automatically.

2.  **Enter the Rabbit Hole:**
    Once the command finishes, log into the VM:
    ```bash
    vagrant ssh
    ```

3.  **Start the Honeypot:**
    Inside the VM, run the following commands:
    ```bash
    cd /app
    /home/vagrant/rabbithole_env/bin/python rabbithole.py
    ```
    *(Note: We use a specific Python virtual environment created during setup to ensure all dependencies are correct.)*

## Usage

Once running, the honeypot services will be accessible from your **host machine** (your actual computer) at:

*   **Web Dashboard:** [http://localhost:8080](http://localhost:8080)
*   **SSH Honeypot:** `ssh -p 2222 root@localhost`
*   **FTP Honeypot:** `ftp -P 2121 localhost`
*   **Metrics:** [http://localhost:8000](http://localhost:8000)

## Configuration

*   **API Key:** Ensure your `config.json` (or `GEMINI_API_KEY` environment variable) is set in the project folder *before* starting. The `/app` folder inside the VM is synced with your project folder, so changes on your host are immediately reflected in the VM.

## Stopping the VM

To stop the honeypot and shut down the VM:
```bash
vagrant halt
```

To completely remove the VM (and free up disk space):
```bash
vagrant destroy
```

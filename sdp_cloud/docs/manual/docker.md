## Docker Installation

Install docker on your system.

```bash
sudo apt-get update
sudo apt-get install docker.io -y
```

Start docker service.
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Verify docker installation.
```bash
docker --version
```

Run docker on user permission.
```bash
sudo usermod -aG docker $USER
```

Use newgrp to use docker. so that we can use docker without rebooting the system.
```bash
newgrp docker
```
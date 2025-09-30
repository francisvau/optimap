# IDLab Experiment Server Setup

This repository contains scripts to configure a physical node for an IDLab experiment. These scripts automate common setup tasks such as configuring network settings, enabling NAT, extending partitions, and upgrading packages.

## Repository Structure

- `configure-public-ip.sh` – Configures the public IP for the node.
- `enable-nat.sh` – Enables NAT for network routing.
- `extend-partition.sh` – Extends the disk partition to utilize full storage.
- `setup.sh` – Main setup script to configure the node.
- `upgrade-packages.sh` – Updates and upgrades system packages.
- `install-custom-dependencies.sh` - Installs custom dependencies for the experiment.
- `enforce-password-on-sudo.sh` - Enforces password prompt on sudo.
- `configure-firewall.sh` – Configures the firewall to allow required ports.
- `install-helm-dependencies.sh` - Install necessary helm dependencies.
- `non-experiment-setup.sh` - Non-experiment specific setup.

## Setup Instructions

### Prepare the System
Ensure the node has the necessary privileges to run these scripts:
```sh
chmod +x *.sh
```

### Prepare scripts

If you are running the script on an IDLab experiment node, you need to prepare the scripts. The `setup.sh` script will call all the other scripts in the correct order.

Edit the `configure-public-ip.sh` script according to the IDLab experiment [guidelines](https://docs.google.com/document/d/16hFuS-5GQD9QbL3Kz03C2pG1FKWCNGFKgpc5wRoao5w/edit?tab=t.0#heading=h.dpgp513na3c2).

now you can run the `setup.sh` script:
```sh
./setup.sh
```

If you are not running the script on an IDLab experiment node, you can run the `non-experiment-setup.sh` script:
```sh
./non-experiment-setup.sh
```

### Installing the gitlab runner using helm
Add your [runner token](https://docs.gitlab.com/ci/runners/runners_scope/#create-an-instance-runner-with-a-runner-authentication-token) on line 79 of values.yaml.
Make sure your runner is registered:
```sh
gitlab-runner register  --url https://gitlab.ilabt.imec.be/  --token <TOKEN>
```
You are now ready to run `install-helm-dependencies.sh`.

### Setup Secrets for Kubernetes

Several files are not filled in with the correct values. These are secrets that should be filled in by the user. The following files should be filled in:

- `kube-config/postgres/secrets.yaml` – Fill in the `POSTGRES_PASSWORD` and `POSTGRES_USER` field.

- `kube-config/mongodb/secrets.yaml` – Fill in the `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` field.


### Deploying the apps

Now the clusteer is ready to deploy the apps. You can deploy the apps using the following command:
```sh
kubectl apply -f kube-config.yaml -R
```

in the `prod` directory.

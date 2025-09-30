# Optimap Prime Deployment

This project contains the deployment and development configurations for the Optimap Prime project.

## Development - Docker Compose (**recommended**)

The other projects are included as submodules. To succesfully start the development environment, use the following steps. The development environment works on Unix-based systems (Linux, MacOS) and Windows Subsystem for Linux (WSL).

### 1. Cloning the repository

Clone this repository using The following command. Make sure to use the `--recurse-submodules` flag to clone the other projects as well:

```bash
git clone git@gitlab.ilabt.imec.be:designproject/dp2025/14-optimap-prime/infrastructure.git --recurse-submodules
```

Also make sure to update the submodules to the latest commit and check out to main:

```bash
./update-submodules.sh
```

### 2. Configuring hosts

Add the following line to your hosts file.

- **Linux**: `/etc/hosts`
- **Windows+WSL**: `C:\Windows\System32\drivers\etc\hosts`

```
127.0.0.1 optimap.local
```

### 3. Creating a certificate

Run the following command in the `platform/dev/nginx` folder:

```bash
openssl req -x509 -nodes -newkey rsa:4096 -keyout ./certs/key.pem -out ./certs/cert.pem -days 3650
```

This will create a self-signed certificate that will be used by the Nginx reverse proxy. By default, you will get a warning in your browser that the certificate is not trusted, just click on the advanced settings and proceed to the website.

#### Optional: trust the certificate

If you want to trust the certificate, you can add it to your keychain. This process differs per OS/browser.

### 4. Configure the `.env` file

Copy the `.env.example` file in the `platform/dev` folder to `.env`. This file contains the necessary environment variables for the backend and frontend and should be self-explanatory.

### 5. Install the pre-commit hooks

Run the following command in the root of the repository:

```bash
bash ./scripts/setup-hooks.sh
```

The pre-commit hooks will check the formatting and linting of the code before each commit in the `frontend`, `engine` and `backend` projects.

### 6. Start the environment

> **Note**: These are instructions for the docker compose development environment. This will be replaced with a Kubernetes setup in the future.

Run `docker compose up` in `platform/dev`.

This will pull the necessary images and start the necessary services for the backend, frontend and AI-engine.

This will allow you to access the frontend, backend and AI-engine at:

- `https://optimap.local`
- `https://optimap.local/api`
- `https://optimap.local/engine`

## Development - Minikube (**not recommended**)

The other projects are included as submodules. To succesfully start the development environment, use the following steps. The development environment works on Unix-based systems (Linux, MacOS) and Windows Subsystem for Linux (WSL).

### 1. Cloning the repository

Clone this repository using The following command. Make sure to use the `--recurse-submodules` flag to clone the other projects as well:

```bash
git clone git@gitlab.ilabt.imec.be:designproject/dp2025/14-optimap-prime/infrastructure.git --recurse-submodules
```

Also make sure to update the submodules to the latest commit and check out to main:

```bash
./update-submodules.sh
```

### 2. Installing Minikube

Install Minikube by following the instructions on the [official website](https://minikube.sigs.k8s.io/docs/start/).

### 3. Configuring hosts

Add the following line to your hosts file:

- **Linux**: `/etc/hosts`
- **Windows+WSL**: `C:\Windows\System32\drivers\etc\hosts`

```
<minikube.ip> optimap.local
```

Where `<minikube.ip>` is the IP address of the Minikube cluster. You can find this by running `minikube ip`.

### 4. Configure the `.env` file

Copy the `.env.example` file in the root folder to `.env`. This file contains the necessary environment variables for the backend and frontend and should be self-explanatory.

### 5. Install the pre-commit hooks

Run the following command in the root of the repository:

```bash
bash ./scripts/setup-hooks.sh
```

The pre-commit hooks will check the formatting and linting of the code before each commit in the `frontend`, `engine` and `backend` projects.

### 6. Add the secrets

Add `k8s-manifest/smtp-secret.yaml` with the following content:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: smtp-secret
type: Opaque
data:
  SMTP_PW: <password>
```

### 7. Start the environment

Run `bash ./run-minikube.sh --build`. Build the images when you make changes to the dependencies. Changes to the code are reflected automatically. This may take a while the first time you run it. It will pull the necessary images and start the necessary services for the backend, frontend and AI-engine.

This will allow you to access the frontend, backend and AI-engine at:

- `https://optimap.local`
- `https://optimap.local/api`
- `https://optimap.local/engine`

## Production

The setup is based on the assumption that it's hosted in an IDLab experiment.

First to setup the server and install all necessary dependencies run the following commands in the `platform/prod` folder:

```bash
chmod +x server-setup/*.sh
bash server-setup/setup.sh
```

This will install all necessary dependencies and setup the server.

After the server is setup all you need to do is configure local secrets.

The following steps are necessary to configure the secrets:

```bash
sudo htpasswd -B -c /etc/registry/auth/htpasswd username
```

# Backend Setup Guide

## **📌 Requirements**

Before you begin, make sure you have the following software installed:

- **Python 3.12** (check with `python --version` or `python3 --version`)
- **Poetry** (check with `poetry --version`)

## **🚀 Project Installation**

Install the dependencies:

```sh
poetry install
```

Activate the virtual environment (optional, Poetry does this automatically when using `poetry run`):

```sh
poetry shell
```

Make sure your IDE uses the correct Python interpreter to prevent IDE warnings. You can check its path with:

```sh
poetry env info --path
```

## **💻 Starting the Local Development Server**

The development server configuration is part of the [deploy project](https://gitlab.ilabt.imec.be/designproject/dp2025/14-optimap-prime/infrastructure). Head over there and read the instructions to start the development server.

## **📝 Running the linter and formatter**

We use `ruff` for linting and formatting. You can run it with:

```sh
poetry run task lint
poetry run task format
```

## **🧪 Running the tests**

We use `pytest` for testing. You can run the tests with:

```sh
poetry run task test
```

## **📊 Running the tests with coverage**

To check how much of the code is covered by tests, use:
```sh
poetry run task coverage
```

## 🛠 Running Database Migrations with Alembic in Kubernetes

This guide explains how to generate and apply database migrations using Alembic.
There are two options:
- Run the migrations locally using the `alembic` command. This assumes that a database is running and the correct environment variables are set (see `database/alembic/env.py` for the defaults used).
- Run the migrations inside the Docker container.

---

### Step 1: Access the Docker Container

To interact with the application and run commands inside the Docker container, access its shell:

```sh
docker exec -it optimap-backend bash
```

### Step 2: Generate a New Migration (optional)

This step is optional, if you just need to update the database when other people made migrations please skip to step 3.
Once inside the container, use Alembic to generate a new migration. This step analyzes the changes in your SQLAlchemy models and creates a migration script:

```sh
poetry run alembic revision --autogenerate -m "your migration message"
```

### Step 3: Apply the latest Migration

After generating the migration or fetching the latest one, apply it to the database to update the schema:

```sh
poetry run alembic upgrade head
```

### Step 4: Exit the Docker Container

Once the migration is complete, exit the container's shell:

```sh
exit
```
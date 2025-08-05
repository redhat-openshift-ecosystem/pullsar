# Pullsar

The Pullsar is a Python-based project that aims to make usage stats data
for Openshift operators easily accessible to the users.

### What it does:
1. parses operator catalogs to access useful metadata about all mentioned operators and their versions
2. uses the metadata to identify Quay.io repositories with respective container images
3. scans these repositories for usage logs, processes them to retrieve pull counts for each operator
4. stores resulting data in a database for easy access in the future

## Prerequisites
Before you begin, ensure you have the following tools installed on your system:
- [Poetry](https://python-poetry.org/docs/#installation) for Python package management
- [opm](https://docs.okd.io/latest/cli_reference/opm/cli-opm-install.html) for rendering OLM catalog images
- [jq](https://jqlang.org/download/) for processing JSON data
- a container engine like [Podman](https://podman.io/docs/installation) (recommended)

## Setup
### 1. clone the repository:
```
git clone https://github.com/redhat-openshift-ecosystem/pullsar.git
cd pullsar
```

### 2. install dependencies:
```
poetry install
```

### 3. make sure you have access to the registries that contain your OLM catalog images:
```
podman login <REGISTRY>
```

### 4. create a file named `.env` with your configuration (see file `.env.example`):
- set Quay administrator scope OAuth API tokens for each Quay organization you intend to process stats from:
```
QUAY_API_TOKENS_JSON='{"org1":"token1","org2":"token2"}'
```

- set PostgreSQL database configuration (optional):
```
DB_NAME="pullsar_db"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"
```

## Usage

### 1. start local Postgres database (optional):
```
podman-compose up -d
```

### 2. run script, e.g.:
```
poetry run pullsar --catalog-image registry.redhat.io/redhat/community-operator-index:v4.18 --log-days 7
```

## Options
```
usage: pullsar [-h] [--dry-run] [--debug] [--log-days LOG_DAYS] --catalog-image IMAGE [RENDERED_JSON_FILE] [IMAGE [RENDERED_JSON_FILE] ...]

Script for retrieving latest pull counts for all the operators and their versions defined in the input operators catalogs (catalog images or pre-rendered catalog JSON files).

options:
  -h, --help            show this help message and exit
  --dry-run, --test     run the script without saving any data to the database
  --debug               makes logs more verbose
  --log-days LOG_DAYS   number of completed past days to include logs from (default: 7)
  --catalog-image IMAGE [RENDERED_JSON_FILE] [IMAGE [RENDERED_JSON_FILE] ...]
                        operators catalog, e.g. '<CATALOG_IMAGE_PULLSPEC>:<OCP_VERSION>' to be rendered with 'opm' and used in database entry (keeping track of each operator's source
                        catalogs). To skip render, provide optional second argument, a path to a pre-rendered catalog JSON file. Option is repeatable.
```

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

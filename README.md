# Pullsar Web Application

The Pullsar Web Application is a project that aims to make usage stats data
for Openshift operators easily accessible to the users.

### It consists of three apps:
1. [Worker](./apps/worker/README.md) that allows us to collect data about OpenShift operators usage and save them to a database.
2. [REST API](./apps/api/README.md) that serves aggregated operator usage statistics from the database.
3. [Web](./apps/web/README.md) frontend that displays the statistics in a user friendly form.

## Setup:
### 1. clone the repository:
```
git clone https://github.com/redhat-openshift-ecosystem/pullsar.git
cd pullsar
```

### 2. create a file named `.env` with your configuration (see file `.env.example`):
- set PostgreSQL database configuration:
```
DB_NAME="pullsar_db"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"
```
- set API configuration (optional):
```
API_EXPORT_MAX_DAYS="30"
API_ALL_OPERATORS_CATALOG="All Operators"
```

### 3. perform one time configuration of DB start date (for API restriction) by creating table app_metadata in your PostgreSQL DB and inserting the db_start_date, e.g.:
```
CREATE TABLE app_metadata (
    key VARCHAR(50) PRIMARY KEY,
    value VARCHAR(255) NOT NULL,
    description TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO app_metadata (key, value, description)
VALUES ('db_start_date', '2025-08-08', 'The earliest date from which pull count data is available.');
```

### 4. start services (web, API, database):
```
podman-compose up -d
```
- serves web static files at root `localhost:8080`
- REST API at both `localhost:8000/v1/` and `localhost:8080/api/v1/`

## For developers, test API and web with pnpm:
### 1. install dependencies:
```
pnpm install
```

### 2. create `/apps/web/.env` to allow forwarding of requests to API:
```
VITE_API_PROXY_TARGET="http://localhost:8000"
```

### 3. run web and API:
```
pnpm dev
```
- serves web static files at root `localhost:5173`
- REST API at both `localhost:8000/v1/` and `localhost:5173/api/v1/`

### 4. run tests:
```
pnpm test
```

## Run worker. See [worker setup](./apps/worker/README.md):
```
pnpm worker:run -- --help
```

## Build worker using Containerfile:
### 1. build image:
```
podman build -t pullsar-worker:1.0 -f ./apps/worker/Containerfile .
```

### 2. run worker:
```
podman run --rm --env-file .env pullsar-worker:1.0 poetry run pullsar --help
```

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

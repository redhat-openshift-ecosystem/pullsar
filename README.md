# Pullsar Web Application

The Pullsar Web Application is a project that aims to make usage stats data
for Openshift operators easily accessible to the users.

### It consists of three apps:
1. [Worker](./apps/worker/README.md) that allows us to collect data about OpenShift operators usage and save them to a database.
2. [REST API](./apps/api/README.md) that serves aggregated operator usage statistics from the database.
3. [Web](./apps/web/README.md) frontend that displays the statistics in a user friendly form.

## Web and API development setup:
### 1. clone the repository:
```
git clone https://github.com/redhat-openshift-ecosystem/pullsar.git
cd pullsar
```

### 2. install dependencies:
```
pnpm install
```

### 3. create a file named `.env` with your configuration (see file `.env.example`):
- set PostgreSQL database configuration:
```
DB_NAME="pullsar_db"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"
```

### 4. start local Postgres database (optional):
```
podman-compose up -d
```

## Web and API testing:
### 1. run web and API:
```
pnpm dev
```

### 2. run tests
```
pnpm test
```

## Run worker. See [worker setup](./apps/worker/README.md):
```
pnpm worker:run -- --help
```

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

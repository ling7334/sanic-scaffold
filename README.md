# scaffold
> python microservices scaffold build with sanic, sqlalchemy and pydantic

[![codecov](https://codecov.io/gh/ling7334/sanic-scaffold/branch/main/graph/badge.svg?token=UvXvZbTLGv)](https://codecov.io/gh/ling7334/sanic-scaffold)
## Tech Stacks

| Stack | Package | Version | Remark |
| ----- |  ----- | ----- | ----- |
| Web framework | Sanic | ^22.6.0 | performence |
| Database ORM | SQLAlchemy | ^1.4 | async introduced after 1.4 |
| DB connector | asyncpg | ^0.25.0 | async |
| Validation | pydantic | ^1.9.1 | |
| Dependency management | poetry | ^1.1.13 |  |
| Unit test | pytest，sanic-testing |  |  |

## Directory

``` tree
├── .vscode  
├── controllers  
│	└─ V1  
├── docs  
├── exceptions  
├── middleware  
├── models  
├── rabbitmq  
│	├─ consumers  
│	└─ messages  
├── scripts  
├── services  
├── statics  
├── tasks  
├── tests  
└── utils  
```

## Files

| File | Description |
| --- | --- |
| `.gitignore` | Define all files need to be ignored by git |
| `LICENSE` | Project license |
| `config.json` | Application settings |
| `Procfile` | Heroku deployment config file |
| `poetry.lock` | Poetey lock file contain all dependency with version |
| `py.typed` | Empty file indicate the project is fully typed |
| `pyproject.toml` | Project configuration |
| `README.md` | Project description file |
| `server.py` | Project entry |
| `settings.py` | Setting definition |
| `setup.py` | Contain setup function for application |
| `version.py` | Define the verison of project |

## Installation

poetry is used to manage the project dependency.

### prerequisite

1. python
    Download python3.10 source
    ```bash
    wget https://www.python.org/ftp/python/3.10.5/Python-3.10.5.tar.xz
    ```
2. build-essential
    ```bash
    sudo apt install wget build-essential checkinstall
    sudo apt install libreadline-gplv2-dev libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
    ```

3. install python
    ```bash
    cd /opt
    tar xf Python-3.10.5.tar.zx
    cd Python-3.10.5
    ```

4. compile
    ```bash
    sudo ./configure --enable-optimizations
    sudo make altinstall
    ```
    > `make altinstall` prevent replacing the default python binary `/usr/bin/python`

5. verify
    ```bash
    python3.10 -V
    ```

6. install pip
    ```bash
    sudo apt install python3-pip
    ```

7. poetry

    Poetry is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.  
    > If `poetry` is perferred, see [poetry installation guide](https://python-poetry.org/docs/#installation)

### Dependency
#### Install with poetry
```bash
poetry install
```
##### Install optional dependency

```bash
# Install sentry-sdk
poetry install -E sentry
# Install aio-pika
poetry install -E rabbitmq
# Install orjson
poetry install -E orjson
# or Install all optional dependency
poetry install -E all
```
#### Install with pip
```bash
pip install -r requirements.txt
```

### Configuration
Take advantage of pydantic's setting management, we can use environment variable for configuration.

see [environment variable](https://pydantic-docs.helpmanual.io/usage/settings/#environment-variable-names)
1. environment variable

    environment variable start with `APP_` will be used as configuration.
    ```
    APP_HOST=0.0.0.0
    APP_PORT=5050
    APP_REDIS_DSN=redis://127.0.0.1:6379/0
    APP_DATABASE_READER=postgresql+asyncpg://postgres:123456@localhost:5432/postgres
    ```

2. Config file

    `config.json` will be used as configuration.

    ```json
    {
        "DATABASE_MASTER": "postgresql+asyncpg://postgres:123456@localhost:5432/postgres"
    }
    ```
    Config `DATABASE_MASTER` is set to `postgresql+asyncpg://postgres:123456@localhost:5432/postgres`
    > Caution: pydantic will fetch config from `config.json` every time, removed as controlled environment needed(unit test, CI, etc.)

3. .env file

    poetry don't support .env file, alternatively, we can use it with vscode
    In `.vscode/lanuch.json`
    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Pytest",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "args": [
                    "--cov"
                ],
                "justMyCode": true
            },
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "envFile": "${workspaceFolder}/.env",
                "console": "integratedTerminal",
                "justMyCode": true
            },
            {
                "name": "Python: Start",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/server.py",
                "envFile": "${workspaceFolder}/.env",
                "console": "integratedTerminal",
                "justMyCode": true
            }
        ]
    }
    ```
    This way when we launch the project in vscode, `.env` is used as configuration.

4. docker secret file

    It's a common way to store the password in docker secret file.
    see [Secret Support](https://pydantic-docs.helpmanual.io/usage/settings/#secret-support)

## Run
### Run with poetry
```bash
# serve
poetry run sanic server.app
# debug
poetry run python server.py
# migration
poetry run migrate
```
### Run with python
```bash
# serve
sanic server.app --host {IP地址} --port {端口号} --worker {线程数}
# debug
python3.10 server.py
# migration
python -c 'from asyncio import run; from models.migrate import init_db; run(init_db())'
```
Before everything is up，database need to be initialized.

## Tips
`sanic-ext` is an extension for `sanic`, offer functions like `openapi`, it's in beta.  
`pydantic` is a package used for data validation and settings management using python type annotations.

## Documentation

## Contributing

see [CONTRIBUTING](CONTRIBUTING.md)

## Changelog

see [CHANGELOG](CHANGELOG.md)


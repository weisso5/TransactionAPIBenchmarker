# TransactionAPIBenchmarker
[WIP] Simple REST API that mimics larger application to be used for environment benchmarking

[![Docker Image CI](https://github.com/weisso5/TransactionAPIBenchmarker/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/weisso5/TransactionAPIBenchmarker/actions/workflows/docker-image.yml)
[![CodeQL](https://github.com/weisso5/TransactionAPIBenchmarker/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/weisso5/TransactionAPIBenchmarker/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/weisso5/TransactionAPIBenchmarker/actions/workflows/dependency-review.yml/badge.svg?branch=main)](https://github.com/weisso5/TransactionAPIBenchmarker/actions/workflows/dependency-review.yml)

The main goals are:

* Minimal Complexity
* Mimic Enterprise Application activity at a small scale
  * Including WebSockets
* Benchmarking of different environment scenarios
* Easily traceable by monitoring tools
* Extensible
* Easy to generate _server load_
* Easy to run/setup
* Fun

**This is a work in progress**

## Requirements

* Python 3.6+
* Docker
*  [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started (Run it)

```console
$ docker-compose up --build

requestapiproject-db-1  | 
requestapiproject-db-1  | PostgreSQL Database directory appears to contain a database; Skipping initialization
requestapiproject-db-1  | 
requestapiproject-db-1  | LOG:  redirecting log output to logging collector process
requestapiproject-db-1  | HINT:  Future log output will appear in directory "/var/log/postgresql".
api                     | INFO:     Will watch for changes in these directories: ['/code']
api                     | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api                     | INFO:     Started reloader process [1] using watchgod
api                     | INFO sqlalchemy.engine.Engine select pg_catalog.version()
api                     | INFO sqlalchemy.engine.Engine [raw sql] {}
api                     | INFO sqlalchemy.engine.Engine select current_schema()
api                     | INFO sqlalchemy.engine.Engine [raw sql] {}
api                     | INFO sqlalchemy.engine.Engine show standard_conforming_strings
api                     | INFO sqlalchemy.engine.Engine [raw sql] {}
api                     | INFO sqlalchemy.engine.Engine BEGIN (implicit)
api                     | INFO sqlalchemy.engine.Engine COMMIT
api                     | INFO:     Started server process [8]
api                     | INFO:     Waiting for application startup.
api                     | Starting up
api                     | INFO:     Application startup complete.
```

## Check it

Open your browser at: <a href="http://127.0.0.1:8000/app" class="external-link" target="_blank">http://127.0.0.1:8000/app</a>.

or

Open your browser at: <a href="http://127.0.0.1:8000/app/view" class="external-link" target="_blank">http://127.0.0.1:8000/app/view</a>.


### Even better:

Open your browser at: <a href="http://127.0.0.1:8000/docs" class="external-link" target="_blank">http://127.0.0.1:8000/docs</a>.

You will see the automatic interactive API documentation (provided by <a href="https://github.com/swagger-api/swagger-ui" class="external-link" target="_blank">Swagger UI</a>):
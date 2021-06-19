Flask code samples
=

REST API examples for Flask.


Installation
-

`pip install -r requirements.txt`

Create a copy of `config_example.ini` as `config.ini`.


Usage: dev
-

Requires `api-db` service running in Docker (see below).

Usage:

`python -m <module> --help`

Set up database with initial data (including `admin:admin` user):

`python -m <module> data --help`

or:

`python -m <module>.setup_db --help`


Running tests:

`python -m <module> test`


Usage: Docker
-

Build image:

`docker build -f devops/<module>/Dockerfile -t <image>:latest .` 

or:

```
cd devops/
docker-compose build [service...]
```


Run image:

`docker run -d <image>`

### Build and run `api-db`

```
cd devops/
docker-compose up -d api-db
```


APIs
=


api_simple
-

Using module level functions only for end points.


api_view
-

Using `View` classes for end points.

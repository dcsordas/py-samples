Flask code samples
=

REST API examples for Flask.


Installation
-

`pip install -r requirements.txt`


Usage: dev
-

`python -m <module> --help`

Running tests:

`python -m <module>.test`

or:

`python -m <module> --test`


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


APIs
=

api_basic_auth
-

With basic HTTP authentication.


api_simple
-

Using module level functions only for end points.

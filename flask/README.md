Flask code samples
=

REST API examples for Flask.


Installation
-

`pip install -r requirements.txt`


Usage: dev
-

`python -m <module> --help`

Database needs only to be set up for creating required table(s) and preloading sample data (optional):

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


APIs
=


api_simple
-

Using module level functions only for end points.


api_view
-

Using `View` classes for end points.


Tools
=


For development purposes only.

Dump database
-

Install required package:

`sudo apt install sqlite3`

FROM python:3

# copy resources
COPY /requirements.txt .

# add service
ADD lib/ /lib/
ADD api_basic_auth/ /api_basic_auth/

# install
WORKDIR /
RUN apt-get update
RUN pip install -r requirements.txt

# set up SQLite database
ADD data/ /data/
RUN python -m api_basic_auth.db_setup

# run
CMD python -m api_basic_auth
EXPOSE 8001

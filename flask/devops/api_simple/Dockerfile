FROM python:3

# copy resources
ADD data/ /data/
COPY /requirements.txt .

# add service
ADD lib/ /lib/
ADD api_simple/ /api_simple/

# install
WORKDIR /
RUN apt-get update
RUN pip install -r requirements.txt

# run
CMD python -m api_simple
EXPOSE 8000

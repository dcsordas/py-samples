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

# run
CMD python -m api_basic_auth
EXPOSE 8001

FROM ubuntu:trusty
MAINTAINER Saad Naeem <saadnaeem.dev@gmail.com>


RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /Final-Project/requirements.txt

WORKDIR /Final-Project

RUN pip install -r requirements.txt

COPY . /Final-Project



CMD ["python", "flaskApp.py" ]

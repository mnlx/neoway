# pull official base image
#FROM ubuntu:bionic
FROM python:3.7-alpine3.9

# set work directory
WORKDIR /usr/src/neowaytest

# Adding environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1




# copy project
COPY . /usr/src/neowaytest/

# install dependencies
#RUN apt update
#RUN apt upgrade -y
#RUN apt install -y python3 python3-pip
#RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
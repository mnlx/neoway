# pull official base image
FROM python:3.7-alpine3.9

# set work directory
WORKDIR /usr/src/worker

# Adding environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY ./worker /usr/src/worker/
COPY ./libs /usr/src/worker/libs

# install dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
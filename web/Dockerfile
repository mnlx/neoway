# pull official base image
FROM python:3.7-alpine3.9

# set work directory
WORKDIR /usr/src/web

# Adding environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY ./web /usr/src/web/
COPY ./libs /usr/src/web/libs

# install dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
# base image (Slim images do not have mysql so 'mysql_config' error happens) (We can maybe fix that later)
FROM python:3.10-alpine
# setup environment variable
# ENV DockerHOME = /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
RUN mkdir -p /usr/src/app

# where your code lives
# TODO: $DockerHOME did not work instead of /usr/src/app for the commands below (Fix this later)
WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app

# Install system dependencies
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev mariadb-connector-c-dev

RUN pip install -r requirements.txt

# copy whole project to your docker home directory.
COPY . /usr/src/app

# port where the Django app runs
EXPOSE 8000

RUN ls -a

RUN chmod +x ./wait.sh
ENTRYPOINT ["./wait.sh"]

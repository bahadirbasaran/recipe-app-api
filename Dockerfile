FROM python:3.8-alpine
MAINTAINER Bahadir Basaran

# Run Python in unbuffered mode to not allow Python to buffer the outputs.
ENV PYTHONUNBUFFERED 1

# Copy the dependencies from the local "requirements.txt" to the Docker image.
COPY ./requirements.txt /requirements.txt

# Implement Postgres database and jpeg-dev for Pillow.
RUN apk add --update --no-cache postgresql-client jpeg-dev

# Install their temporary dependencies.
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN /usr/local/bin/python -m pip install --upgrade pip

# Install the specified dependencies.
RUN pip install -r /requirements.txt

# Delete the temproray dependencies after the installation.
RUN apk del .tmp-build-deps

# Create a directory inside the image to store the application source code,
# make it the default directory, copy the source code.
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create the directory vol to store:
# - media (images uploaded by users) that can be shared with other containers.
# - static data (JS, css files etc.)
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Create a user (with limited access) who is going to use the application using
# the Docker image, then switch to the user.
RUN adduser -D user

# Change the ownership of all directories within the vol to the custom user.
RUN chown -R user:user /vol/

# Give owner full permission, the rest can read and execute.
RUN chown -R 755 /vol/web

USER user

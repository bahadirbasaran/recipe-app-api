FROM python:3.8-alpine
MAINTAINER Bahadir Basaran

# Run Python in unbuffered mode to not allow Python to buffer the outputs.
ENV PYTHONUNBUFFERED 1

# Copy the dependencies from the local "requirements.txt" to the Docker image.
COPY ./requirements.txt /requirements.txt

# Implement Postgres database and the temporary dependencies for it.
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev

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

# Create a user (with limited access) who is going to use the application using
# the Docker image, then switch to the user.
RUN adduser -D user
USER user
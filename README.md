# recipe-app-api 
### django Backend REST API for Recipe-based Applications

[![Build Status](https://www.travis-ci.com/bahadirbasaran/recipe-app-api.svg?branch=main)](https://www.travis-ci.com/github/bahadirbasaran/recipe-app-api)

The capabilities of this API, which was developed by following the Test-driven Development methodology and has 100% test coverage, are as follows:
- Creating and updating users
- User authentication
- Creating and updating recipes
- Searching, filtering, sorting recipe objects by ingredients and tags
- Uploading images to recipes

### Getting Started

#### Dependencies

##### Docker

macOS and Windows users can install Docker Desktop which contains both Docker and Docker-Compose tools.
Linux users need to follow the instructions on Get Docker CE for Ubuntu and then Install Docker Compose separately.

You are good to go if you can successfully run:
```sh
docker-compose --version
```



#### To start the project, just run (in the root directory):

```sh
docker-compose up
```
The API will then be available at http://127.0.0.1:8000.

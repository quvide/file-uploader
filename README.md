# file-uploader
Source code for my personal file hosting site

## Usage
Running `docker-compose up` should be enough, provided you have Docker installed. You might want to change the exposed ports in `docker-compose.yaml` though. By default it's only visible to localhost. You're supposed to use a second nginx (or other http server) to implement TLS etc. 

## Configuration
The only configuration file can be found in `backend/app/config.yaml`. The options are commented.

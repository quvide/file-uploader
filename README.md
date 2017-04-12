# file-uploader
Source code for my personal file hosting site

## Usage
Running `docker-compose up` should be enough, provided you have Docker installed. You might want to change the exposed ports in `docker-compose.yaml` though. By default it's only visible to localhost. You're supposed to use a second nginx (or other http server) as a reverse proxy to implement TLS etc.

## Configuration
The only configuration file can be found in `backend/app/config.yaml`. The options are commented. You must set `proxy_set_header X-Real-IP $remote_addr;` in your reverse proxy for IP logging to work.

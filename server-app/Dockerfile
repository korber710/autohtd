# Build from directory above (ie. "..") or use docker-compose.yml
# eg. docker build -f ./downloader-app/Dockerfile .

# Using Python 3.10 image
FROM python:3.10

# Copy files
ADD ./server-app /server-app
ADD ./libs/ /server-app/src/

# Change workdir and install Python requirements
WORKDIR /server-app
RUN pip install -r requirements.txt

# Change workdir for docker-compose.yml to run the apps
WORKDIR /server-app/src
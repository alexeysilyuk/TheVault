FROM ubuntu:latest

LABEL maintainer="Alexey S"

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update -y&&\
  apt install software-properties-common -y &&\
  add-apt-repository ppa:deadsnakes/ppa -y &&\
  apt install python3.10 -y &&\
  apt-get -y install python3-pip -y &&\
  apt-get install python3-dev -y


RUN mkdir -p /home/app/

COPY requirements.txt  /home/app/requirements.txt
COPY .env  /home/app/.env

EXPOSE 5000

COPY src/ /home/app/src
WORKDIR /home/app/src
RUN pip3 install -r  ../requirements.txt
CMD [ "python3", "main.py"]

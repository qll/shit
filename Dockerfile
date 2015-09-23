FROM ubuntu

RUN apt-get update
RUN apt-get install -y python-pil python-matplotlib python-scipy

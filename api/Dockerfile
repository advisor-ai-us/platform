FROM ubuntu:22.04

# install supervisor software
RUN apt-get update && \
 apt-get -y upgrade && \
 apt-get install -y supervisor --no-install-recommends
 
RUN apt install -y curl net-tools telnet

RUN apt install -y python3-pip

RUN apt install -y screen

RUN pip install --no-cache-dir -r requirements.txt

CMD ["/usr/bin/supervisord", "-n","-c","/etc/supervisor/supervisord.conf"]
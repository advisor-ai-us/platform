FROM ubuntu:22.04

# install supervisor software
RUN apt-get update && \
 apt-get -y upgrade && \
 apt-get install -y supervisor --no-install-recommends
 
RUN apt install -y curl net-tools telnet

RUN apt install -y python3-pip

RUN pip install openai

RUN pip install flask

RUN pip install flask-cors

RUN apt install -y screen

RUN pip install python-dotenv

RUN pip install PyMuPDF

RUN pip install stripe

RUN pip install elevenlabs

RUN pip install twilio

CMD ["/usr/bin/supervisord", "-n","-c","/etc/supervisor/supervisord.conf"]
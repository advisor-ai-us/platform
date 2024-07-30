##### Section 1: Common across all grmtech docker containers. #####
FROM registry.gitlab.com/grmtech-oss/docker-images/ubuntu22.04-nginx
RUN apt-get update

# Q) Why am I exporting the environment variable TERM=screen?
#  1. clear gives the error message TERM environment variable not set.
#  2. ls command will not show dirs in a different color.
ENV TERM screen

##### Section 2: Container specific packages #####
RUN apt-get install -y cron git
# I do not want to send the information that I am running nginx
RUN apt-get install -y nginx-extras

# Section3: Letsencrypt wants automated certificate installation, hence its certificates expire in 90 days
# Following lines will install the latest version of certbot
#RUN add-apt-repository ppa:certbot/certbot
#RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y certbot

# What does expose do?
# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. EXPOSE does not make the ports of the container accessible to the host.
# To do that, you must use either the -p flag to publish a range of ports or the -P flag to publish all of the exposed ports.
# Expose port 443 for https
Expose 443

# Most users will enter www.ovlg.com in their browser so we need to respod to port 80. Once we respond to port 80 we will redirect to port 443.
Expose 80

# Docker container runs as long as the command you specify with CMD, ENTRTYPOINT or through the command line is running. 
# Setting deamon off so that nginx runs in the foreground and does not exit.
# I am using CMD instead of entrypoing since CMD can be overridden on the command line easily
# ref: https://www.ctl.io/developers/blog/post/dockerfile-entrypoint-vs-cmd/
# nginx has to be last command since it is running in daemon off. Hence it never returns control and hence if service redis-server start is specified after nginx it will not start.
CMD ["/usr/bin/supervisord", "-n","-c","/etc/supervisor/supervisord.conf"]

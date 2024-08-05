FROM ubuntu:22.04

#RUN apt-get update && apt-get -y dist-upgrade &&\

RUN apt-get update && \
 apt-get -y dist-upgrade && \
 apt-get install -y telnet inetutils-ping net-tools --no-install-recommends && \
 apt-get install -y supervisor --no-install-recommends && apt-get install -y curl --no-install-recommends


# needed to install bower components from supervisor
RUN apt install -y git

#Upgrade Nodejs version help:https://computingforgeeks.com/how-to-install-node-js-on-ubuntu-debian/

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -

# nodejs comes with npm
RUN apt -y install nodejs 

# install 2022 package manager Ref: https://www.npmjs.com/package/pnpm
RUN curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm

# to monitor the running commands
RUN apt -y install screen

# Since using the server as a console to see what is happening hence installing the fish shell
RUN apt-get install --quiet --yes fish

SHELL ["fish", "--command"]

RUN chsh -s /usr/bin/fish

ENV SHELL /usr/bin/fish
ENV LANG=C.UTF-8 LANGUAGE=C.UTF-8 LC_ALL=C.UTF-8

# Increase the value of max_user_instances due to bypass error "Like: EMFILE: too many open files, watch" when run "npm run serve" command help: https://stackoverflow.com/questions/72762834/watchpack-error-watcher-error-emfile-too-many-open-files-watch
RUN sysctl fs.inotify.max_user_instances=256


# Expose port 80 and 8080 for npm
Expose 80 8080 3005

# Docker container runs as long as the command you specify with CMD, ENTRTYPOINT or through the command line is running.
# I am using CMD instead of entrypoing since CMD can be overridden on the command line easily
# ref: https://www.ctl.io/developers/blog/post/dockerfile-entrypoint-vs-cmd/
CMD ["/usr/bin/supervisord", "-n","-c","/etc/supervisor/supervisord.conf"]
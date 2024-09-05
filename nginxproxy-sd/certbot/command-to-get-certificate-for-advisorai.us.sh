#!/bin/bash

#curl https://api.ipify.org/ > test1.txt
serverIP=$(curl https://api.ipify.org/)
if [ $serverIP == "65.19.143.244" ]
then
    echo "in prod"

#The following command need to run for generating new ssl certificate. The following coomands are commentout becouse we will be only renew the certificate.
#certbot certonly --webroot --webroot-path=/var/www/html/ --agree-tos --no-eff-email --email tanmoy@grmtech.com --rsa-key-size 4096 -d www.advisorai.us -d advisorai.us  
    
# --rsa-key-size 4096 this will give 4096 key
# -d is used to specify the domain name
# --no-eff-email opts out of signing up for the EFF mailing list,

    
# The following command check expaire date of all ssl certificates and renewed certificates befour due date. ref:https://www.onepagezen.com/letsencrypt-auto-renew-certbot-apache/   
certbot renew

# Copy the https certificate files to respective domain path where nginx will be read the certificate files.
cp /etc/letsencrypt/live/www.advisorai.us/fullchain.pem /gt/gt-prog-repos/platform/nginxproxy-sd/https-certificates/advisorai.us/
cp /etc/letsencrypt/live/www.advisorai.us/privkey.pem   /gt/gt-prog-repos/platform/nginxproxy-sd/https-certificates/advisorai.us/


else
 echo "not in prod"
fi

#Restart the nginx services.
nginx -s reload


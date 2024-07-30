Q1) What is dhparam?
It is a protocol which allows two parties to negotiate a secret without ever putting that secret on the wire. 
Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0

Q2) What size of dhparam to use?
To get 100 on https://www.ssllabs.com/ssltest/analyze.html?d=www.finadvisorai.com we need to use 4096 prime as per https://github.com/ssllabs/ssllabs-scan/issues/159 

Q3) How to generate the dhparam?
> openssl dhparam 2048 -out /etc/nginx/certs/dhparam.pem
> openssl dhparam -dsaparam -out dhparam.pem 4096

Q4) Why use the parameter -dsparam when generating the key?
https://security.stackexchange.com/questions/95178/diffie-hellman-parameters-still-calculating-after-24-hours



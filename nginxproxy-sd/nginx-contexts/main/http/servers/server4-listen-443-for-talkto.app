# Section 6/6
server {

    # 1/6 Goal: Listen on 443 on any ip address
    # Q) Why dont you specify ip address in listen directive?
    # Since the goal is to run the same confuguration in dev -> drone -> prod
    # added http2 on 18th may 2016 ref: https://www.digitalocean.com/community/tutorials/how-to-set-up-nginx-with-http-2-support-on-ubuntu-16-04
    listen 443 ssl http2;

    # 2/6 Goal: Listen on hostname
    # if I enter https://127.0.0.1/api/ i will get the https warning with the https crossed out.
    # if I use macos app gasmask and enter host file entry 127.0.0.1 www.talkto.app and than enter https://www.talkto.app/api/ I will get proper green bar.
    # as per http://nginx.org/en/docs/http/server_names.html _ is a catchall
    # allowing _ is a risk since on internet people keep probing the ip address with different paths to find vulnerability
    # for e.g. 83.142.229.75 - - [07/May/2018:07:04:14 +0000] "GET /xmlrpc.php HTTP/1.1" 404 169 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"

    server_name www.talkto.app local.www.talkto.app 127.0.0.1;

    # The main page needs to accessed from all over the world, So commented the following 3/6 steps: 	      
    # 3/6
    #if ($allowed_country = "yes") {
    #   set $exclusions 1;
    #}

    # if exclusions are not used then LAN ips will not be able to access and server to server api calls for e.g. for oauth will not work.
    # the $exclusions is defined in /gt/sc-prog-repos/nginxproxy-sd-v1/nginx-contexts/main/http/level-2-http-context.conf
    # Ref: https://stackoverflow.com/questions/17223360/how-to-grant-access-to-a-specific-ip-address-that-is-blocked-by-geoipcountry-i
    #if ($exclusions = "0") {
    #   return 444;
    #}

    # 4/6
    # Goal: Not allowing access on public ip address to prevent bots on internet from probing

    if ($host != "www.talkto.app") {
        set $directIPAccess "${directIPAccess}1";
    }

    if ($host != "local.www.talkto.app") {
        set $directIPAccess "${directIPAccess}1";
    }

    if ($host != "127.0.0.1") {
        set $directIPAccess "${directIPAccess}1";
    }
	      
    if ( $directIPAccess = "111" ) {
        return 444;
    }

    # 5/6: If the user enters http://www.talkto.app:443 do a force https-redirect
    if ($scheme = http) {
        return 301 https://www.talkto.app$request_uri;
    }

    # 6/6: Enable large file uplaods
    # ref: http://cnedelcu.blogspot.com/2013/09/nginx-error-413-request-entity-too-large.html
    client_max_body_size 1000M;

    ######################################################
    # Category B: Secure Nginx
    ######################################################

    # Requirement B1: Enable https certificates
    ssl_certificate /gt/gt-prog-repos/platform/nginxproxy-sd/https-certificates/talkto.app/fullchain.pem;
    ssl_certificate_key /gt/gt-prog-repos/platform/nginxproxy-sd/https-certificates/talkto.app/privkey.pem;

    # Requirement B2: Configure which SSL protocols will we support?
    # TLSv1 TLSv1.1 TLSv1.2 This gives a score of 95.
    # Disabling TLSv1.0 gives 97.
    # Disabling TLSv1.1 gives 100.
    # Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    ssl_protocols TLSv1.2;

    # Requirement B2: Enable SSL sessions Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    # TLS session timeout to 4hrs and increase size of TLS session cache to 40MB:
    ssl_session_cache shared:SSL:40m;
    ssl_session_timeout 4h;

    # Requirement B3: Enable SSL session tickets Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    ssl_session_tickets on;

    # Requirement B3: Configure the correct ssl ciphers
    # What is ssl_ciphers? used to coordinate between client/server on which security algorithms to use when sending and receiving information from each other when using TLS and SSL
    # Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    ssl_prefer_server_ciphers on;
    # The cipher values have been chosen from: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    ssl_ciphers 'AES256+EECDH:AES256+EDH:!aNULL';

    # Requirement B4: Tell nginx to use our own DH key exchange parameters.
    # What is DH key exchange? It is a protocol which allows two parties to negotiate a secret without ever putting that secret on the wire. Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    ssl_dhparam /gt/gt-prog-repos/platform/nginxproxy-sd/dhparams-key/dhparam-4096.pem;

    # Requriement B5: Enable HSTS: Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Requirement B6: Do not allow anyone to open the site in a frame
    # Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    add_header X-Frame-Options DENY;

    # Requirement B7: Prevent mime based attacks
    # Ref: https://stackoverflow.com/questions/18337630/what-is-x-content-type-options-nosniff
    # if the following line is enabled then the error in chrome console is
    # Filed to execute programmatically-generated-master-skills-list.json becasue its mime type is application/json is not executable and strict mime type checking is enabled
    # add_header X-Content-Type-Options nosniff;


    # Requirement B8: Enable SSL stapling Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    # What is SSL stapling? https://en.wikipedia.org/wiki/OCSP_stapling
    # How to check if SSL stapling is working correctly? https://www.ssllabs.com/ssltest/analyze.html?d=www.talkto.app
    ssl_stapling on;
    ssl_stapling_verify on;

    # Requirement B9: Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    ssl_ecdh_curve secp384r1;


    ######################################################
    # Category D: Include all the locations that this nginx will proxy for
    ######################################################

      include /gt/gt-prog-repos/platform/nginxproxy-sd/nginx-contexts/main/http/servers/listen-443-for-sub-domain/advisorai-locations/access-through-all-ip-locations/*.conf;
      include /gt/gt-prog-repos/platform/nginxproxy-sd/nginx-contexts/main/http/servers/listen-443-for-sub-domain/advisorai-locations/access-only-through-trusted-ip-locations/*.conf;
}


# Section 6/6
server {

    # 1/6 Goal: Listen on 443 on any ip address
    # Q) Why dont you specify ip address in listen directive?
    # Since the goal is to run the same confuguration in dev -> drone -> prod
    # added http2 on 18th may 2016 ref: https://www.digitalocean.com/community/tutorials/how-to-set-up-nginx-with-http-2-support-on-ubuntu-16-04
    listen 443 ssl http2;

    # 2/6 Goal: Listen on hostname
    # if I enter https://127.0.0.1/api/ i will get the https warning with the https crossed out.
    # if I use macos app gasmask and enter host file entry 127.0.0.1 www.talkto.app and than enter https://www.talkto.app/api/ I will get proper green bar.
    # as per http://nginx.org/en/docs/http/server_names.html _ is a catchall
    # allowing _ is a risk since on internet people keep probing the ip address with different paths to find vulnerability
    # for e.g. 83.142.229.75 - - [07/May/2018:07:04:14 +0000] "GET /xmlrpc.php HTTP/1.1" 404 169 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"

    server_name talkto.app local.talkto.app;

    # The main page needs to accessed from all over the world, So commented the following 3/6 steps: 	      
    # 3/6
    #if ($allowed_country = "yes") {
    #   set $exclusions 1;
    #}

    # if exclusions are not used then LAN ips will not be able to access and server to server api calls for e.g. for oauth will not work.
    # the $exclusions is defined in /gt/sc-prog-repos/nginxproxy-sd-v1/nginx-contexts/main/http/level-2-http-context.conf
    # Ref: https://stackoverflow.com/questions/17223360/how-to-grant-access-to-a-specific-ip-address-that-is-blocked-by-geoipcountry-i
    #if ($exclusions = "0") {
    #   return 444;
    #}

    # 4/6
    # Goal: Not allowing access on public ip address to prevent bots on internet from probing
    if ($host != "talkto.app") {
        set $directIPAccess "1";
    }

    if ($host != "local.talkto.app") {
        set $directIPAccess "${directIPAccess}1";
    }

    if ( $directIPAccess = "11" ) {
        return 444;
    }

    # 5/6: If the user enters http://talkto.app or https://talkto.app do a force https-redirect
    if ($scheme = http) {
        return 301 https://www.talkto.app$request_uri;
    }
    if ($scheme = https) {
        return 301 https://www.talkto.app$request_uri;
    }
	      
    # 6/6: Enable large file uplaods
    # ref: http://cnedelcu.blogspot.com/2013/09/nginx-error-413-request-entity-too-large.html
    client_max_body_size 1000M;

    ######################################################
    # Category B: Secure Nginx
    ######################################################

    # Requirement B1: Enable https certificates
    ssl_certificate /gt/gt-prog-repos/platform/nginxproxy-sd/https-certificates/talkto.app/fullchain.pem;
    ssl_certificate_key /gt/gt-prog-repos/platform/nginxproxy-sd/https-certificates/talkto.app/privkey.pem;

    # Requirement B2: Configure which SSL protocols will we support?
    # TLSv1 TLSv1.1 TLSv1.2 This gives a score of 95.
    # Disabling TLSv1.0 gives 97.
    # Disabling TLSv1.1 gives 100.
    # Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    ssl_protocols TLSv1.2;

    # Requirement B2: Enable SSL sessions Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    # TLS session timeout to 4hrs and increase size of TLS session cache to 40MB:
    ssl_session_cache shared:SSL:40m;
    ssl_session_timeout 4h;

    # Requirement B3: Enable SSL session tickets Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    ssl_session_tickets on;

    # Requirement B3: Configure the correct ssl ciphers
    # What is ssl_ciphers? used to coordinate between client/server on which security algorithms to use when sending and receiving information from each other when using TLS and SSL
    # Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    ssl_prefer_server_ciphers on;
    # The cipher values have been chosen from: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    ssl_ciphers 'AES256+EECDH:AES256+EDH:!aNULL';

    # Requirement B4: Tell nginx to use our own DH key exchange parameters.
    # What is DH key exchange? It is a protocol which allows two parties to negotiate a secret without ever putting that secret on the wire. Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    ssl_dhparam /gt/gt-prog-repos/platform/nginxproxy-sd/dhparams-key/dhparam-4096.pem;

    # Requriement B5: Enable HSTS: Ref: https://medium.com/@mvuksano/how-to-properly-configure-your-nginx-for-tls-564651438fe0
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Requirement B6: Do not allow anyone to open the site in a frame
    # Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    add_header X-Frame-Options DENY;

    # Requirement B7: Prevent mime based attacks
    # Ref: https://stackoverflow.com/questions/18337630/what-is-x-content-type-options-nosniff
    # if the following line is enabled then the error in chrome console is
    # Filed to execute programmatically-generated-master-skills-list.json becasue its mime type is application/json is not executable and strict mime type checking is enabled
    # add_header X-Content-Type-Options nosniff;


    # Requirement B8: Enable SSL stapling Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    # What is SSL stapling? https://en.wikipedia.org/wiki/OCSP_stapling
    # How to check if SSL stapling is working correctly? https://www.ssllabs.com/ssltest/analyze.html?d=www.talkto.app
    ssl_stapling on;
    ssl_stapling_verify on;

    # Requirement B9: Ref: https://michael.lustfield.net/nginx/getting-a-perfect-ssl-labs-score
    ssl_ecdh_curve secp384r1;

}



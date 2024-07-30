#!/bin/bash
cd /gt/gt-prog-repos/webapp/nginxproxy-sd/trusted-ip-addresses-allowed-to-access-secure-locations
ip1=`getent hosts grm-ae-wan01.nsupdate.info | awk '{ print $1 }'`
ip2=`getent hosts grm-ae-wan02.nsupdate.info | awk '{ print $1 }'`
ip3=`getent hosts grm-ae-wan03.nsupdate.info | awk '{ print $1 }'`
ip4=`getent hosts grm-ae-wan04.nsupdate.info | awk '{ print $1 }'`
#ip5=`getent hosts grm-ae-wan05.nsupdate.info | awk '{ print $1 }'`
ip6=`getent hosts grm-ae-wan06.nsupdate.info | awk '{ print $1 }'`
ip7=`getent hosts grm-ae-wan07.nsupdate.info | awk '{ print $1 }'`
ip8=`getent hosts vk-home-ct.nsupdate.info | awk '{ print $1 }'`   # This is needed for VK home office ct => covington
ip9=`getent hosts grm-he-ps12.nsupdate.info | awk '{ print $1 }'`    # this is needed to access emergnecy server for SC reports
ip10=`getent hosts grm-he-ps13.nsupdate.info | awk '{ print $1 }'`    # this is needed for ansible to log into other servers
ip11="172.16.0.0/12" # Needed since this runs inside a docker and it connects to its own base host server
ip12="127.0.0.1" # Allow connections from localhost for testing
ip13="10.0.0.0/8" # Allow connections from LAN IPs
ip14=`getent hosts grm-ae-wan08.nsupdate.info | awk '{ print $1 }'`
ip15=`getent hosts grm-he-ps03.nsupdate.info | awk '{ print $1 }'` # Allowed IP of he-ps03 server due to take data this server using curl request.
ip16=`getent hosts vk-apt-palo-alto.nsupdate.info | awk '{ print $1 }'`   # This is needed for Vikas Kedia Palo alto apartment
ip17=`getent hosts joann-mundin.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Joann Mundin home own
ip18=`getent hosts vk-ip-when-travelling.nsupdate.info | awk '{ print $1 }'`   # This is the IP that VK has when he is outside his home and he is travelling 
#ip19=`getent hosts grm-ae-wan10.nsupdate.info | awk '{ print $1 }'`
ip20="116.203.134.163" # Allow IP of P20 staging server for post message of ssh security in rocket chat.
ip21=`getent hosts peter-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Peter Gill
ip22=`getent hosts barbara-huynh.grmtech.com | awk '{ print $1 }'`   # This is needed for DR. Barbara Huynh home own
ip23="192.168.0.0/16" # Allow connections from LAN IPs of VK home office as trusted IP to open backup SC site which is running in ct-ps02 server. 
ip24=`getent hosts petergill.nsupdate.info | awk '{ print $1 }'`   # This is needed for Peter Gill1 home  Kol => Kolkata
ip25=`getent hosts robin-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Robin Nelson home  Kol => Kolkata
ip26=`getent hosts sajal-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Sajal Chaudhuri home  Kol => Kolkata
ip27=`getent hosts rrj-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Raj Roshan home  Kol => Kolkata
ip28=`getent hosts ritika-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Ritika Karar home  Kol => Kolkata
ip29=`getent hosts steves-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Steve Smith home Kol => Kolkata
ip30=`getent hosts bianca-cersosimo.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Bianca Cersosimo home
ip31=`getent hosts preet.nsupdate.info | awk '{ print $1 }'`   # This is needed for Peter Gill2 home  Kol => Kolkata
ip32=`getent hosts anita-mukherjee.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Anita Mukherjee home own
ip33=`getent hosts agniva-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Agniva C
ip34=`getent hosts bg-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Bijoesh Roy home  Kol => Kolkata
ip35=`getent hosts sr-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Suvankar Roy home  Kol => Kolkata
ip36=`getent hosts shebna-osanmoh.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr.Shebna Osanmoh own
ip37=`getent hosts ag-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Anirban Ghosh home Kol => Kolkata
ip38=`getent hosts vince-giacomelli.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Vince Giacomelli home own
ip39=`getent hosts aamir-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Aamir Reza home
ip40=`getent hosts sofia-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Sofia R  home Kol => Kolkata
ip41=`getent hosts bernice-ponce.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Bernice ponce
ip42=`getent hosts liang-zhou.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Liang Zhou home own
#ip43=`getent hosts ajm-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Anita Mukherjee home
ip44=`getent hosts vk-office.nsupdate.info | awk '{ print $1 }'`   # This is needed for Vikas Kedia Palo alto office
ip45=`getent hosts brayden-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Brayden R home
ip46=`getent hosts raju-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Raju Das  home Kol => Kolkata
ip47=`getent hosts sajal-home.grmtech.com | awk '{ print $1 }'`   # This is needed for Sajal Chaudhuri home
ip48=`getent hosts td-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Tanmoy Das home
#ip49=`getent hosts ka-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Kehinde Adedayo home
ip50=`getent hosts donna-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Donna Smith home
ip51=`getent hosts tj-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Tanmoy Jana home
ip52=`getent hosts kehinde-adedayo.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Kehinde Adedayo home own
ip53=`getent hosts ellen-machikawa.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Ellen Machikawa own
ip54=`getent hosts nita-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Nita Baker
ip55=`getent hosts prosenjit-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Prosenjit B
ip56=`getent hosts alexcava-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Alexcava home
ip57=`getent hosts sean-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Sean Lewis
ip58=`getent hosts thomas-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Thomas Brown
ip59=`getent hosts sanjay-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Sanjay Singh
ip60=`getent hosts nick-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Nick Denton
ip61=`getent hosts diego-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Diego Sanchez
ip62=`getent hosts nandini-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Nandini De
#ip63=`getent hosts van-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Van Cliburn
#ip64=`getent hosts em-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Ellen Machikawa
ip65=`getent hosts papri01-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Papri Naskar
ip66=`getent hosts sub-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Soumen Bera
ip67=`getent hosts phacharawut-kanchan.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Phacharawut Kanchananakhin own
ip68=`getent hosts barry-stein.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Barry Stanley Stein own
#ip69=`getent hosts bss-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Barry Stanley Stein
ip70=`getent hosts pradip-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Pradip Santra
ip71=`getent hosts shruti-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Shruti Jaswal
ip72=`getent hosts bessy-martirosyan.grmtech.com | awk '{ print $1 }'`   # This is needed for Dr. Bessy Martirosyan own
ip73=`getent hosts antonio-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Antonio Mendez
ip74=`getent hosts harry-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Harry Miller
ip75=`getent hosts oscar-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Oscar Sanchez
#ip76=`getent hosts abhikm-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Abhik Mitra
ip77=`getent hosts sneha-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Sneha S home
#ip78=`getent hosts bm-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Bessy Martirosyan
ip79=`getent hosts subhojit-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Subhojit Ray
ip80=`getent hosts laboni-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Laboni Bhattacharya
ip81=`getent hosts rd-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Rajkumar Dasgupta
ip82=`getent hosts rebecca-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Rebecca D
#ip83=`getent hosts ag1-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Alex Ghobadi
ip84=`getent hosts suraj-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Suraj Lal
ip85=`getent hosts chitra-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Chitrabhanu Chakraborty
#ip86=`getent hosts pk-home.nsupdate.info | awk '{ print $1 }'`   # This is needed for Dr. Phacharawut Kanchananakhin
#ip87=`getent hosts nicola-home-kol.nsupdate.info | awk '{ print $1 }'`   # This is needed for Nicola F home Kol => Kolkata
newString="#This file is updated automatically by update-trusted-ips-list-and-if-changed-then-restart-nginx.sh 
# Trusted IP     \t\t\t #  Why is it trusted1 
allow $ip1;  \t\t\t # IP of grm-ae-wan01.nsupdate.info 
allow $ip2;  \t\t\t # IP of grm-ae-wan02.nsupdate.info
allow $ip3;  \t\t\t # IP of grm-ae-wan03.nsupdate.info
allow $ip4;  \t\t\t # IP of grm-ae-wan04.nsupdate.info
allow $ip6;  \t\t\t # IP of grm-ae-wan06.nsupdate.info
allow $ip7;  \t\t\t # IP of grm-ae-wan07.nsupdate.info 
allow $ip8;  \t\t\t # IP of vk-home-ct.nsupdate.info
allow $ip9;  \t\t\t # IP of grm-he-ps12.nsupdate.info
allow $ip10; \t\t\t # IP of grm-he-ps13.nsupdate.info
allow $ip11; \t\t\t # LAN IP 
allow $ip12; \t\t\t # Localhost IP 
allow $ip13; \t\t\t # LAN IP
allow $ip14; \t\t\t # IP of grm-ae-wan08.nsupdate.info
allow $ip15; \t\t\t # IP of grm-he-ps03.nsupdate.info 
allow $ip16; \t\t\t # Allow IPs of Vikas Kedia Palo Alto apartment
allow $ip17; \t\t\t # Allow IPs of Dr. Joann Mundin home own 
allow $ip18; \t\t\t # IP of vk travelling 
allow $ip20; \t\t\t # Allow IP of P20 staging server.
allow $ip21; \t\t\t # Allow IP of Peter Gill
allow $ip22; \t\t\t # Allow IPs of Dr. Barbara Huynh own 
allow $ip23; \t\t\t # Allow connections from LAN IPs of VK home office
allow $ip24; \t\t\t # Allow IPs of Peter Gill1 home
allow $ip25; \t\t\t # Allow IPs of Robin Nelson home
allow $ip26; \t\t\t # Allow IPs of Sajal Chaudhuri home
allow $ip27; \t\t\t # Allow IPs of Raj Roshan home 
allow $ip28; \t\t\t # Allow IPs of Ritika Karar home
allow $ip29; \t\t\t # Allow IPs of Steve Smith home
allow $ip30; \t\t\t # Allow IPs of Dr. Bianca Cersosimo home
allow $ip31; \t\t\t # Allow IPs of Peter Gill2 home
allow $ip32; \t\t\t # Allow IPs of Dr. Anita Mukherjee own
allow $ip33; \t\t\t # Allow IPs of Agniva C 
allow $ip34; \t\t\t # Allow IPs of Bijoesh Roy home 
allow $ip35; \t\t\t # Allow IPs of Suvankar Roy home
allow $ip36; \t\t\t # Allow IPs of Dr. Shebna Osanmoh own 
allow $ip37; \t\t\t # Allow IPs of Anirban  home
allow $ip38; \t\t\t # Allow IPs of Dr. Vince Giacomelli own
allow $ip39; \t\t\t # Allow IPs of Aamir  home
allow $ip40; \t\t\t # Allow IPs of Sofia R  home
allow $ip41; \t\t\t # Allow IPs of Dr. Bernice Ponce home own
allow $ip42; \t\t\t # Allow IPs of Dr. Liang Zhou home own
allow $ip44; \t\t\t # Allow IPs of Vikas Kedia Palo Alto office
allow $ip45; \t\t\t # Allow IPs of Brayden Home
allow $ip46; \t\t\t # Allow IPs of Raju Das
allow $ip47; \t\t\t # Allow IPs of Sajal Chaudhuri own
allow $ip48; \t\t\t # Allow IPs of Tanmoy Das
allow $ip50; \t\t\t # Allow IPs of Donna Smith Home
allow $ip51; \t\t\t # Allow IPs of Tanmoy Jana
allow $ip52; \t\t\t # Allow IPs of Dr. Kehinde Adedayo own
allow $ip53; \t\t\t # Allow IPs of Dr. Ellen Machikawa own
allow $ip54; \t\t\t # Allow IPs of Nita Baker
allow $ip55; \t\t\t # Allow IPs of Prosenjit B
allow $ip56; \t\t\t # Allow IPs of Alexcava
allow $ip57; \t\t\t # Allow IPs of Sean Lewis
allow $ip58; \t\t\t # Allow IPs of Thomas Brown
allow $ip59; \t\t\t # Allow IPs of Sanjay Singh
allow $ip60; \t\t\t # Allow IPs of Nick Denton
allow $ip61; \t\t\t # Allow IPs of Diego Sanchez
allow $ip62; \t\t\t # Allow IPs of Nandini De
allow $ip65; \t\t\t # Allow IPs of Papri Naskar home
allow $ip66; \t\t\t # Allow IPs of Soumen Bera home
allow $ip67; \t\t\t # Allow IPs of Dr. Phacharawut Kanchananakhin own
allow $ip68; \t\t\t # Allow IPs of Dr. Barry Stanley Stein own
allow $ip70; \t\t\t # Allow IPs of Pradip Santra
allow $ip71; \t\t\t # Allow IPs of Shruti Jaswal
allow $ip72; \t\t\t # Allow IPs of Dr. Bessy Martirosyan own
allow $ip73; \t\t\t # Allow IPs of Antonio Mendez
allow $ip74; \t\t\t # Allow IPs of Harry Miller
allow $ip75; \t\t\t # Allow IPs of Oscar
allow $ip77; \t\t\t # Allow IPs of Sneha
allow $ip79; \t\t\t # Allow IPs of Subhojit Ray
allow $ip80; \t\t\t # Allow IPs of Laboni Bhattacharya
allow $ip81; \t\t\t # Allow IPs of Rajkumar Dasgupta
allow $ip82; \t\t\t # Allow IPs of Rebecca D
allow $ip84; \t\t\t # Allow IPs of Suraj Lal
allow $ip85; \t\t\t # Allow IPs of Chitrabhanu Chakraborty
deny all;"

printf "$newString" > /dev/shm/for-nginx-list-of-ips-resolved-from-trusted-domains.txt
# To check blank IP string, like: 'allow ;' and replace it to '#allow ;'
cd /dev/shm; find -type f -name "for-nginx-list-of-ips-resolved-from-trusted-domains.txt" -exec sed -i 's/allow \;/#allow \;/g' {} \;

newStringForGeoIP="#This file is updated automatically by update-trusted-ips-list-and-if-changed-then-restart-nginx.sh for geoIP Trusted IPs which are in blocked country list  
# Trusted IP     \t\t\t #  Why is it trusted1 
$ip1 1;  \t\t\t # IP of grm-ae-wan01.nsupdate.info 
$ip2 1;  \t\t\t # IP of grm-ae-wan02.nsupdate.info
$ip3 1;  \t\t\t # IP of grm-ae-wan03.nsupdate.info
$ip4 1;  \t\t\t # IP of grm-ae-wan04.nsupdate.info
$ip6 1;  \t\t\t # IP of grm-ae-wan06.nsupdate.info
$ip7 1;  \t\t\t # IP of grm-ae-wan07.nsupdate.info 
$ip8 1;  \t\t\t # IP of vk-home-ct.nsupdate.info
$ip9 1;  \t\t\t # IP of grm-he-ps12.nsupdate.info
$ip10 1; \t\t\t # IP of grm-he-ps13.nsupdate.info
$ip11 1; \t\t\t # LAN IP 
$ip12 1; \t\t\t # Localhost IP
$ip13 1; \t\t\t # LAN IP
$ip14 1; \t\t\t # IP of grm-ae-wan08.nsupdate.info
$ip15 1; \t\t\t # IP of grm-he-ps03.nsupdate.info
$ip16 1; \t\t\t # Allow IPs of Vikas Kedia Palo Alto apartment
$ip17 1; \t\t\t # Allow IPs of Dr. Joann Mundin home own
$ip18 1; \t\t\t # IP of vk travelling
$ip20 1; \t\t\t # Allow IP of P20 staging server.
$ip21 1; \t\t\t # Allow IP of Peter Gill
$ip22 1; \t\t\t # Allow IPs of Dr. Barbara Huynh own
$ip23 1; \t\t\t # Allow connections from LAN IPs of VK home office
$ip24 1; \t\t\t # Allow IPs of Peter Gill1 home
$ip25 1; \t\t\t # Allow IPs of Robin Nelson home
$ip26 1; \t\t\t # Allow IPs of Sajal Chaudhuri home
$ip27 1; \t\t\t # Allow IPs of Raj Roshan home
$ip28 1; \t\t\t # Allow IPs of Ritika Karar home
$ip29 1; \t\t\t # Allow IPs of Steve Smith home
$ip30 1; \t\t\t # Allow IPs of Dr. Bianca Cersosimo home
$ip31 1; \t\t\t # Allow IPs of Peter Gill2 home
$ip32 1; \t\t\t # Allow IPs of Dr. Anita Mukherjee own
$ip33 1; \t\t\t # Allow IPs of Agniva C
$ip34 1; \t\t\t # Allow IPs of Bijoesh Roy home
$ip35 1; \t\t\t # Allow IPs of Suvankar Roy home
$ip36 1; \t\t\t # Allow IPs of Dr. Shebna Osanmoh own
$ip37 1; \t\t\t # Allow IPs of Anirban home
$ip38 1; \t\t\t # Allow IPs of Dr. Vince Giacomelli own
$ip39 1; \t\t\t # Allow IPs of Aamir Reza home
$ip40 1; \t\t\t # Allow IPs of Sofia R home
$ip41 1; \t\t\t # Allow IPs of Dr. Bernice Ponce home own
$ip42 1; \t\t\t # Allow IPs of Dr. Liang Zhou home own
$ip44 1; \t\t\t # Allow IPs of Vikas Kedia Palo Alto Office
$ip45 1; \t\t\t # Allow IPs of Brayden R Home
$ip46 1; \t\t\t # Allow IPs of Raju Das
$ip47 1; \t\t\t # Allow IPs of Sajal Chaudhuri own
$ip48 1; \t\t\t # Allow IPs of Tanmoy Das home
$ip50 1; \t\t\t # Allow IPs of Donna Smith Home
$ip51 1; \t\t\t # Allow IPs of Tanmoy Jana
$ip52 1; \t\t\t # Allow IPs of Dr. Kehinde Adedayo home own
$ip53 1; \t\t\t # Allow IPs of Dr. Ellen Machikawa own
$ip54 1; \t\t\t # Allow IPs of Nita Baker
$ip55 1; \t\t\t # Allow IPs of Prosenjit B
$ip56 1; \t\t\t # Allow IPs of Alexcava
$ip57 1; \t\t\t # Allow IPs of Sean Lewis
$ip58 1; \t\t\t # Allow IPs of Thomas Brown
$ip59 1; \t\t\t # Allow IPs of Sanjay Singh
$ip60 1; \t\t\t # Allow IPs of Nick Denton
$ip61 1; \t\t\t # Allow IPs of Diego Sanchez
$ip62 1; \t\t\t # Allow IPs of Nandini De
$ip65 1; \t\t\t # Allow IPs of Papri Naskar home
$ip66 1; \t\t\t # Allow IPs of Soumen Bera home
$ip67 1; \t\t\t # Allow IPs of Dr. Phacharawut Kanchananakhin own
$ip68 1; \t\t\t # Allow IPs of Dr. Barry Stanley Stein own
$ip70 1; \t\t\t # Allow IPs of Pradip Santra
$ip71 1; \t\t\t # Allow IPs of Shruti Jaswal
$ip72 1; \t\t\t # Allow IPs of Dr. Bessy Martirosyan own
$ip73 1; \t\t\t # Allow IPs of Antonio Mendez
$ip74 1; \t\t\t # Allow IPs of Harry Miller
$ip75 1; \t\t\t # Allow IPs of Oscar
$ip77 1; \t\t\t # Allow IPs of Sneha
$ip79 1; \t\t\t # Allow IPs of Subhojit Ray
$ip80 1; \t\t\t # Allow IPs of Laboni Bhattacharya 
$ip81 1; \t\t\t # Allow IPs of Rajkumar Dasgupta
$ip82 1; \t\t\t # Allow IPs of Rebecca D
$ip84 1; \t\t\t # Allow IPs of Suraj Lal
$ip85 1; \t\t\t # Allow IPs of Chitrabhanu Chakraborty
"
printf "$newStringForGeoIP" > /dev/shm/for-nginx-geoIP-list-of-ips-resolved-from-trusted-domains.txt
# To check blank IP string, like: ' 1;' and replace it to '# 1;'
cd /dev/shm; find -type f -name "for-nginx-geoIP-list-of-ips-resolved-from-trusted-domains.txt" -exec sed -i 's/^ 1\;/# 1\;/g' {} \;

md5OfFile1=`md5sum /dev/shm/for-nginx-list-of-current-trusted-ips-allowed.txt | cut -d " " -f1`
md5OfFile2=`md5sum /dev/shm/for-nginx-list-of-ips-resolved-from-trusted-domains.txt | cut -d " " -f1`

if [ $md5OfFile1 = $md5OfFile2 ]; then
    echo "Files are the same $md5OfFile1 $md5OfFile2 $(date)" >> /dev/shm/for-nginx-update-ip-status.log
    echo "Going to sleep for 60 seconds before exiting"
    sleep 60          # if i do not give this then supervisor complains exited too quickly
else
    echo "Files are different $md5OfFile1 $md5OfFile2 $(date)" >> /dev/shm/for-nginx-update-ip-status.log
    echo "The difference is: "
    diff /dev/shm/for-nginx-list-of-ips-resolved-from-trusted-domains.txt /dev/shm/for-nginx-list-of-current-trusted-ips-allowed.txt >> /dev/shm/for-nginx-update-ip-status.log
    echo "Step1/3: Updating for-nginx-list-of-current-trusted-ips-allowed.txt"
    cp /dev/shm/for-nginx-list-of-ips-resolved-from-trusted-domains.txt /dev/shm/for-nginx-list-of-current-trusted-ips-allowed.txt
    echo "Step2/3: Updating for-nginx-geoIP-list-of-current-trusted-ips-allowed.txt" # This file include in level-2-http-context.conf at "exclusions under geoip_country" section to allow IPs which are in blocked country list.
    cp /dev/shm/for-nginx-geoIP-list-of-ips-resolved-from-trusted-domains.txt /dev/shm/for-nginx-geoIP-list-of-current-trusted-ips-allowed.txt
    echo "Step3/3: Restarting nginx for new ips to take effect"
    nginx -s reload
    sleep 60
fi


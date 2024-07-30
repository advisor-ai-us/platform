Why are 2 files needed?
1. update-masterdb-trusted-ips-if-ips-changed.sh
2. update-nginx-if-ips-changed-and-then-restart-nginx.sh

In nginx we can restrict access based on IP address by running update-nginx-if-ips-changed-and-then-restart-nginx.sh

update-nginx-if-ips-changed-and-then-restart-nginx.sh -> this script fetches the IP address based on dyndns entries from nsupdate.info (login using vikaskedia/vikas12 github) and updates those ip addresses in the file: /dev/shm/for-nginx-current-allowed-ips.txt

The problem is that some users will want to access from home and we have no way to know their ip address.



Discuss with hemkanta since the following was most probably deprecated:

Hence we want to give an interface inside masterDB where a users IP address can be updated manually.

Inside masterdb -> trusted IPs we want to maintain two categories of IP addresses:
1. Updated automatically by a script.
2. Updated manually.

In updated-manually we will not allow more than 1 IP address per internal-user role. We do this restriction of 1 IP address per internal-user role since otherwise too many ip addresses are added as anyone is scared of removing an exisiting IP address.

There will be 3 api's:
1. https://www.savantcare.com/v1/api/trusted-ips/get-manual-ips -> This API is needed so that I can get a list of IPs from here and update it in /dev/shm/for-nginx-current-allowed-ips.txt. Format is a.b.c.d,q.w.e.r,
2. https://www.savantcare.com/v1/api/trusted-ips/get-automated-ips
3. https://www.savantcare.com/v1/api/trusted-ips/set-automated-ip/a.b.c.d/notes

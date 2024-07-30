#!/bin/bash                                                                                                                                                                             
                                                                           
if [[ -z "${roleOfServer}" ]]; then
    echo "Role of server is not set."
    echo "If you are running it on master-for-productoon do -> export roleOfServer=master-for-production"
    echo "If you are running it on slave-for-emergency do -> export roleOfServer=backup-verification"
    echo "If you are running it on alpha do -> export roleOfServer=alpha"
    echo "To undertand the concept read: https://www.savantcare.com/superstars/t/q104-what-are-the-different-server-roles/2742"
    exit;
fi

if [ "${roleOfServer}"  = "master-for-production" ]
then
    docker-compose -f docker-compose.use-to-start-at-hurricane-electric-data-center.yml up -d
elif [ "${roleOfServer}"  = "backup-verification" ]
then
    docker-compose -f docker-compose-use-for-backup-verification-with-custom-ports.yml up -d
elif [ "${roleOfServer}"  = "alpha" ]
then
    docker-compose -f docker-compose-use-for-alpha.yml up -d
else
    docker-compose -f docker-compose.use-to-start-at-hurricane-electric-data-center.yml up -d
fi

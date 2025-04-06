#!/bin/sh

python manage.py migrate

# Set container time
unlink /etc/localtime
ln -s /usr/share/zoneinfo/Universal /etc/localtime

while true;
do
   echo "check pid app"
   ps -ef | grep -v grep | grep -i -e application -e runserver
   if [ $? -ne "0" ];then
    echo "Service started"
    . venv/bin/activate
    python manage.py runserver
   else
       echo " Application not started !!! Please wait on 5 sec to restart"
   fi

   sleep 5
done
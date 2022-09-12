#! /bin/bash

clear

echo "                                                                             "
echo "                                   ▄▄                                    ▄▄  "
echo "  ▄▄█▀▀▀█▄█                      ▀███                        ▀███▀▀▀██▄  ██  "
echo "▄██▀     ▀█                        ██                          ██   ▀██▄     "
echo "██▀       ▀ ▄█▀██▄ ▀███▄███   ▄█▀▀███   ▄▄█▀██▀████████▄       ██   ▄██▀███  "
echo "██         ██   ██   ██▀ ▀▀ ▄██    ██  ▄█▀   ██ ██    ██       ███████   ██  "
echo "██▄    ▀████▄█████   ██     ███    ██  ██▀▀▀▀▀▀ ██    ██       ██        ██  "
echo "▀██▄     ████   ██   ██     ▀██    ██  ██▄    ▄ ██    ██       ██        ██  "
echo "  ▀▀███████▀████▀██▄████▄    ▀████▀███▄ ▀█████▀████  ████▄   ▄████▄    ▄████▄"
echo "                                                                             "
echo "_____________________________________________________________________________"
echo ""
echo " This script will set up the Raspberry Pi with any dependencies required "
echo ""
echo " Please note that the system is developed for a Raspberry Pi 4 and has not"
echo " Been tested with other Pi systems yet. "
echo ""
echo " "

# Install script customization
piUserName="jpk"


#### Developer options
# If installing as a development environment please check the following variables
developerInstall=TRUE
gitName=""
gitEmail=""
gitCred="store"

# Do not change these variables unless the related login the the code base is changed as well
SQL_USER="garden"
SQL_PASS="garden"
REPO_NAME="garden_pi"

# Start the total duration timer
START_TIME=$SECONDS

echo " == INSTALL =="                                                                             
####
t_start=$SECONDS

echo " Install packages"                                                                            
####
apt-get -qq update
apt-get -qq upgrade
apt-get -qq -y install apache2 expect git postgresql-13 python3-dev python3-venv ufw

if [ $developerInstall = TRUE ] 
then
    echo " Install development packages"                                                                            
    apt -qq -y install code
fi

echo " Clone git repos"
####
su - $linuxUser <<HERE
    cd ~
    git clone --quiet https://github.com/Kellrond/garden_pi.git
    git config --global --add safe.directory /home/$piUserName/$REPO_NAME
HERE

duration=($SECONDS - $t_start)
echo " Installs and downloads completed in $duration seconds"



echo " == SETUP =="
####
t_start=$SECONDS

echo " git: user.name, user.email and cedential.helper"
su - $piUserName <<HERE
    git config --global user.email "$gitEmail"
    git config --global user.name "$gitName"
    git config --global credential.helper $gitCred
HERE

echo " postgres: Setup to allow remote connections"
####
echo "\n$SQL_USER             $piUserName               postgres" >> /etc/postgresql/13/main/pg_ident.conf
sed -i "s:#listen_addresses = 'localhost':listen_addresses = '*':g" /etc/postgresql/13/main/postgresql.conf
echo "host    all             all              0.0.0.0/0                       md5" >> /etc/postgresql/13/main/pg_hba.conf
echo "host    all             all              ::/0                            md5" >> /etc/postgresql/13/main/pg_hba.conf
sed -i "s:# Put your actual configuration here:# Put your actual configuration here\nlocal   all             $SQL_USER                                password:g" /etc/postgresql/13/main/pg_hba.conf

echo " postgres: Setup user(s)"
####
su - postgres <<HERE
    /usr/bin/expect <<EOD
        spawn createuser $SQL_USER -sdrlP
        expect "Enter password for new role:"
        send "$SQL_PASS\n"
        expect "Enter it again:"
        send "$SQL_PASS\n"
        expect eof
    EOD
    createdb garden 
HERE

echo "python: create virtual environment (venv)"
####
cd /home/$piUserName/$REPO_NAME/
python3 -m venv venv

echo "python: install dependancies in venv"
/home/$piUserName/$REPO_NAME/venv/bin/python3 -m pip install -q -r /home/$piUserName/$REPO_NAME/documentation/python_pip.txt

duration=($SECONDS - $t_start)
echo " Setup completed in $duration seconds"
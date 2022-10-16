#!/bin/bash

clear

if [ "$EUID" -ne 0 ]
  then 
  echo "Please run script as root"
  echo "sudo ./install.sh"
  exit
fi

clear

echo ""
echo "     █▒▒▒▒    █▒▒▒▒▒▒▒         █▒▒▒▒      █▒▒        █▒▒ "
echo "   █▒    █▒▒  █▒▒    █▒▒     █▒▒    █▒▒   █▒▒        █▒▒ "
echo "  █▒▒         █▒▒    █▒▒   █▒▒        █▒▒ █▒▒   █▒   █▒▒ "
echo "  █▒▒         █▒ █▒▒       █▒▒        █▒▒ █▒▒  █▒▒   █▒▒ "
echo "  █▒▒   █▒▒▒▒ █▒▒  █▒▒     █▒▒        █▒▒ █▒▒ █▒ █▒▒ █▒▒ "
echo "   █▒▒    █▒  █▒▒    █▒▒     █▒▒     █▒▒  █▒ █▒    █▒▒▒▒ "
echo "    █▒▒▒▒▒    █▒▒      █▒▒     █▒▒▒▒      █▒▒        █▒▒ "
echo "                                                         "
echo "_________________________________________________________"
echo ""
echo " This script will set up the Raspberry Pi with any dependencies required "
echo ""
echo " Please note that the system is developed for a Raspberry Pi 4 and has not"
echo " Been tested with other Pi systems yet. "
echo ""
echo ""

# Install script customization
piUserName="jpk"

#### Developer options
# If installing as a development environment please check the following variables
developerInstall=TRUE
desktopInstall=FALSE
gitName="Jordan Kell"
gitEmail="kellrond@gmail.com"
gitCred="store"

# Do not change these variables unless the related login the the code base is changed as well
INSTALL_DIR="/srv"
SQL_USER="grow"
SQL_PASS="grow"
DB_NAME="grow"
REPO_NAME="grow"

# Start the total duration timer
START_TIME=$SECONDS

echo " == INSTALL =="                                                                             
####
t_start=$SECONDS

#### If installing on Ubuntu 22.04 there is a prompt that needs silencing
if test -f "/etc/needrestart/needrestart.conf"
then
    echo "Silence the 'Daemons using outdated libraries' message"
    sed -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g'  /etc/needrestart/needrestart.conf
fi

echo "intall: packages"                                                                            
####

apt-get -qq update > /dev/null
apt-get -qq upgrade > /dev/null
apt-get -qq -y install apache2 expect ffmpeg git libxext6 libsm6 postgresql python3-dev python3-venv ufw > /dev/null

if [ $desktopInstall = TRUE ] 
then
    echo "install: desktop development packages"                                                                            
    apt -qq -y install code
fi

echo "git: clone repo"
####
su - $linuxUser <<HERE
    cd $INSTALL_DIR
    git clone --quiet https://github.com/Kellrond/grow.git
    git config --global --add safe.directory /srv/$REPO_NAME
HERE

duration=($SECONDS - $t_start)
echo "  installs and downloads completed in $duration seconds"


echo " == SETUP =="
####
t_start=$SECONDS

echo "linux: set folder permissions"
####
chown $piUserName:$piUserName -R $INSTALL_DIR/$REPO_NAME
chmod 777 -R $INSTALL_DIR/$REPO_NAME

echo "git: user.name, user.email and cedential.helper"
####
su - $piUserName <<HERE
    git config --global user.email "$gitEmail"
    git config --global user.name "$gitName"
    git config --global credential.helper $gitCred
HERE

chmod 777 -R $INSTALL_DIR/$REPO_NAME

echo "postgres: Setup to allow remote connections"
####
postgres_config_dir=$(find /etc/postgresql -name pg_ident.conf | cut -c1-18)
echo "\n$SQL_USER             $piUserName               postgres" >> $postgres_config_dir/main/pg_ident.conf
sed -i "s:#listen_addresses = 'localhost':listen_addresses = '*':g" $postgres_config_dir/main/postgresql.conf
echo "host    all             all              0.0.0.0/0                       md5" >> $postgres_config_dir/main/pg_hba.conf
echo "host    all             all              ::/0                            md5" >> $postgres_config_dir/main/pg_hba.conf
sed -i "s:# Put your actual configuration here:# Put your actual configuration here\nlocal   all             $SQL_USER                                password:g" $postgres_config_dir/main/pg_hba.conf

echo "postgres: Setup user(s) and create database"
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
createdb $DB_NAME 
HERE

if [ $developerInstall = TRUE ]
then
echo "postgres: Setup test database"
####
su - postgres <<HERE
createdb test_$DB_NAME 
HERE
fi

echo "postgres: restart service"
####
service postgresql restart

echo "postgres: create database schema"
####
su - postgres <<HERE
PGOPTIONS='--client-min-messages=warning' psql -X -q -1 -v ON_ERROR_STOP=1 --pset pager=off -d $DB_NAME -f $INSTALL_DIR/$REPO_NAME/database/scripts/schema.sql
HERE


if [ $developerInstall = TRUE ]
then
echo "postgres: create test database schema"
####
su - postgres <<HERE
PGOPTIONS='--client-min-messages=warning' psql -X -q -1 -v ON_ERROR_STOP=1 --pset pager=off -d test_$DB_NAME -f $INSTALL_DIR/$REPO_NAME/database/scripts/schema.sql
HERE
fi

echo "python: create virtual environment (venv)"
####
cd $INSTALL_DIR/$REPO_NAME/
python3 -m venv venv

echo "python: install dependancies in venv"
####
$INSTALL_DIR/$REPO_NAME/venv/bin/python3 -m pip install -q -r $INSTALL_DIR/$REPO_NAME/install/python_requirements.txt

echo "ufw: allow ports"
#### 
ufw allow 22 > /dev/null   # ssh
ufw allow 5000 > /dev/null # flask dev server
ufw allow 5432 > /dev/null # postgres

echo "ufw: enable firewall"
####
ufw enable

duration=($SECONDS - $t_start)
echo " Setup completed in $duration seconds"

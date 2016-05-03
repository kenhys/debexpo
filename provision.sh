#!/usr/bin/env bash

set -e

# For some reasons the tests want this.
mkdir -p ~/.gnupg

DEBIAN_RELEASE=$(lsb_release -c | awk '{print $2}')

cd ~/debexpo/
if [ $DEBIAN_RELEASE = "wheezy" ]; then
    if ! grep -q backports /etc/apt/sources.list; then
        echo 'deb http://http.debian.net/debian/ wheezy-backports main contrib non-free' | sudo sh -c 'cat >> /etc/apt/sources.list'
    fi
fi
if ! grep -q deb-src /etc/apt/sources.list; then
    echo "deb-src http://mirrors.kernel.org/debian ${DEBIAN_RELEASE} main" | sudo sh -c 'cat >> /etc/apt/sources.list'
    echo "deb-src http://security.debian.org/ ${DEBIAN_RELEASE}/updates main" | sudo sh -c 'cat >> /etc/apt/sources.list'
    echo "deb-src http://mirrors.kernel.org/debian ${DEBIAN_RELEASE}-updates main" | sudo sh -c 'cat >> /etc/apt/sources.list'
fi
export DEBIAN_FRONTEND=noninteractive
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
sudo debconf-set-selections <<< "postfix postfix/mailname string debexpo-dev"
sudo apt-get update
case $DEBIAN_RELEASE in
    wheezy)
        sudo apt-get install postfix python-lxml libapt-pkg-dev python-pip python-dev python-virtualenv python-django=1.7.1-1~bpo70+1 --yes
        sudo apt-get install --yes python-fedmsg -t wheezy-backports
        ;;
    jessie)
        sudo apt-get install postfix python-lxml libapt-pkg-dev python-pip python-dev python-virtualenv python-django python-fedmsg python-apt --yes
        ;;
esac
sudo apt-get build-dep --yes python-lxml
echo '* discard:' | sudo sh -c 'cat > /etc/postfix/discard-transport'
if ! grep -q transport_maps /etc/postfix/main.cf; then
    echo 'transport_maps = hash:/etc/postfix/discard-transport' | sudo sh -c 'cat >> /etc/postfix/main.cf'
fi
sudo postmap /etc/postfix/discard-transport
sudo service postfix restart
if ! [ -f ~/debexpo/venv/bin/python ]; then
    virtualenv venv --system-site-packages
fi
. venv/bin/activate
if [ $DEBIAN_RELEASE = "wheezy" ]; then
    pip install https://launchpad.net/python-apt/main/0.7.8/+download/python-apt-0.8.5.tar.gz
fi
pip install --editable .
paster setup-app development.ini
python setup.py compile_catalog

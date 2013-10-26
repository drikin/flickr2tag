#!/bin/bash
set -e

# Load base utility functions like sunzi.mute() and sunzi.install()
source recipes/sunzi.sh
source recipes/private.sh

# This line is necessary for automated provisioning for Debian/Ubuntu.
# Remove if you're not on Debian/Ubuntu.
export DEBIAN_FRONTEND=noninteractive

echo "xxxxxxxxxxxxxxxxxxxx"
if [ -z "$FLICKR_API" ]; then
    echo "FLICKR_API wsa missing"
    exit
else
    echo "FLICKR_API=$FLICKR_API"
fi
echo "xxxxxxxxxxxxxxxxxxxx"

# Add Dotdeb repository. Recommended if you're using Debian. See http://www.dotdeb.org/about/
# source recipes/dotdeb.sh
# source recipes/backports.sh

# Update apt catalog and upgrade installed packages
sunzi.mute "apt-get update"
sunzi.mute "apt-get -y upgrade"

# Install packages
apt-get -y install git-core ntp curl python python-tornado python-simplejson python-flickrapi nginx supervisor

# Install sysstat, then configure if this is a new install.
if sunzi.install "sysstat"; then
  sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat
  /etc/init.d/sysstat restart
fi

# Set RAILS_ENV
environment=<%= @attributes.environment %>

if ! grep -Fq "RAILS_ENV" ~/.bash_profile; then
  echo 'Setting up RAILS_ENV...'
  echo "export RAILS_ENV=$environment" >> ~/.bash_profile
  source ~/.bash_profile
fi

if ! grep -Fq "FLICKR_API" ~/.bash_profile; then
  echo 'Setting up FLICKR_API...'
  echo "export FLICKR_API=$FLICKR_API" >> ~/.bash_profile
  source ~/.bash_profile
fi

# Install Ruby using RVM
source recipes/rvm.sh
ruby_version=<%= @attributes.ruby_version %>

if [[ "$(which ruby)" != /usr/local/rvm/rubies/ruby-$ruby_version* ]]; then
  echo "Installing ruby-$ruby_version"
  # Install dependencies using RVM autolibs - see https://blog.engineyard.com/2013/rvm-ruby-2-0
  rvm install --autolibs=3 $ruby_version
  rvm $ruby_version --default
  echo 'gem: --no-ri --no-rdoc' > ~/.gemrc

  # Install Bundler
  gem install bundler
fi

# Custom script from here
REPO_NAME='flickr2tag'
REPO_URL='https://github.com/drikin/'${REPO_NAME}'.git'
if [ ! -e ~/git ]; then
  echo 'Create git dir'
  mkdir ~/git; cd ~/git;
  git clone ${REPO_URL}
  chmod 711 /root
else
  echo 'Update git dir'
  cd ~/git/${REPO_NAME};
  git pull
fi

echo 'Setup supervisor'
cp /root/git/flickr2tag/conf/supervisor.conf /etc/supervisor/conf.d/
/usr/bin/pkill supervisord
/usr/bin/supervisord

if sunzi.install "nginx"; then
    echo "Remove nginx default config"
    rm /etc/nginx/sites-enabled/default
    mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf_org
fi

if [ ! -e /etc/nginx/nginx.conf ]; then
  echo 'Enable sites'
  ln -Fs ~/git/flickr2tag/conf/nginx/nginx.conf /etc/nginx/nginx.conf
fi

if [ ! -e /etc/nginx/sites-enabled/flickr2tag.conf ]; then
  ln -Fs ~/git/flickr2tag/conf/nginx/sites-available/flickr2tag.conf /etc/nginx/sites-enabled/flickr2tag.conf
fi

/etc/init.d/nginx restart


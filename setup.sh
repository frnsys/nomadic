# vim-instant-markdown dependencies
gem install pygments.rb
gem install redcarpet
sudo npm -g install git+git://github.com/ftzeng/instant-markdown-d

# Additional Linux dependency.
if [[ -f /etc/debian_version ]]; then
    sudo apt-get install xdg-utils
fi

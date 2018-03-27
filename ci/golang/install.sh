#!/usr/bin/env bash

VERSION="1.10"

GOFILE="go$VERSION.linux-amd64.tar.gz"

#gimme --force $VERSION

#wget https://storage.googleapis.com/golang/$GOFILE -O /tmp/go.tar.gz
wget https://dl.google.com/go/$GOFILE -O /tmp/go.tar.gz

#if [ $? -ne 0 ]; then
#	echo "Go download failed.  Exiting."
#	exit 1
#fi
#
#echo "Extracting Go..."
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
#tar -C "$HOME" -xzf /tmp/go.tar.gz
#mv "$HOME/go" "$HOME/.go"
#
#echo "Preparing system variables..."
#touch "$HOME/.bashrc"
#{
#    echo '# GoLang'
#    echo 'export GOROOT=$HOME/.go'
#    echo 'export PATH=$PATH:$GOROOT/bin'
#    echo 'export GOPATH=$HOME/go'
#    echo 'export PATH=$PATH:$GOPATH/bin'
#} >> "$HOME/.bashrc"


#export GOROOT=$HOME/.go
#export PATH=$PATH:$GOROOT/bin
#export GOPATH=$HOME/go
#export PATH=\$PATH:/usr/lib/go-1.9/bin
export PATH=$PATH:/usr/local/go/bin
#export PATH=$PATH:$GOPATH/bin

#echo "Finishing up..."
#mkdir -p $HOME/go/{src,pkg,bin}
#source $HOME/.bashrc
echo "Go $VERSION successfully installed.\n"
go version
#rm -f /tmp/go.tar.gz

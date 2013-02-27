#!/bin/bash -e

# Install dependencies
sudo apt-get install -y devscripts debhelper

cd `dirname $0`  # Move to top repo directory

# Clean up old artifacts
set +e
rm -rf *.deb
rm -rf *.changes
rm -rf $(find . -name '*.pyc')
set -e

msgfmt -v po/pt_BR.po -o po/endless_photos.mo

# Build package
debuild -i -uc -us -b

# Move package to this directory and clean up
mv ../*photos*.deb .
mv ../*photos*.changes .
rm ../*.build

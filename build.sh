#!/bin/bash -e

# Install dependencies
sudo apt-get install -y devscripts debhelper r1.2-gtkclutter-1.0

cd `dirname $0`  # Move to top repo directory

# Clean up old artifacts
set +e
rm -rf *.deb
rm -rf *.changes
rm -rf $(find . -name '*.pyc')
set -e

python generate_filter_thumbnails.py
msgfmt -v po/pt_BR.po -o po/endless_photos.mo

# Build package
debuild -i -uc -us -b

# Move package to this directory and clean up
mv ../*photos*.deb .
mv ../*photos*.changes .
rm ../*.build

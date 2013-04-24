#!/bin/bash -e

# Install dependencies
sudo apt-get install -y devscripts debhelper gir1.2-gtkclutter-1.0

cd `dirname $0`  # Move to top repo directory

# Clean up old artifacts
set +e
rm -rf *.deb
rm -rf *.changes
rm -rf $(find . -name '*.pyc')
set -e

python generate_filter_thumbnails.py
for po_file in po/*.po
do
    echo "Building binary from $po_file"
    # Extract locale name from path
    locale=$(basename "$po_file")
    locale=${locale%.*}
    outdir=mo/$locale/LC_MESSAGES
    mkdir -p $outdir
    msgfmt -v $po_file -o $outdir/endless_photos.mo
done

# Build package
debuild -i -uc -us -b

# Move package to this directory and clean up
mv ../*photos*.deb .
mv ../*photos*.changes .
rm ../*.build

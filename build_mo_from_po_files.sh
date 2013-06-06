#!/bin/bash -e

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

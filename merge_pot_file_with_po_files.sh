#!/bin/bash -e

for po_file in po/*.po
do
    echo "Merging $po_file"
    msgmerge $po_file po/endless_photos.pot -o $po_file
done

# Bootstrap script for the English app
# Run this script on a clean source checkout to get ready for building.

FILE_MUST_EXIST=src/endless_photos.py
POT_FILE=po/eos-photos.pot

test -n "$srcdir" || srcdir=`dirname "$0"`
test -n "$srcdir" || srcdir=.
olddir=`pwd`

cd $srcdir
test -f $FILE_MUST_EXIST || {
    echo "You must run this script in the top-level checkout directory"
    exit 1
}

# GNU gettext automake support doesn't get along with git
# https://bugzilla.gnome.org/show_bug.cgi?id=661128
touch -t 200001010000 $POT_FILE

# NOCONFIGURE is used by gnome-common
if test -z "$NOCONFIGURE"; then
    echo "This script will run ./configure automatically. If you wish to pass "
    echo "any arguments to it, please specify them on the $0 "
    echo "command line. To disable this behavior, have NOCONFIGURE=1 in your "
    echo "environment."
fi

# Run the actual tools to prepare the clean checkout
mkdir -p m4
autoreconf -fi -I m4 || exit $?
rm -f po/Makevars.template

cd "$olddir"
test -n "$NOCONFIGURE" || "./configure" "$@"
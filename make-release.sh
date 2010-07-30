#!/bin/bash
# Generic script for creating a source tarball
# Released into the public domain.
# Thomas Perl <thpinfo.com/about>; 2010-07-30

NAME=bwmon
VERSION=`python -c 'import bwmon; print bwmon.__version__'`
SOURCES=*

###

RELEASE=${NAME}-${VERSION}
TMPDIR=`mktemp -d`

###

mkdir -p ${TMPDIR}/${RELEASE}/
cp -rpv ${SOURCES} ${TMPDIR}/${RELEASE}/
tar czvf ${RELEASE}.tar.gz -C ${TMPDIR} ${RELEASE}
rm -rf ${TMPDIR}

echo ""
echo "--> " ${RELEASE}.tar.gz


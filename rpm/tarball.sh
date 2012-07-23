#!/bin/bash -e
PROG=`basename $0`
PKG_NAME="aiaiai"

if [ $# -ne 1 ]; then
        echo "Usage: $PROG COMMIT-ISH"
        echo ""
        exit 1
fi

SHA1=`git rev-parse --short "$1"`
# Committer date 
CDATE=`git show --pretty="%ci" "$1" | head -n1 | xargs -I'{}' date -d {} +%Y%m%d`
echo "Creating tarball from $SHA1, commited on $CDATE"
COMMIT_COUNT=`git log --oneline $1 | wc -l`
echo "Number of commits $COMMIT_COUNT"

#ARCH_NAME_BASE="$PKG_NAME-0.0.$COMMIT_COUNT.g$SHA1"
ARCH_NAME_BASE="$PKG_NAME-0.0.$CDATE"
git archive --format=tar --prefix="$ARCH_NAME_BASE/" "$1" | bzip2 > "$ARCH_NAME_BASE.tar.bz2"

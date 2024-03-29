#!/usr/bin/env bash
DIR="$( cd "$( dirname $0 )" && pwd )"
cd $DIR

git submodule sync 
for module in \
    ./chisel; do
    git submodule update --init $module
    cd $module && ./init_submodules.sh
done

exit 0




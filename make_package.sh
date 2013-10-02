#!/bin/bash

scriptname=`basename $0`

if [ "$#" != "2" ]; then
    echo "Usage $scriptname file_name dest_dir"
    exit 1
fi

file_name=$1
dest_dir=$2

# PACKAGE_NAME, PACKAGE_COPY and PACKAGE_REMOVE should be defined here
package_info="./make_package.info"
source $package_info

build_dir=/tmp/glass_prj/builds/$PACKAGE_NAME
rm -rf $build_dir
mkdir -p $build_dir
mkdir -p $dest_dir
for var in "${PACKAGE_COPY[@]}"; do
    cp -r ${var} $build_dir/
done

cd $build_dir

for file in "${PACKAGE_REMOVE[@]}"; do
    rm -rf ${file}
done

tar czpf $dest_dir/$file_name . --exclude "*~"  --exclude "*.pyc" --exclude ".svn"
if [ $? -ne 0 ]; then
    echo "tar failed"
    exit 1
fi

echo "$file_name Ready to deploy"

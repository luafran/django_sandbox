#!/bin/bash
LOG=/var/log/cyclone/daemons/watch_for_new_version.txt
installed_something=0
function process_manifest()
{
    new_manifest=$1

    echo "##### Processing manifest $new_manifest"

    new_file_hash=`grep '^FILE_HASH' $new_manifest | awk '{print $3}'`
    install_dir=`grep '^INSTALL_DIR' $new_manifest | awk '{print $3}'`
    
    installed_manifest=$install_dir/$new_manifest
    installed_file_hash=""
    if [ -f $installed_manifest ]; then
        installed_file_hash=`grep '^FILE_HASH' $installed_manifest | awk '{print $3}'`
    fi

    if [ "$installed_file_hash" != "$new_file_hash" ]; then
        installed_something=1
	install_package $new_manifest
    else
        echo "Found version with same hash. Skipping install"
    fi
}

function install_package()
{
    manifest_file=$1
    back_dir=$PWD
    
    package_name=`grep '^PACKAGE_NAME' $new_manifest | awk '{print $3}'`
    file_name=`grep '^FILE_NAME' $new_manifest | awk '{print $3}'`
    file_hash=`grep '^FILE_HASH' $new_manifest | awk '{print $3}'`
    install_dir=`grep '^INSTALL_DIR' $new_manifest | awk '{print $3}'`
    remove_install_dir=`grep '^REMOVE_INSTALL_DIR' $new_manifest | awk '{print $3}'`
    
    echo "##### Installing package $package_name"
    echo "file_name   = $file_name"
    echo "file_hash   = $file_hash"
    echo "install_dir = $install_dir"
    echo "remove_install_dir = $remove_install_dir"

    rm -rf ${package_name}_*
    s3cmd -c $AWS_CREDENTIAL_FILE --force get s3://portal_deployments/$MML_ENVIRONMENT/$file_name
    downloaded_file_hash=`sha1sum $file_name | awk '{print $1}'`
    if [ "$downloaded_file_hash" != "$file_hash" ]; then
        echo "ERROR: downloaded file hash does not match"
        # TODO: retry or whatever
        return
    fi

    if [ "$remove_install_dir" == "yes" ]; then
        echo "Removing dir $install_dir"
        rm -rf $install_dir
    fi

    mkdir -p $install_dir
    tar xvzf $file_name -C $install_dir
    cd $install_dir/scripts
    chmod +x ./setup.sh
    ./setup.sh
    if [ $? -ne 0 ]; then
        echo "Setup FAILED"
        # TODO: remove dir?
        return
    else
        echo "Setup OK"
    fi

    cd $back_dir
    cp $manifest_file $install_dir
    chown www-data.www-data -R $install_dir
}

####################
# Script main body #
####################

scriptname=`basename $0`

echo "--------> $scriptname"

source /etc/profile
export PATH=$PATH:/sbin:/usr/sbin

export MML_ENVIRONMENT=sandbox

mkdir -p /tmp/sandboxsite_deploys
cd /tmp/sandboxsite_deploys

# Ugly to have /var/sites hardcoded here...
sites_dir="/var/sites"

# Update MML packages
rm -rf *.manifest
s3cmd -c $AWS_CREDENTIAL_FILE --force get s3://portal_deployments/$MML_ENVIRONMENT/*.manifest

for manifest in *.manifest; do
    process_manifest $manifest
done

if [ "$installed_something" = "1" ]; then
    s3cmd -c $AWS_CREDENTIAL_FILE --force put $LOG s3://portal_deployments/$MML_ENVIRONMENT/log_`hostname`_`date +%d_%m_%y_%H:%M:%S`_deploy.txt
fi

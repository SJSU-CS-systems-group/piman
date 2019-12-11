#!/bin/busybox sh
exec 2>&1
set -x
# Send and recv are from skeleton code
send() {
    echo "$1"
}

recv() {
    msg=""
    while read line
    do
        if [ "x$line" == "xEOM" ]
    then
        echo -n "$msg"
        return
    fi
    msg="$msg$line"
    done
    echo -n "$msg"
    return
}

format() {
    send "FORMATTING"
    umount /m
    umount /new_root
    # Code from Ben that formats the partitions and mounts the OS on /m
    sfdisk /dev/mmcblk0 <<EOC
    label: dos
    label-id: 0x5f5d7a31
    device: /dev/mmcblk0
    unit: sectors

    /dev/mmcblk0p1 : start= 8192, size= 88472, type=c
    /dev/mmcblk0p2 : start= 98304, size= 62423040, type=83
EOC
    mkfs.ext4 /dev/mmcblk0p2 -L rootfs

    sfdisk /dev/mmcblk0 <<EOC
    label: dos
    label-id: 0x5f5d7a31
    device: /dev/mmcblk0
    unit: sectors

    /dev/mmcblk0p1 : start= 8192, size= 88472, type=c
    /dev/mmcblk0p2 : start= 98304, size= 62423040, type=83
EOC
    sfdisk --dump /dev/mmcblk0
    mkfs.ext4 /dev/mmcblk0p2 -L rootfs
    mount -t ext4 /dev/mmcblk0p2 /m

    send "FINISHED FORMATTING"
}

mounting() {
    send "MOUNTING"
    mkdir -p /new_root
    mount -t ext4 /dev/mmcblk0p2 /new_root
    send "FINISHED MOUNTING"
}

unmount() {
    send "UNMOUNTING"
    umount /dev/mmcblk0p2
    send "FINISHED UNMOUNTING"
}

makenode() {
    send "MAKING NODES"
    # Workaround for missing dev files (in discussions)
    mkdir /m
    mknod /dev/mmcblk0 b 179 0
    mknod /dev/mmcblk0p1 b 179 1
    mknod /dev/mmcblk0p2 b 179 2
    send "MADE NODES"
}

checkinstalled() {
    send "CHECKING IF INSTALLED"
    (mount -t ext4 /dev/mmcblk0p2 /m && stat /m/bin && send "IS_INSTALLED" && umount /m && mounting) || (send "IS_UNINSTALLED") 
}


# gets a trace of all the commands that are getting executed, printed to stderr
set -x
send "Hello World"
makenode
checkinstalled

while true
do
    req="`recv`"
    send "$req" 
    case "$req" in
    ip)
        # This case was just left over from the skeleton code, left it just in case we would need it later
        send "`ip addr`"
        ;;
    boot)
        # If Pi already has OS, exit out of the script. The script in the init will then switch the root filesystem to new_root
        send "RECIEVED BOOT"
        mounting
        exit 0
        break
        ;;
    format)
        format
        cd /m
        # After the partitions have been formatted, send "FORMATTED" to let Piman know
        # that we are ready to receive the port # that we will transfer the file over
        # Pipe the file input so it would unzip the file
        nc $master 4444 | gunzip | tar -xf -
        # Mounts the OS on /new_root and exits
        mounting
        send "IS_FORMATTED"
        exit 0
        ;;
    reinstall)
        mounting
        rm -rf /*
        unmount
        send "IS_UNINSTALLED" 
        break
        ;;
    *)
        send "Sorry don't know how to do $req"
        ;;
    esac
done
exit 0    



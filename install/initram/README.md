# Hello Protocol

## Navigation
[What is hello_protocol.sh](##What-is-hello_protocol.sh?)   
[Why hello_protocol.sh is designed like this](##What-hello_protocol.sh-is-designed-like-this?)   
[How does hello_protocol.sh work?](##How-does-hello_protocol.sh-work?)   
[Classes and Functions Definitions](##Classes-and-Functions-Definitions)   
*Unfortunately, BitBucket has not fixed header-linking in the README's. Please use `Ctrl + F` to find things in here.*    

## What is hello_protocol.sh?
The script is zipped into a `install/boot/initramfs.gz` with  `install/initram/create_initramfs.gz.sh` and send through TFTP so the Raspberry Pi can create requests from and to the TCP server. This readme is meant to talk about `install/initram/hello_protocol.sh`, however, the `install/initram/init` is also important because it is the script to start hello protocol on boot.

## Why hello_protocol.sh is designed like this?   
Hello protocol is designed to send messages to the TCP of it's progress during installing. It works to signal to the TCP to begin installation of the Pi after it receives all the files from the TCP connection.    

## How does hello_protocol.sh work?    
The pi will receive messages from the TCP and will begin to mount a file system onto the pi and installs rootfs onto the Pi that was sent over through TCP. This was made under your supervisor's (a.k.a Ben) recommendations. Most of the code was given by your supervisor. `/dev/mmcblk0` represents the SD card within the pi. `/dev/mmcblk0p1` represents the first partition of the SD card and `/dev/mmcblk0p2` represents the second partition.    
Hello protocol receives the messages from the TCP connection in the listener loop at the bottom of the code - depending on the message, the switch-case will execute that command that was declared as a function earlier. **Do keep track of what is mounted and unmounted when going through this code.**

Everything below will detail how each function works according to class and it's functionalities. It is ***highly recommended*** that you step through the code to see how it works and immediately ask for clarification for what everything does since the documentation may not be concise in definition. If you would like to see the packets being sent "live", we recommend executing this command below in a separate terminal to monitor the network. Please refer to the [manpages](https://linux.die.net/man/8/tcpdump) for more uses.    
```tcpdump -i ens4```

We are executing this command assuming that you have the following pre-conditions:

1. That you are logged into the Pi Manager's Virtual Machine (VM) via `ssh`.
2. You are using the *bash shell* to execute these commands.
3. We are assuming that `ens4` is the switch's (the switch that contains all the RPi's) IP address. Otherwise, change accordingly in `.env` file. If you do not see the switch's IP address please inform your supervisor. Execute this following command in the VM to verify:            
```ifconfig```
## Classes and Functions Definitions    
---
*Warning: This is ***bash*** script so it will differ from Python*    
It is recommended that you use the Linux manpages to see what the common commands do.
This is how the following documentation will be formatted:
```
Class
Function In Class
1. Brief description
2. Return values
3. Code block (Only Global / Public Functions)
```    
### **Global / Public Functions **
#### Function: send()
*Description*:   
Displays the output of execution into the console for users to see what has been installed. 
      
*Return*: None    
```bash
send() {
    echo "$1"
#    echo EOM
}
```   
      
#### Function: recv()
*Description*:   
Processes the message sent from TCP and echoes out the received message. 

*Return*: None         
```bash
recv() {
    msg=""
    while read line
    do
        if [ "x$line" == "xEOM" ]
    then
        echo -n "$msg"
        return
    fi
    msg="$msg$line
"
    done
    echo -n "$msg"
    return
}
```   

#### Function: format()
*Description*:   
Unmounts any prexisting directory of `/m` and begins to partition the first and second partition with the set here-document (EOC). The `mkfs.ext4 /dev/mmcblk0p2 -L rootfs` command will relabel the second partition to rootfs. The `sfdisk --dump /dev/mmcblk0` will be used to format the partitions of the device to correct any bad last extended partition. Then, the second partition will be relabeled to `rootfs` and proceed to mount in a *ext4* filesystem with the second partition and mount to the `/m`. Afterwards, it would send the message "FINISHED FORMATTING".    

*Return*: None   
```bash
format() {
    send "FORMATTING"
    umount /m
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
```    

#### Function: mounting()
*Description*:   
Sends a description of what action is being taken through TCP and creates a new directory and mounts the second partition to the new directory 

*Return*: None         
```bash
mounting() {
    send "MOUNTING"
    mkdir -p /new_root
    mount -t ext4 /dev/mmcblk0p2 /new_root
    send "FINISHED MOUNTING"
}
```                       

#### Function: unmount()
*Description*:   
Unmounts the second partition and sends status of what has occurred through TCP.

*Return*: None         
```bash
unmount() {
    send "UNMOUNTING"
    umount /dev/mmcblk0p2
    send "FINISHED UNMOUNTING"
}
```

#### Function: makenode()
*Description*:   
Creates the `/m` directory and creates a special file name of type buffered with the MAJOR ID of 179 and minor as 0 for the SD card, the partitions of the SD card also have nodes created with different minor ID's. These are used for creating the file system. 

*Return*: None         
```bash
makenode() {
    send "MAKING NODES"
    # Workaround for missing dev files (in discussions)
    mkdir /m
    mknod /dev/mmcblk0 b 179 0
    mknod /dev/mmcblk0p1 b 179 1
    mknod /dev/mmcblk0p2 b 179 2
    send "MADE NODES"
}
```

#### Function: checkinstalled()
*Description*:   
Determines if the PI has been installed successfully.

*Return*: None         
```bash
checkinstalled() {
    send "CHECKING IF INSTALLED"
    (mount -t ext4 /dev/mmcblk0p2 /m && stat /m/bin && send "IS_INSTALLED" && umount /m && mounting) || (send "IS_UNINSTALLED") 
}
```    
      
#!/bin/sh

echo creating ../initramfs.gz
find . | cpio -H newc -o | gzip -9 > ../boot/initramfs.gz

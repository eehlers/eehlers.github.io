
[Back to Index](nanopi.00.index.md)

[2. Serial Port](nanopi.02.serial_port.md)

# 3. Load Root Partition From SSD

The device can boot from the microSD card, or from eMMC (which is optional).  There is an NVMe SSD slot, but the device is not capable of booting from SSD.  The best you can do is to install the root partition to the SSD and boot from the eMMC.

## Download the SD Images

Go to the [vendor's download link](https://drive.google.com/drive/folders/17e39J34E4308WaKZimcjWO2_daLseAr2) and get the images for SD and SD-to-eMMc.

## Install to the eMMC

Burn the SD-to-eMMc image to a microSD card and install the image to the R6C.  You will have to choose which operating system you want.  For this tutorial I am using ubuntu on both the laptop and the NanoPi.

## Clone the root partition

Now burn the SD image to a microSD card and start up the NanoPi from the SD.  We do this so as not to mount the eMMC partitions.

Do `sudo fdisk -l` to list all mounted partitions.  `/dev/mmcblk0` is the microSD card.  `/dev/mmcblk2` is the eMMC.  `/dev/nvme0n1` is the SSD.  The root partition on the eMMC is `/dev/mmcblk2p8`.

Do `sudo fdisk /dev/nvme0n1` and create the new root partition on the SSD.  Give it the default start offset of 2028, and the same size (7995392) as the existing root partition:

    pi@NanoPi-R6C:~$ sudo fdisk -l /dev/nvme0n1
    Disk /dev/nvme0n1: 465.76 GiB, 500107862016 bytes, 976773168 sectors
    Disk model: CT500P3PSSD8                            
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: dos
    Disk identifier: 0x4a4a7129

    Device         Boot Start     End Sectors  Size Id Type
    /dev/nvme0n1p1       2048 7997439 7995392  3.8G 83 Linux

Format the partition:

    sudo mkfs.ext4 /dev/nvme0n1p1

Copy the contents of the old partition to the new one:

    sudo dd if=/dev/mmcblk2p8 of=/dev/nvme0n1p1

Now you can mount the new partition and take a look at it to confirm that it is okay:

    pi@NanoPi-R6C:~$ mkdir mnt
    pi@NanoPi-R6C:~$ sudo mount /dev/nvme0n1p1 mnt
    pi@NanoPi-R6C:~$ ls mnt
    bin   dev  home  lost+found  mnt  proc  run   snap  sys     tmp  var
    boot  etc  lib   media       opt  root  sbin  srv   system  usr

## Change the root partition (Attempt #1)

On the NanoPi, do `sudo reboot`.  In the serial console, look out for the line below...

    Hit key to stop autoboot('CTRL+C'):

...and when you see it, hit `Ctrl-C`.  Now you are at the U-Boot "monitor" (command line prompt).

Print out the existing value of the boot arguments:

    => print bootargs
    bootargs=storagemedia=sd androidboot.storagemedia=sd androidboot.mode=normal androidboot.dtbo_idx=1

Overwrite it with the existing value, appending `root=/dev/nvme0n1p1`:

    => setenv bootargs ootargs=storagemedia=sd androidboot.storagemedia=sd androidboot.mode=normal androidboot.dtbo_idx=1 root=/dev/nvme0n1p1

Now enter the command below to exit the monitor and continue with the boot:

    => boot

In the output that scrolls by from the serial port, you will see:

    [  274.055328] Kernel command line: bootargs=storagemedia=sd androidboot.storagemedia=sd androidboot.mode=normal androidboot.dtbo_idx=1 root=/dev/mmcblk2p8 androidboot.verifiedbootstate=orange earlycon=uart8250,mmio32,0xfeb50000 console=ttyFIQ0 coherent_pool=1m irqchip.gicv3_pseudo_nmi=0 rw rootfstype=ext4 data=/dev/mmcblk0p9 consoleblank=0 cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory swapaccount=1

Our fix didn't work, it is still loading the root partition from `/dev/mmcblk2p8`.  I did some digging and it turns out that the bootloader disregards any values entered into the monitor (I believe that this is a flaw in the vendor's implementation of U-Boot).  So we will have to do it another way.

## Change the root partition (Attempt #2)

We are going to make a little edit to the source code of the bootloader, and then recompile it and install it.

The instructions for compiling the bootloader are [here](https://wiki.friendlyelec.com/wiki/index.php/NanoPi_R6C#Build_u-boot_v2017.09).  Before you run the build command, edit file `arch/arm/mach-rockchip/board.c`, function `board_fdt_chosen_bootargs`, and add the additional lines shown below:

```c
    bootargs = env_get("bootargs");
    printf("\n###BEFORE\n%s\n###\n", bootargs);     // new code
    env_update("bootargs", "root=/dev/nvme0n1p1");  // new code
    bootargs = env_get("bootargs");                 // new code
    printf("\n###AFTER\n%s\n###\n", bootargs);      // new code
    if (dump)
        printf("## bootargs(merged): %s\n\n", bootargs);

    return (char *)bootargs;
```
Now build U-Boot.

Now you have to rebuild the SD image.  The manufacturer's instructions to do that are [here](https://github.com/friendlyarm/sd-fuse_rk3588/tree/kernel-6.1.y).  Replace the stock `uboot.img` with the one you built.  You can build the SD image to test these changes using the microSD card, and/or the SD-to-eMMC image to apply these changes to the eMMC.

Restart the device.  Now in the serial port you should see the effect of your change:

    ###BEFORE
    bootargs=storagemedia=sd androidboot.storagemedia=sd androidboot.mode=normal androidboot.dtbo_idx=1 root=/dev/mmcblk0p8 androidboot.verifiedbootstate=orange earlycon=uart8250,mmio32,0xfeb50000 console=ttyFIQ0 coherent_pool=1m irqchip.gicv3_pseudo_nmi=0 rw rootfstype=ext4 data=/dev/mmcblk0p9 consoleblank=0 cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory swapaccount=1
    ###

    ###AFTER
    bootargs=storagemedia=sd androidboot.storagemedia=sd androidboot.mode=normal androidboot.dtbo_idx=1 root=/dev/nvme0n1p1 androidboot.verifiedbootstate=orange earlycon=uart8250,mmio32,0xfeb50000 console=ttyFIQ0 coherent_pool=1m irqchip.gicv3_pseudo_nmi=0 rw rootfstype=ext4 data=/dev/mmcblk0p9 consoleblank=0 cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory swapaccount=1
    ###

And it loads the root partition from NVMe.  You can confirm this by executing the command below after you log in to the machine:

    pi@NanoPi-R6C:~$ cat /proc/cmdline 
    bootargs=storagemedia=sd androidboot.storagemedia=sd androidboot.mode=normal androidboot.dtbo_idx=1 root=/dev/nvme0n1p1 androidboot.verifiedbootstate=orange earlycon=uart8250,mmio32,0xfeb50000 console=ttyFIQ0 coherent_pool=1m irqchip.gicv3_pseudo_nmi=0 rw rootfstype=ext4 data=/dev/mmcblk0p9 consoleblank=0 cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory swapaccount=1

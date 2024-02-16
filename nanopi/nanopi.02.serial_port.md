
[Back to Index](nanopi.00.index.md)

[1. Notes](nanopi.01.notes.md)

[3. Load Root Partition From SSD](nanopi.03.partition.md)

# 2. Serial Port

It is easier to troubleshoot problems with the device if you connect to the serial port.  For example this lets you get to the U-Boot command prompt.

You will need a command line utility to connect to the serial port.  The standard is minicom.  I use BootTerm:

    git clone https://github.com/wtarreau/bootterm
    cd bootterm
    make
    sudo make install

There are two USB C ports on the back of the device, one labelled USB-CPD for power, the other labelled DEBUG for the serial port.  Connect a USB cable from the serial port on the R6C to a USB port on your laptop.

On your laptop, do:

    sudo bt -b 1500000

Now power up the NanoPi.  The first time I try this it does not work.  On the laptop I run dmesg and it says:

    [70743.937494] usb 1-11: new full-speed USB device number 26 using xhci_hcd
    [70744.087234] usb 1-11: New USB device found, idVendor=1a86, idProduct=7523, bcdDevice= 2.64
    [70744.087239] usb 1-11: New USB device strings: Mfr=0, Product=2, SerialNumber=0
    [70744.087240] usb 1-11: Product: USB Serial
    [70744.089068] ch341 1-11:1.0: ch341-uart converter detected
    [70744.089565] usb 1-11: ch341-uart converter now attached to ttyUSB0
    [70746.346638] usb 1-11: usbfs: interface 0 claimed by ch341 while 'brltty' sets config #1
    [70746.347190] ch341-uart ttyUSB0: ch341-uart converter now disconnected from ttyUSB0
    [70746.347204] ch341 1-11:1.0: device disconnected
    [70818.398641] usb 1-11: USB disconnect, device number 26

The R6C appears on device ttyUSB0, but some process called brltty grabs the connection before BootTerm can.  So I disable brltty:

    erik@laptop:~$ sudo systemctl stop brltty-udev.service
    erik@laptop:~$ sudo systemctl mask brltty-udev.service
    Created symlink /etc/systemd/system/brltty-udev.service → /dev/null.
    erik@laptop:~$ sudo systemctl stop brltty.service
    erik@laptop:~$ sudo systemctl disable brltty.service

Then I restart everything and now BootTerm shows me the output of the serial port from the NanoPi.

# References

- [BootTerm](https://github.com/wtarreau/bootterm)
- [NanoPi R6C review – Ubuntu 22.04, NVMe SSD, USB debug](https://www.cnx-software.com/2023/04/02/nanopi-r6c-review-ubuntu-22-04-nvme-ssd-usb-debug/)
- [Bootterm – a developer-friendly serial terminal program](https://www.cnx-software.com/2020/12/14/bootterm-a-developer-friendly-serial-terminal-program/)
- [dev/ttyUSB0 device connects then is forced to disconnect by another device](https://askubuntu.com/questions/1454633/dev-ttyusb0-device-connects-then-is-forced-to-disconnect-by-another-device)


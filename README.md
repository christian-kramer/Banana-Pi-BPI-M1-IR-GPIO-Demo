# Banana-Pi-BPI-M1-IR-GPIO-Demo
Resurrecting the Banana Pi BPI-M1 and figuring out how to use its IR receiver and GPIO header again in 2019.

___

For those of you who remember it, the Banana Pi BPI-M1 was the very first Raspberry Pi competitor made by GuangDong BiPai Technology Co., LTD. In appearance, it resembled the Raspberry Pi Model B, with some key differences.

![Raspberry Pi Model B](https://i.imgur.com/1xuRSpT.png)

*Raspberry Pi Model B (above)*

![Banana Pi BPI-M1](http://www.banana-pi.org/images/bpi-images/M1/m14.jpg)

*Banana Pi BPI-M1 (above)*

First, you may notice the SATA port next to the HDMI port, on the Banana Pi. This is actually bootable, and the connector on the corner of the board even provides power for an SSD!

There's also a microphone hiding out next to the RCA jack.

Additionally, there are *two* Micro-USB ports... one is strictly for power, the other is an OTG port.

Above the OTG port are two buttons: Power, and Reset... Unlike the Raspberry Pi, the Banana Pi has native support for shutting down completely, and being able to be turned back on without connecting/disconnecting its power supply.

Finally... Above the USB ports, just barely visible in the above picture is an IR receiver for remote controls. This is what initially caught my eye when I recently acquired a couple BPI-M1s from my cousin. When I saw it, I decided for my first project with the Banana Pi, I wanted to turn on and off an LED connected to a GPIO pin with an IR remote I had lying around. But, oh boy, that was easier said than done.

___

### Challenge #1: Finding an OS

So, first thing to note about the BPI-M1 is that it was never even close to being as popular to its mainstream cousin, the RPi Model B.  When you get a Raspberry Pi, it comes with mountains of forum posts, tutorials, and libraries online to help you figure out how to do just about anything you want. The Banana Pi offers an entirely different experience of "finding your own way" with small hints here and there from various forum users from years ago.

This was made abundantly clear when visiting the BPI-M1 "downloads" page on Banana Pi's website. Every OS image is distributed via a Google Drive link, and every single one has been deleted.

![Downloads](https://i.imgur.com/vqHS4tx.png)

Cool, so... just find it somewhere else, I guess?

Easier said than done. I managed to find a mirror of their Raspbian Jessie Lite image on Baidu Cloud.

![Baidu Cloud](https://i.imgur.com/Vs0Nxip.png)

But something to note about Baidu Cloud is that you really can't use it without an account. They push their "Network Disk Client" *super* hard, and for most files restrict downloads to only their utility.

![Network Disk Client](https://i.imgur.com/uU98Pgf.png)

Something else to note is that you cannot use the Network Disk Client without a Mainland China phone number.

Time to find something else.

Eventually, I stumbled upon [this](https://drive.google.com/drive/folders/0B_YnvHgh2rwjWGgyYlppSXI3N00) Google Drive folder that contains not all, but some of the images for the BPI-M1. Included are Raspbian Jessie Desktop and various versions of Ubuntu 16.04 Server. Hooray!

Settling for Ubuntu instead of Raspbian, I flashed Ubuntu 16.04 2018-01-15 to an SD card, plugged the Banana Pi into the network and a display, threw in a keyboard, and fired it up. Immediately encouraged by the Ubuntu bootup messages, and successfully logging in with credentials: `Username: pi` and `Password: bananapi` I went about setting up the Banana Pi as I would any old Raspberry Pi... Change the password, update `apt-get`, and enable SSH. With all of that done, I tested out SSH to make sure it was working, and that I could log into the Banana Pi from my PC.

Funny enough, though... I couldn't!

### Challenge #2: OpenSSH

I tried rebooting the Banana Pi to see if that would fix anything, and this time the Ubuntu bootup messages were full of red "FAIL" alerts, all pertaining to OpenSSH. What in the world?! What's going on with OpenSSH that would cause it to not run?

Well, I know weird network behavior can sometimes be caused by a clock that's off... come to think of it, I never even set a timezone on this thing. Sure enough, running `timedatectl` showed that this thing thought it was in the Taiwan/Taipei timezone! That's over 12 hours ahead of Minnesota.

A quick `sudo timedatectl set-timezone America/Chicago` and `hwclock --systohc` to sync the RTC chip to the system time, and the Banana Pi now had the correct time settings. Yet still the OpenSSH problem persisted, even after a reboot!

This was all systemd would tell me:

```
ssh.service: main process exited, code=exited, status=255/n/a
Unit ssh.service entered failed state.
ssh.service start request repeated too quickly, refusing to start.
Failed to start OpenBSD Secure Shell server.
Unit ssh.service entered failed state.
```

Not a whole lot.

By dumb luck, I stumbled across this: [https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1811580](https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1811580)

Apparently, Ubuntu 16.04 has a very specific bug with systemd and OpenSSH that prevents having `UsePrivilegeSeparation` set to "yes" in the config file.

Switching this to "no"  mitigates the bug, and OpenSSH runs just fine on the Banana Pi after that.

### Challenge #3: Reading the IR Sensor

This one I figured out by accident as well. While changing the input on my TV to the Banana Pi, I noticed weird characters had appeared in the shell. Initially I was worried it was  a keyboard issue, but then I noticed they only appeared when I pushed buttons on the remote! "Does this thing show up as a keyboard?" I wondered... and after figuring out how to list input devices in Ubuntu (`sudo cat /proc/bus/input/devices`) I noticed it did show up!

```
pi@bpi-iot-ros-ai:~$ sudo cat /proc/bus/input/devices
[sudo] password for pi:
I: Bus=0019 Vendor=0001 Product=0001 Version=0100
N: Name="axp20-supplyer"
P: Phys=m1kbd/input2
S: Sysfs=/devices/platform/sunxi-i2c.0/i2c-0/0-0034/axp20-supplyer.28/input/inpu                                                                                                                                                                                               t0
U: Uniq=
H: Handlers=kbd event0
B: PROP=0
B: EV=7
B: KEY=100000 0 0 0
B: REL=0

I: Bus=0019 Vendor=0001 Product=0001 Version=0100
N: Name="sunxi-ir"
P: Phys=RemoteIR/input1
S: Sysfs=/devices/virtual/input/input1
U: Uniq=
H: Handlers=sysrq rfkill kbd event1
B: PROP=0
B: EV=100003
B: KEY=ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffffe
```

"sunxi-ir" located at /dev/input/event1... I bet I can `cat` that and see what comes through!

But because linux events are timestamped, all that displayed as unicode in the terminal was this garbled mess of ever-changing data whenever I pushed a button. I piped it to `hexdump` with the `-C` flag so I could see everything clearly as bytes.

```
pi@bpi-iot-ros-ai:~$ sudo cat /dev/input/event1 | hexdump -C
00000000  fb b5 48 5d cc f5 05 00  01 00 64 00 01 00 00 00  |..H]......d.....|
00000010  fb b5 48 5d d6 f5 05 00  00 00 00 00 00 00 00 00  |..H]............|
00000020  fb b5 48 5d 89 bc 09 00  01 00 64 00 02 00 00 00  |..H]......d.....|
00000030  fb b5 48 5d 91 bc 09 00  00 00 00 00 01 00 00 00  |..H]............|
00000040  fb b5 48 5d b2 bc 09 00  01 00 64 00 00 00 00 00  |..H]......d.....|
00000050  fb b5 48 5d b7 bc 09 00  00 00 00 00 00 00 00 00  |..H]............|
00000060  fe b5 48 5d 8a d5 0a 00  01 00 22 00 01 00 00 00  |..H]......".....|
00000070  fe b5 48 5d 94 d5 0a 00  00 00 00 00 00 00 00 00  |..H]............|
00000080  fe b5 48 5d 89 9e 0e 00  01 00 22 00 02 00 00 00  |..H]......".....|
00000090  fe b5 48 5d 90 9e 0e 00  00 00 00 00 01 00 00 00  |..H]............|
000000a0  fe b5 48 5d ad 9e 0e 00  01 00 22 00 00 00 00 00  |..H]......".....|
000000b0  fe b5 48 5d b2 9e 0e 00  00 00 00 00 00 00 00 00  |..H]............|
000000c0  ff b5 48 5d e1 25 06 00  01 00 1f 00 01 00 00 00  |..H].%..........|
000000d0  ff b5 48 5d ea 25 06 00  00 00 00 00 00 00 00 00  |..H].%..........|
000000e0  ff b5 48 5d 97 e3 09 00  01 00 1f 00 02 00 00 00  |..H]............|
000000f0  ff b5 48 5d 9e e3 09 00  00 00 00 00 01 00 00 00  |..H]............|
00000100  ff b5 48 5d c1 0a 0a 00  01 00 1f 00 00 00 00 00  |..H]............|
00000110  ff b5 48 5d ca 0a 0a 00  00 00 00 00 00 00 00 00  |..H]............|
00000120  ff b5 48 5d 57 eb 0e 00  01 00 12 00 01 00 00 00  |..H]W...........|
00000130  ff b5 48 5d 61 eb 0e 00  00 00 00 00 00 00 00 00  |..H]a...........|
00000140  00 b6 48 5d e6 53 03 00  01 00 12 00 02 00 00 00  |..H].S..........|
00000150  00 b6 48 5d ee 53 03 00  00 00 00 00 01 00 00 00  |..H].S..........|
00000160  00 b6 48 5d 17 7b 03 00  01 00 12 00 00 00 00 00  |..H].{..........|
00000170  00 b6 48 5d 20 7b 03 00  00 00 00 00 00 00 00 00  |..H] {..........|
00000180  00 b6 48 5d be 1e 09 00  01 00 21 00 01 00 00 00  |..H]......!.....|
00000190  00 b6 48 5d c7 1e 09 00  00 00 00 00 00 00 00 00  |..H]............|
000001a0  00 b6 48 5d c9 c9 0c 00  01 00 21 00 02 00 00 00  |..H]......!.....|
000001b0  00 b6 48 5d d0 c9 0c 00  00 00 00 00 01 00 00 00  |..H]............|
000001c0  00 b6 48 5d fa f0 0c 00  01 00 21 00 00 00 00 00  |..H]......!.....|
000001d0  00 b6 48 5d 03 f1 0c 00  00 00 00 00 00 00 00 00  |..H]............|
000001e0  01 b6 48 5d d9 10 01 00  01 00 28 00 01 00 00 00  |..H]......(.....|
000001f0  01 b6 48 5d e2 10 01 00  00 00 00 00 00 00 00 00  |..H]............|
00000200  01 b6 48 5d 8a da 04 00  01 00 28 00 02 00 00 00  |..H]......(.....|
00000210  01 b6 48 5d 92 da 04 00  00 00 00 00 01 00 00 00  |..H]............|
00000220  01 b6 48 5d ae da 04 00  01 00 28 00 00 00 00 00  |..H]......(.....|
00000230  01 b6 48 5d b3 da 04 00  00 00 00 00 00 00 00 00  |..H]............|
00000240  01 b6 48 5d 7f 34 0a 00  01 00 0b 00 01 00 00 00  |..H].4..........|
00000250  01 b6 48 5d 88 34 0a 00  00 00 00 00 00 00 00 00  |..H].4..........|
00000260  01 b6 48 5d 46 02 0e 00  01 00 0b 00 02 00 00 00  |..H]F...........|
00000270  01 b6 48 5d 4d 02 0e 00  00 00 00 00 01 00 00 00  |..H]M...........|
00000280  01 b6 48 5d 69 02 0e 00  01 00 0b 00 00 00 00 00  |..H]i...........|
00000290  01 b6 48 5d 6e 02 0e 00  00 00 00 00 00 00 00 00  |..H]n...........|
```

Keep in mind, each line is a "message" sent from the remote. Now, if you look at the 11th byte from the left, you'll notice that's the "magic" byte, indicating which button was pressed on the remote. On my remote, I hit "power" and "volume up" and "volume down"  and a couple others to generate this output. The button IDs are `64`, `22`, `1f`, `12`, `21`, `28`, and `0b` repeated a few times, because when you press a button on an IR remote, it will keep sending that same message over and over again until it's released. Well, mostly the same message... There is another piece of information that is encoded: "button up", "button down", or "button held". If you look at the 13th byte of the message, you'll notice it's always `00`, `01`, or `02`. `01` means "button down", `02` means "button up", and `00` means button held. The shortest of button presses will always have one of each of these types, or 3 messages total for one press: `button down`, `button held`, and then finally `button up`. Pretty simple!

Now let's make those buttons on our remote do something.

### Challenge #4: GPIO

Now, this is where I was worried things were going to go really south... A *lot* of Banana Pi examples use the WiringPi C library to control GPIO, and WiringPi isn't supported anymore. It works fine on Raspbian, but I'm using Ubuntu for my Banana Pi... and try as I might, I could not for the life of me get `blink.c` from the WiringPi examples to compile on Ubuntu 16.04. It's just missing way too many dependencies.

Besides, I wanted to see if I could get Python working with the GPIO so I could treat this similarly to a Raspberry Pi.

I wondered... "can I just use the regular RPi.GPIO library with this thing?"

Well, as I found out, the answer is no. RPi.GPIO even has an error that clearly states: `RuntimeError: This module can only be run on a Raspberry Pi!` Great! That's exactly what I'm trying to circumvent! Thanks, RPi.GPIO!

After a quick Google search, I found a fork of RPi.GPIO specifically for the Banana Pi called [RPi.GPIO_BP](https://github.com/LeMaker/RPi.GPIO_BP). After I ran 
```
python setup.py install                 
sudo python setup.py install
```

exactly as the README said, it worked absolutely flawlessly.

Here's my Python script I wrote to take input from `/dev/input/event1` to toggle a GPIO pin.

```
import RPi.GPIO as GPIO
from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/input/event1')

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
                print(event)
                if event.code == 1:
                        GPIO.output(12, GPIO.HIGH)
                if event.code == 255:
                        GPIO.output(12, GPIO.LOW)
```
The GPIO pinout is the same as the RPi Model A/B, so it was pretty easy to figure out which GPIO pin to specify in my program.

The remote I was using had separate "on" and "off" buttons, of values `1` and `255` respectively, which is why I didn't make a toggle portion of my program.

To see it work:
[https://i.gyazo.com/7b71b17713efd810f77512d742e31b33.gif](https://i.gyazo.com/7b71b17713efd810f77512d742e31b33.gif)


___

And... that was pretty much it! I did, during my testing, add user `pi` to the `input` group in Ubuntu, to allow sudo-less access to `/dev/input/eventx` devices. I don't know if there are any direct security vulnerabilities incurred by this addition, but it is something you can do to avoid running your program with root permissions.

In short:

1. Change UsePrivilegeSeparation from "yes" to "no" in `/etc/ssh/sshd_config`
2. Change Timezone to your own with `timedatectl set-timezone America/Chicago` (for example)
3. Update Hardware Clock with `hwclock --systohc` (needs to be done every time it's unplugged)
4. Get RPi.GPIO at `https://github.com/LeMaker/RPi.GPIO_BP`
5. Add your current user to input group with `adduser pi input` (optional)

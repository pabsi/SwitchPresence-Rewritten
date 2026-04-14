# SwitchPresence-Rewritten

Forked from https://github.com/SunResearchInstitute/SwitchPresence-Rewritten

Change your Discord rich presence to your currently playing Nintendo Switch game! Concept taken from [SwitchPresence](https://github.com/Random0666/SwitchPresence) by [Random](https://github.com/Random0666)<br>

# Build

I was able to build it with `docker run -it --rm -v $PWD:/project -w /project devkitpro/devkita64:20230419 make`.

I tried to update the code to the latest compatible version with libnx and latest `devkitpro/devkita64` but something breaks, as the server does
not seem to be sending data :(

# Install

1. Build
1. You'll get:
   ```
   [drwxr-xr-x]  out/
    ├── [-rw-r--r--]  SwitchPresence-Rewritten-Manager.nro
    └── [-rw-r--r--]  Sysmodule.zip
    ```
1. Copy `SwitchPresence-Rewritten-Manager.nro` to your Switch SD card `sdmc:/switch/switchpresence-rewritten` dir
1. Extract `Sysmodule.zip` contents  to your Switch SD card `sdmc:/` (would ask to override/replace if you had SwitchPresence before). Final dir should be `sdmc:/atmosphere/contents/0100000000000464`
1. Start your switch (or Atmosphere), open SwitchPresence Manager -> Enable the sysmodule.

# Known Issues

The sysmodule stops working after a long deep sleep of the switch. And after waking the switch up, it seems the sysmodule does not respond anymore and needs a restart.
I am looking into it.

# Support

Feel free to open an Issue :)

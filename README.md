# firekeeper-bot
Fire Keeper (a Discord bot)
<http://firekeeper.info/>

## About
Firekeeper.py is a multi-purpose Discord bot lightly themed after the Dark Souls series. It started as a small Python project by [codesavage]() and [k3wio]() and was initially released on its home server on February 14th, 2018. Since then it's grown significantly in both size and scope, and it's fair to say it's something we're proud to call our own.

## Features
- Multi-server functionality
- Module permission control
- Global currency
- Customizable XP generation that can be tied to server roles
- Various games and fun extras, like a nickname generator
- Enhanced mod tools, such as timed muting and permanent warn/ban logs

## Installation
These notes may not be comprehensive, but they should be enough to get you started if you're interested in self-hosting the bot.
`Include our server distro/version`
`Include Python version requirement`
The following modules are required and can be installed with Pip:
- bson
- matplotlib
- pymongo
- dnspython
- twilio
- discord-py
- qrcode
- pymaging - git+git://github.com/ojii/pymaging.git#egg=pymaging
- pymaging-png - git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png
`there are some others not listed here, pull from setup script on the desktop`

`Go over MongoDB setup`
`Go over Twilio setup or feature removal`
`Discord Developer Portal setup and requirements`

## Setup
`Secrets.py setup and sample`
`Initial server config`
- `Admins`
- `XP channels and roles`
- `Module permissions`
- `Logging server setup`

`Verify if any of the below is still necessary`
- `use new collections - prod-ng/test-ng`
- `mkdir logs`
- `mkdir /tmp/firekeeper-qr/`
- `chown firekeeper /tmp/firekeeper-qr/`
- `chmod 755 /tmp/firekeeper-qr/`

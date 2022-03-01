# Simple Reverse IPv6 to IPv4 Proxy
Very Simple Python Reverse IPv6 to IPv4 Proxy. Works on one port. Was originally made for the Derail Valley mod [Remote Dispatch](https://www.nexusmods.com/derailvalley/mods/328)

# How to use?

Either you can run the reverse_proxy.py using Python. I used 3.10 during development so I'd recommend using that.

Or you can just open the reverse_proxy.exe

Then you just enter the port the game server is running at or well press enter if you are using the default Remote Dispatch port.

Then if the app detects you have multiple IPv6 addresses, you get to decide which one to use!

And just like you'd portforward in IPv4, in IPv6 you need to open this port in your router. Make sure the IPv6 displayed there matches the one this app binds to. Routers are sometimes still weird with this.

Then tell your friends to write e.g. '\[1234:&#8203;1234:&#8203;1234:&#8203;1234:&#8203;1234:&#8203;1234:&#8203;1234:&#8203;1234]:7245' in the address bar of their favorite browser and voilá they should be greeted with the Remote Dispatch webapp. Well replace the address with the address the app is showing you, duh.

# Galaxy C2

## Internal

- Set up zero-tier local network controller (on attack box)
- Set up zero-tier local root node (on independent server with IP)
- Build network and point to root node using network controller

- Drop zerotier binary on target
- Manually join target to network using network controller (how do we get the network ID?)
- Run some kind of reverse shell using the new subnet on target

- You have to give each target the moonfile so they know where to go

## External

- Set up zero-tier network controller, or you can just use their root ones
- Create network with a network controller
- Drop zerotier-one binary on target host
- Run script to join network on target machine (assuming they can reach zerotier-one servers, otherwise maybe you need to have your own root server on a public IP?)
- Then it's done, you don't need to expose anything on your end.

- This would all work just fine if you could point to a root node using a DNS entry instead of a static IP...

Lokey I think this would work better for pivoting...

- You have initial access on a network, you want your pivoting traffic to be hidden
- You can set up a self-hosted root node on any owned machine

# Rocket - Get a private IP subnet connection to an infected host (can bypass a lot of firewall restrictions, and you can communicate directly from your host machine without exposing your IP (maybe) - we need to test this)

## This is the easiest thing to do so let's start here...

- You want to  get a callback from a target box to your local one.
    - Setting up a public listener with ngrok is for chumps
- Set up a zerotier network using their public root nodes (can be done locally for automation's sake)
- Drop a payload on the target that has the zerotierone binary, uses it to join the network
- Your locallu running script is constantly checking for new piers and authenticate them (or you can have it manually send the ID back for verification)
- You have IP, go crazy with metasploit or whatever else your payload runs

# Pivoting

- Host root node internally on infected network
- Pivot to piers (with whatever works) and add them to the network
- Oh shit can you then tunnel your local connection in with SSH or something to point to that root node?
- SSH with an outbound port forward to your ngrok domain (which is proxying your SSH client) and you could probably hand code your machine to look for the root on the infected box... or they can hit the root on your machine. You just need SSH or chisel or another port forwarding tool!
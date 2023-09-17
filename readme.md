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

# High Level Layout

The local network manager's networks should be managed by Galaxy. The local node's connection to the local network manager's networks can be temporary (and in fact should be to stay clean).

The local networks are managed by network IDs, the names of which can't be changed. We could keep a data file mapping local network IDs to names to use in the interface.

User can view all networks on the server, and "load / connect" to those networks which joins the local node and authorizes it (it could also authorize all other nodes when loaded, but idk if we should be turning the others on and off). Galaxy should have the ability to list all actively loaded nodes at any time.

Once a network is loaded, the user should be able to view all nodes on that network, and assign names to those nodes (store in local storage). The user can then get a list of all nodes (by name) and relative IPs for that network (can you do that?)

I could also add local DNS, but I think it's best to get the IPs working first.

All of this requires actually having zero tier running on the infected hosts, which requires payloads to do so. The user needs to be able to create a payload that if run on the victim machine (with root I knowww) installs zerotier and joins them to the network. Other things like persistence and evasion would be nice too but we can do that later.

## Self Hosted Root Nodes

This should not be done first, but you can set up self-hosted root nodes (I want to call them starports or something like that) to route traffic for a network. If that is going to happen, two things must take place at a high level:
1. The network creation and management must send those changes to the root node with a public IP
2. A .moon file has to be part of the generated payload that gets run to initialize zero-tier on target machines.
It would be cool to have a teraform file or some kind of automated deployment for root nodes.

## What has to get stored locally

- A json file of all local network IDs and the galaxy names for those networks
- A json file for each local network with all node IDs, local names for those node IDs, and maybe IP addresses?
- This can be one giant json file actually

TBH most of the rest is stored on the zero-tier network manager server

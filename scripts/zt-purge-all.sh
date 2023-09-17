#!/bin/bash
for NWID in $(sudo zerotier-cli listnetworks | cut -d ' ' -f 3 | tail -n +2); do sudo zerotier-cli leave $NWID; done
sudo systemctl stop zerotier-one
sudo rm -rf /var/lib/zerotier-one/controller.d
sudo systemctl start zerotier-one

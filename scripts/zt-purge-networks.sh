#!/bin/bash
sudo systemctl stop zerotier-one
sudo rm -rf /var/lib/zerotier-one/controller.d
sudo systemctl start zerotier-one

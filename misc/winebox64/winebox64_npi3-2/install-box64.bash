#!/bin/bash
set -euxo pipefail

# From https://github.com/Pi-Apps-Coders/box64-debs

# check if .list file already exists
if [ -f /etc/apt/sources.list.d/box64.list ]; then
  sudo rm -f /etc/apt/sources.list.d/box64.list || exit 1
fi
# check if .sources file already exists
if [ -f /etc/apt/sources.list.d/box64.sources ]; then
  sudo rm -f /etc/apt/sources.list.d/box64.sources || exit 1
fi
# download gpg key from specified url
if [ -f /usr/share/keyrings/box64-archive-keyring.gpg ]; then
  sudo rm -f /usr/share/keyrings/box64-archive-keyring.gpg
fi
sudo mkdir -p /usr/share/keyrings
wget -qO- "https://pi-apps-coders.github.io/box64-debs/KEY.gpg" | sudo gpg --dearmor -o /usr/share/keyrings/box64-archive-keyring.gpg
# create .sources file
echo "Types: deb
URIs: https://Pi-Apps-Coders.github.io/box64-debs/debian
Suites: ./
Signed-By: /usr/share/keyrings/box64-archive-keyring.gpg" | sudo tee /etc/apt/sources.list.d/box64.sources >/dev/null
sudo apt update
sudo apt install box64-generic-arm -y

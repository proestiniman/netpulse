#!/bin/bash
Failcounter=0
#python3 install
while [ "$Failcounter" -lt "5" ]; do
	sudo apt install python3-venv -y
		if [ $? -ne "0" ]; then
		((Failcounter++)) 
		else echo "successfully installed python3"
		Failcounter=0
		break
		fi
done
if [ "$Failcounter" -eq "5" ]; then
	echo "failed to install python3"
	exit 1
fi
#docker install
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

#create and activate virtual environment
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
#install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "no requirements.txt found!"
    exit 1
fi

cd monitoring
sudo docker compose up -d
cd ..
./.venv/bin/fastapi dev main.py

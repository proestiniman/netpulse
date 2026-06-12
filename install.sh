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
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o/etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-com

#create and activate virtual environment
python3 -m venv .venv
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
fastapi dev main.py

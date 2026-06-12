#!/bin/bash
Failcounter=0
#Verzeichnisstruktur erstellen

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

cd .venv
python3 - m venv vvv
source vvv/bin/activate

for requirement in "{requirements[@]}"; do
	pip install "$requirement"
	if [ $? -ne "0" ]; then
	echo "failed to install $requirement"
	exit 1
	else echo "$requirement installed"
	fi
done

cd ..
cd monitoring
docker compose up -d
cd ..
fastapi dev main.py


exit
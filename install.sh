#!/bin/bash
Failcounter=0
#Verzeichnisstruktur erstellen

while [ "$Failcounter" -lt "5" ]; do
	mkdir -p "./netpulse"
		if [ $? -ne "0" ]; then
		((Failcounter++)) 
		else echo "successfully created directory netpulse"
		Failcounter=0
		break
		fi
done
if [ "$Failcounter" -eq "5" ]; then
	echo "failed to create directory netpulse"
	exit 1
fi

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

cd netpulse
python3 -m venv .venv
sudo apt install python3-pip -y
while [ "$Failcounter" -lt "5" ]; do
	cp main.py "./netpulse"
		if [ $? -ne "0" ]; then
		((Failcounter++)) 
		else echo "successfully copied main.py"
		Failcounter=0 
		break
		fi
done
if [ "$Failcounter" -eq "5" ]; then
	echo "failed to copy main.py"
	exit 1
fi

while [ "$Failcounter" -lt "5" ]; do
	cp monitoring "./netpulse"
		if [  $? -ne "0" ]; then
		((Failcounter++))
		else echo "successfully copied monitoring folder"
		Failcounter=0 
		break
		fi
done
if [ "$Failcounter" -eq "5" ]; then
	echo "failed to copy the monitoring folder"
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
cd netpulse
fastapi dev main.py


exit





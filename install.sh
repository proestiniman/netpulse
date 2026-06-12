#!/bin/bash
Failcounter=0
#Verzeichnisstruktur erstellen

while ["$Failcounter" -lt "5"]; do
	mkdir -p "$HOME/netpulse"
		if [ $? -ne 0 ]; then
		Failcounter+=1 
		else echo "successfully created directory netpulse"
		$Failcounter=0
		break
		fi
done
if [ "$Failcounter"=5 ]; then
	echo "failed to create directory netpulse"
	exit1
fi

while ["$Failcounter" -lt "5"]; do
	sudo apt install python3-venv
		if [ $? -ne 0 ]; then
		Failcounter+=1 
		else echo "successfully installed python3"
		$Failcounter=0
		break
		fi
done
if [ "$Failcounter"=5 ]; then
	echo "failed to install python3"
	exit 1
fi

cd netpulse
python3 -m venv .venv
sudo apt install python3-pip
while ["$Failcounter" -lt "5"]; do
	cp main.py "$HOME/netpulse"
		if [ $? -ne 0 ]; then
		Failcounter+=1 
		else echo "successfully copied main.py"
		$Failcounter=0 
		break
		fi
done
if [ "$Failcounter"=5 ]; then
	echo "failed to copy main.py"
	exit 1
fi

while ["$Failcounter" -lt "5"]; do
	cp monitoring "$HOME/netpulse"
		if [  $? -ne 0 ]; then
		Failcounter+=1
		else echo "successfully copied monitoring folder"
		$Failcounter=0 
		break
		fi
done
if [ "$Failcounter"=5 ]; then
	echo "failed to copy the monitoring folder"
	exit 1
fi

cd .venv
python3 - m venv vvv
source vvv/bin/activate

for k in {requirements.length}; do
	requirement=requirements[k]
	pip install requirement
	if [ $? -ne 0 ]; then
	echo "failed to install $requirement"
	exit 1
	else "$requirement installed"
	fi
done

cd ..
cd monitoring
docker compose up -d
cd ..
cd netpulse
fastapi dev main.py


exit





# TimerTesting

## Github
	git config --global user.email "luisalfperez@hotmail.com"
	git config --global user.name "LuisAlfPerez"
	git config --global credential.helper store

## Ubuntu consola
  	sudo apt update
    sudo apt upgrade
    sudo apt install nginx
  	sudo apt install gunicorn3
  	sudo apt install postgresql postgresql-contrib

  	sudo apt install net-tools
  	sudo apt install nginx
  	sudo apt install gunicorn3
	sudo apt install python3-pip
  	sudo apt install python3-venv
  	sudo apt install python3-dev libpq-dev #Puede ser necesaria en el venv
	sudo apt install build-essential libssl-dev libffi-dev python3-setuptools
	sudo apt-get install python3-opencv
	sudo apt install raspi-config
	sudo apt install setserial


## Python
 	***
	pip3 list
 	***
	cd
 	cd Timer
 	sudo -H pip3 install -r requirements.txt
	python3 -m venv venv
 	source venv/bin/activate
 	pip3 install -r requirements.txt

## Python Sensors

	sudo nano /etc/systemd/system/sensors.service

[Unit]
Description=Timer_Sensors
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/Trelainn/Timer/sensors.py

[Install]
WantedBy=multi-user.target


## Gunicorn3

	sudo nano /etc/systemd/system/app.service

[Unit]
Description=SeaMaze Server
After=network.target

[Service]
User=Trelainn
Group=www-data
WorkingDirectory=/home/Trelainn/Timer
Environment="PATH=/home/Trelainn/Timer/venv/bin"
Environment="HOST=localhost"
Environment="USER=postgress"
Environment="PASSWORD=8fnVZpx7i+RT?47"
Environment="DATABASE=seamaze"
ExecStart=/home/Trelainn/Timer/venv/bin/gunicorn --workers 3 --bind unix:app.sock -m 007 wsgi:app --error-logfile /home/Trelainn/Timer/log/gunicorn.log

[Install]
WantedBy=multi-user.target

	sudo systemctl start app
	sudo systemctl enable app
		Created symlink /etc/systemd/system/multi-user.target.wants/app.service → /etc/systemd/system/app.service.
	sudo systemctl status app

## Nginx
	sudo unlink /etc/nginx/sites-enabled/default
	sudo unlink /etc/nginx/sites-available/default
	
	sudo nano /etc/nginx/sites-enabled/app

server {
	listen 8080;

	location / {
		proxy_pass http://unix:/home/Trelainn/Timer/app.sock;
		proxy_set_header HOST $host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
}

	sudo ln -s /etc/nginx/sites-enabled/app /etc/nginx/sites-available/
	sudo nginx -t
		nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
		nginx: configuration file /etc/nginx/nginx.conf test is successful
	sudo ufw allow 'Nginx Full'
	sudo chmod 755 /home/Trelainn
	sudo ufw disable
	sudo systemctl restart nginx
	
## Postgres
 	sudo -u postgres psql template1;
	 	template1=# ALTER USER POSTGRES WITH ENCRYPTED PASSWORD '8fnVZpx7i+RT?47';
		ALTER ROLE
		template1=# create database seamaze;
		CREATE DATABASE
		template1=# exit;
	sudo systemctl restart postgresql.service
	sudo -u postgres psql seamaze;
***
Añadir database_setup.txt	
********************

## Python Start-Up Config
	*** To test ***
	sh launcher.sh
	***************
	chmod 755 launcher.sh
	mkdir logs
	sudo crontab -e
	"Choose 1-3 [1]:" 1
		@reboot sh /home/seabob/seabob/launcher.sh >/home/seabob/seabob/logs/cronlog 2>&1
	sudo reboot -n

## USB static ports
	*** Identify each port and rename in code (if needed) ***
	ls -la /dev/serial/by-path/
	
## Generate Requirements File
	pip3 freeze > requirements.txt
	
## Install Arduino in Ubuntu 22.04 LTS
	sudo apt autopurge arduino   *** if previously installed ***
	sudo add-apt-repository ppa:lyzardking/ubuntu-make
	sudo apt-get update
	sudo apt-get install ubuntu-make
	umake electronics arduino-legacy
	sudo usermod -a -G dialout seabob
	sudo reboot -n
	
## To allow multiple same model serials
	*** To check serial actions ***
	dmesg | grep tty
	*** To see current detected serials ***
	ls -l /dev/serial*
	setserial -g /dev/tty*
	sudo usermod -a -G dialout seabob
	sudo nano /usr/lib/udev/rules.d/85-brltty.rules
	*** comentar #: ***
	# ENV{PRODUCT}=="1a86/7523/*",ENV{BRLTTY_BRAILLE_DRIVER}="bm",GOTO="brltty_usb_run"
	sudo reboot -n
	
## Camera Config
	sudo raspi-config
	-> Interface Options
	-> Legacy Camera -> Enable

## Hotspot auto
***
Crear red hotspot:
	SSID: Timer
	Contraseña: 123465789
*********
	nm-connection-editor 
	priority = 100 (Numero más alto mayor prioridad)
	sudo systemctl restart NetworkManager
README
Cointains the guide how to set the UDOO by scratch
1) install the UDOObuntu_neo_v2.0rc1.img in a sd card
2) modify the /etc/network/interfaces like suggested in daemons/etc/interfaces
3) place the sd card in the udoo neo, connect the udoo with an ethernet to you PC and to internet and power it on 
4) login to it with login: udooer, pass: udooer
5) install the following software, after sudo apt-get update. The sudo password is udooer
sudo apt-get install ntp python-matplotlib vim git
6) type git clone https://github.com/marinetech/Udoo.git
7) create a new user called themo_user with a searten password decided from the admin with no root privileges. To do that, type:
adduser themo_user
then follow the procedure and confirm
8) change the password of the root user (udooer) in order to have an higher level of security. Please, type:
sudo passwd udooer
<new password>
9) type:
sudo cp Udoo/daemons/etc/network/interfaces /etc/network/interfaces
sudo cp Udoo/daemons/etc/rc.local /etc/rc.local 
sudo cp Udoo/daemons/user/local/bin/* /usr/local/bin/.
sudo cp Udoo/daemons/user/local/sbin/* /usr/local/sbin/.
sudo cp -r Udoo/udoo/themosignal /usr/local/lib/python2.7/dist-packages/.
sudo cp -r Udoo/udoo2node/udoo2no_pkg /usr/local/lib/python2.7/dist-packages/.
sudo cp -r Udoo/udoo/script /home/themo_user/.
sudo mkdir /home/themo_user/files2upload
sudo mkdir /home/themo_user/files_uploaded
sudo chown -R themo_user /home/themo_user/script/
sudo chown -R themo_user /home/themo_user/f*

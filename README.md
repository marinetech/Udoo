README
Cointains the guide how to set the UDOO by scratch
1) install the UDOObuntu_neo_v2.0rc1.img in a sd card
2) modify the /etc/network/interfaces like suggested in daemons/etc/interfaces
3) place the sd card in the udoo neo, connect the udoo with an ethernet to you PC and to internet and power it on 
4) login to it with login: udooer, pass: udooer
5) install the following software, after sudo apt-get update. The sudo password is udooer. This requires a while.
sudo apt-get install expect ntp rsync python-matplotlib vim git daemontools daemontools-run python-scipy p7zip-full sox vsftpd
pip install scipy
6) type 
git clone https://github.com/marinetech/Udoo.git
if doesn't work due to server certificates, please type 
export GIT_SSL_NO_VERIFY=1 and retry
7) create a new user called themo_user with a searten password decided from the admin with no root privileges. To do that, type:
adduser themo_user
then follow the procedure and confirm
8) change the password of the root user (udooer) in order to have an higher level of security. Please, type:
sudo passwd udooer
<new password>
9) type:
sudo cp Udoo/daemons/etc/network/interfaces /etc/network/interfaces
sudo cp Udoo/daemons/etc/rc.local /etc/rc.local 
sudo cp Udoo/daemons/usr/local/bin/* /usr/local/bin/.
sudo cp Udoo/daemons/usr/local/sbin/* /usr/local/sbin/.
sudo cp -r Udoo/udoo/themosignal /usr/local/lib/python2.7/dist-packages/.
sudo cp -r Udoo/udoo2node/ud2no_pkg /usr/local/lib/python2.7/dist-packages/.
sudo cp -r Udoo/udoo/script /home/themo_user/.
sudo cp -r Udoo/daemons/etc/service/* /etc/service/.
sudo chmod -R 1755 /etc/service
sudo mkdir /home/themo_user/files2upload
sudo mkdir /home/themo_user/files_uploaded
sudo chown -R themo_user /home/themo_user/script/
sudo chown -R themo_user /home/themo_user/f*

10) if you want to use a dhcp, configure /etc/network/interfaces accordingly, and change the host name to avoid multiple hosts with the same ip:
change the host name in /etc/hostname and the frist two lines of /etc/hosts accordingly
11) modify /etc/vsftpd.conf and set "write_enable=YES"
12) login as themo_user
13) cd script
14) chmod +x *.sh
15) in YOUR PC open an tcp server at the port 44444 (typing nc -l 44444)
16) in the UDOO run one of the scripts .sh with ./<script_name>.sh
17) reboot it to make the daemons running and change hostname permanently

NOTE: if you have some ssh key problem (offending, scp problems, ..),please type (in all user, root as well):
ssh-keygen -R

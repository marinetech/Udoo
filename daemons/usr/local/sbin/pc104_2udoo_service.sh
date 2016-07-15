#/bin/bash
# Copyright (c) 2016 Regents of the SIGNET lab, University of Padova.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University of Padova (SIGNET lab) nor the 
#    names of its contributors may be used to endorse or promote products 
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED 
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Author: Filippo Campagnaro
# email: campagn1@dei.unipd.it
# place it in /usr/local/sbin/pc104_2udoo_service.sh
# Breif description: daemon handling tcp messages incoming from pc104

# UDOO DAEMON
COMMON_LOG=/var/log/check_status
port=55555
rm $COMMON_LOG/check_off.log > /dev/null
STATUS="ON"
while true
do
	pc104_message=$(echo $STATUS | nc -l -p $port)
	echo $pc104_message

	#if getStatus
	getStatus_flag=$(echo $pc104_message | grep getStatus)
	if [ -n "$getStatus_flag" ]
	then
		echo $STATUS | nc -l -p $port
	fi

	# set date if date
	pc104_date=$(echo $pc104_message | grep set_date | awk -F "," '{print $2}')
	if [ -n "$pc104_date" ]
	then
		sudo date +%s.%N -s @$pc104_date
	fi

  # upload
	upload_flag=$(echo $pc104_message | grep upload)
	if [ -n "$upload_flag" ]
	then
		upload_all.sh
		sleep 1
	fi

	# remove all
	erase_flag=$(echo $pc104_message | grep remove_all)
	if [ -n "$erase_flag" ]
	then
		remove_all_sent.sh
		sleep 1
	fi

	upload_again_flag=$(echo $pc104_message | grep retransmit)
	if [ -n "$upload_again_flag" ]
        then
		mv /home/themo_user/files_uploaded/* /home/themo_user/files2upload/.
		sleep 1
                upload_all.sh
                sleep 1
        fi

	#run bash script

	run_file=$(echo $pc104_message | grep run_file | awk -F "," '{print $2}')
	if [ -n "$run_file" ]
	then
	#TODO: TEST THIS
		usr=$(echo $run_file | grep / | awk -F "/" '{print $1}')
		chmod +x /home/$run_file
		sudo -u $usr /home/$run_file &
		sleep 1
	fi

	# poweroff procedure if poweroff
	poweroff_flag=$(echo $pc104_message | grep poweroff)
	if [ -n "$poweroff_flag" ]
	then
		# poweroff_procedure
		echo "poweroff" > $COMMON_LOG/check_off.log
		STATUS="poweroff"
		sleep 10
		sudo poweroff
	fi
done

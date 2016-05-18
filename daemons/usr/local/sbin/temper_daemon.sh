#!/bin/bash

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
# place it in /usr/local/sbin/temper_daemon.sh
# Breif description: daemon taking care about checking the CPU temperature 
# preventing CPU dameges


# procedure to poweroff the UDOO preventing cpu damages
LOG_PATH="/var/log/temper"
COMMON_LOG="/var/log/check_status"
function turn_off {
	echo "Exiting and powering it off..." >> $LOG_PATH/temp_daemon.log
	# procedure to trigger off the ongoing processes e.g. set a config file to turn off the py scripts
	echo "poweroff" > $COMMON_LOG/check_off.log
	sleep 10
	sudo poweroff
}

# procedure killing the UDOO higest load process 
# preventing cpu damages
function kill_hi_lo_proc {
	
	TROUBLEMAKERS="python ns"
	
	sleep 1 # wait a few seconds (just as a precaution)

	TOPPROCESS=$(top -b -n 1 | sed 1,6d | sed -n 2p)
	TOPPID=$(echo "$TOPPROCESS" | awk '{print $1}')
	TOPNAME=$(echo "$TOPPROCESS" | awk '{print $12}')

	if [[ "$TROUBLEMAKERS" == *"$TOPNAME"* ]]
	then
      		echo "Cause of high CPU load: "$TOPNAME" ("$TOPPID")" >> $LOG_PATH/temp_daemon.log
      		echo "In troublemaker list. Killing..." >> $LOG_PATH/temp_daemon.log
      		# procedure to trigger off the process e.g. set a config file to turn off the py scripts
		echo "kill $TOPPID" >> $COMMON_LOG/check_kills.log
		sleep 50
	     	kill -9 $TOPPID
	else
      		echo "Cause of high CPU load: "$TOPNAME" ("$TOPPID")" >> $LOG_PATH/temp_daemon.log
      		turn_off
      		exit 1
	fi
	exit 0
}


#guard temperature in millicelsius
GUARD=7500
HARD_GUARD=4000
# either passive or critical cpu temperature, depending on the system
REF_TEMP=$(cat /sys/class/thermal/thermal_zone0/trip_point_0_temp)

if [ -z $REF_TEMP ]
then 
	REF_TEMP=95000 
fi


rm $COMMON_LOG/check_off.log $COMMON_LOG/check_kills.log

# passive temp - guard before to start killing processes
# to cool the CPU
CHECK_TEMP=$(expr $REF_TEMP - $GUARD)
# passive temp - hard_guard before to power-off the processor
# to cool the CPU and prevent damage
CHECK_HARD_TEMP=$(expr $(cat /sys/class/thermal/thermal_zone0/trip_point_0_temp) - $HARD_GUARD)


echo "Temperature daemon starting..." > $LOG_PATH/temp_daemon.log

TEMP_STATUS="OK"
while true 
do
	sleep 5
	TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
	if [[ "$TEMP" -ge "$CHECK_HARD_TEMP" ]]
	then
		TEMP_STATUS="BAD"
		echo "temp_status=$TEMP_STATUS" > $LOG_PATH/temp_daemon_status.log
		sleep 1
		turn_off
	elif [[ "$TEMP" -ge "$CHECK_TEMP" ]]
	then
		TEMP_STATUS="BAD"
		echo "temp_status=$TEMP_STATUS" > $LOG_PATH/temp_daemon_status.log
		kill_hi_lo_proc			
	else
		TEMP_STATUS="OK"
		echo "temp_status=$TEMP_STATUS" > $LOG_PATH/temp_daemon_status.log
	fi
done


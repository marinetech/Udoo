UPLOAD_FOLDER=/home/themo_user/files2upload
CURRENT_FOLDER=/home/themo_user/script
cd $CURRENT_FOLDER
LOG_NAME=transmitter$(/bin/date +%s)_log.out
SCRIPT_NAME=transmit.py
/bin/date >> $CURRENT_FOLDER/$LOG_NAME 2>&1
/bin/sleep 1
/usr/bin/python $CURRENT_FOLDER/$SCRIPT_NAME >> $CURRENT_FOLDER/$LOG_NAME 2>&1
/bin/sleep 2
cp $CURRENT_FOLDER/$LOG_NAME $UPLOAD_FOLDER/$LOG_NAME
/bin/sleep 1
rm $CURRENT_FOLDER/$LOG_NAME
/usr/local/bin/upload_spec_file.tcl $LOG_NAME themo_user
#upload_all.sh


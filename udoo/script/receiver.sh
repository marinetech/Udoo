LOG_FOLDER=/home/themo_user/files2upload
CURRENT_FOLDER=/home/themo_user/script
cd $CURRENT_FOLDER
LOG_NAME=receiver$(/bin/date +%s)_log.out
SCRIPT_NAME=receiver.py
/bin/date >> $CURRENT_FOLDER/$LOG_NAME
/usr/bin/python $CURRENT_FOLDER/$SCRIPT_NAME $OUTPUT_FOLDER >> $CURRENT_FOLDER/$LOG_NAME 2>&1
/bin/sleep 2
cp $CURRENT_FOLDER/$LOG_NAME $LOG_FOLDER/.
cp -r $CURRENT_FOLDER/*stream* $LOG_FOLDER/.
/bin/sleep 1
rm $CURRENT_FOLDER/$LOG_NAME
rm -r $CURRENT_FOLDER/*stream*
upload_all.sh


LOG_FOLDER=~/files2upload
LOG_NAME=receiver_log.out
/bin/date >> $LOG_FOLDER$LOG_NAME
python receiver.py >> $LOG_FOLDER/$LOG_NAME
upload_spec_file.tcl $LOG_NAME
sleep 2
cp *stream* $LOG_FOLDER/.
rm -r *stream*
upload_all.sh
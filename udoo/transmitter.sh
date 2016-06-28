LOG_FOLDER=~/files2upload/
LOG_NAME=tranmsitter_log.out
/bin/date >> $LOG_FOLDER$LOG_NAME
python transmit.py >> $LOG_FOLDER$LOG_NAME
upload_spec_file.tcl $LOG_NAME
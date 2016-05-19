# UDOO TO NODE TCP interface
ud2n_pkg is a package that has to be placed in /usr/local/lib/python2.7/dist-packages/ud2n_pkg (need route permission)
This provide the tools you need to operate the submerged node.
To see an example, please read the examples in the application folder
FC:todo: add something more (where to find the documentation, etc..)


# List of commands
0) 	OK : the confirm message.

1) 	send_file,name,size: the send_file message(name of the file, size of the file in bytes)

2) 	get_file,name,delete: the get_file message requires a file to the node (name of the file required, delete flag, if 1 erase it after sending, otherwise if 0 not). The node answer with OK, then with the send_file command before sending the file.

3)	get_data,delete: the get_data message: get whatever data has been recorded. (delete flag, if 1 erase it after sending, if 0 not ). Before each file the node sends the corresponding send_file command.

4)	set_power,cum_id,s_l: the set_power message(cum_id cumulative list (NOTE1) of the projector IDs where to play the file, s_l source level output power)

5)	play_audio,name,cum_id,starting_time,n_rip: the play_audio message (name of the file that has to be played, cum_id cumulative list (NOTE1) of the projector IDs where to play the file, starting_time HH:MM:SS when to start playing the file, n_rip number of time it has to be consecutively played, delete flag, if 1 erase it after playing, if 0 not, force_flag if trying to transmit while recording:
            0 (default) not allowed (error feedback)
            1 (force) stop recording and start transmitting
            2 (both) do both the operations together
		)

6)	record_data,name,sens_t,cum_id,starting_time,duration,force_flag: the record_data message (name of the file where to record the audio, sens_t of the sensors that have to record the data:
            1 --> hydrophone,
            2 --> camera
            3 --> others,
    cum_id cumulative (NOTE1) list of the sensors IDs used to record the audio, starting_time HH:MM:SS when to start recording the file, duration HH:MM:SS of duration of the recording, force_flag if trying to record while transmitting:
            0 (default) not allowed (error feedback)
            1 (force) stop transmitting and start recording
            2 (both) do both the operations together
    )

7) 	get_rt_data,sens_t,cum_id,starting_time,duration,chunck_duration,delete: the get_rt_data message ask the node to record and send the data in real time, divided them in chunck of fixed time length. The node before to send each chunck, sends an IDENTIFIER (e.g. UNIX EPOCH). (cum_id cumulative list of the senseors IDs used to record the audio, sens_t of the sensors that have to record the data:
            1 --> hydrophone,
            2 --> camera
            3 --> others,
    starting_time HH:MM:SS when to start recording the file, duration HH:MM:SS of duration of the recording, chunck_duration chunk duration [seconds], delete flag, if 1 erase it after sending, otherwise if 0 not, force_flag if trying to record while transmitting:
                0 (default) not allowed (error feedback)
                1 (force) stop transmitting and start recording
                2 (both) do both the operations together

8)	get_status the get_status message to obtain the node status.

9)	reset_proj,cum_id,force_flag: the reset_proj message. This message will reset the projectors (cum_id cumulative (NOTE1) list of the projector IDs that has to be resetted, force_flag if 1 reset also if pending operations, if 0 not )

10)	reset_sen,sens_t,cum_id,force_flag: the reset_sen message. This message will reset the sensors(sens_t of the sensors that have to record the data:
            1 --> hydrophone,
            2 --> camera
            3 --> others,
    cum_id cumulative list of the projector IDs that has to be resetted, force_flag if 1 reset also if pending operations, if 0 not)

11)	reset_all,force_flag: the reset_all message. This message will reset the node (force_flag if 1 reset also if pending operations, if 0 not)

12) delete_all_rec,sens_t: the delete_all_rec message. This message delete the recorded (sens_t of the sensors that have to record the data:
            o --> all,
            1 --> hydrophone,
            2 --> camera
            3 --> others)

13)   delete_all_sent: the delete_all_rec message. This message delete the files sent to the node

#Notes
NOTE0: At each command the node answers eitherwith OK or error,# to confirm the command has been received and processed correctly or signal an error.  The results of the command, if any, will be sent after this.

NOTE1: we should find a way with proj_id and sensor_id to set the list of devices to employ
SOLUTION: the same of linux chmod → group the devices in bit fashion:
0 ->   0: none
1 ->   1: dev1
2 ->  10: dev 2
3 ->  11: dev 1 and 2
4 -> 100: dev 3
and so on

NOTE2: the recording sensors are either hydrophones, cameras or other sensors. To identify them we use an ID:
0: all
1: hydrophone
2: cameras
3: others

NOTE3: by default either sending or recording. Therefore the flag in the command 2, 4 and 13 can be:
0: default: if trying to transmit while recording, not allowed (error feedback)
1: force: if trying to transmit while recording, stop recording and transmit
2: both: if trying to transmit while recording, do it together

List of the messages:

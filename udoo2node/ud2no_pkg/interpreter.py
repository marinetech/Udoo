import math
class Interpreter(object):
    """Class to build the command string for the modem"""
    SEPARATOR = ","
    END_COMMAND = ""
    START_COMMAND = ""
    
    def __init__(self):
        """
        Constructor, initialize the iterpreter. 
        @param self pointer to the class object
        """
        self.debug = 1
    
    def setDebug(self,debug):
        """
        Set the debug mode. 
        @param self pointer to the class object
        @param debug is the debug mode. O-->OFF, 1-->ON
        """
        self.debug = debug
    
    def s(self):
        """
        Shortcut to return the separator. 
        @param self pointer to the class object
        @return the separator
        """
        return Interpreter.SEPARATOR

    def end(self):
        """
        Shortcut to return the end command separator. 
        @param self pointer to the class object
        @return the separator
        """
        return Interpreter.END_COMMAND

    def start(self):
        """
        Shortcut to return the start command separator. 
        @param self pointer to the class object
        @return the separator
        """
        return Interpreter.START_COMMAND

    def buildConfirm(self):
        """
        Build the confirm message. 
        @param self pointer to the class object
        @return the message
        """
        msg = self.start() + "OK" + self.end()
        return msg

    def buildSendFile(self, name, size):
        """
        Build the send_file message. 
        @param self pointer to the class object
        @param name of the file
        @param size of the file in bytes
        @return the message
        """
        msg = self.start() + "send_file" + self.s() + str(name) + self.s() + \
            str(size) + self.end()
        if self.debug :
            print msg
        return msg
        
    def buildGetFile(self, name, delete = 1):
        """
        Build the get_file message. 
        @param self pointer to the class object
        @param name of the file required
        @param delete flag, if 1 erase it after sending, otherwise if 0 not 
        @return the message
        """
        msg = self.start() + "get_file" + self.s() + str(name)+ self.s() + \
            str(delete) + self.end()
        if self.debug :
            print msg
        return msg
      
    def buildGetData(self, delete = 1):
        """
        Build the get_data message: get whatever data has been recorded. 
        @param self pointer to the class object
        @param delete flag, if 1 erase it after sending, if 0 not 
        @return the message
        """
        msg = self.start() + "get_data" + self.s() + str(delete) + self.end()
        if self.debug :
            print msg
        return msg      
 
    def buildSetPower(self, ID_list, s_l):
        """
        Build the set_power message. 
        @param self pointer to the class object
        @param ID_list list of the projector IDs where to play the file
        @param s_l source level output power
        @return the message
        """
        cum_id = self.getCumulativeID(ID_list)
        msg = self.start() + "set_power" + self.s() + str(cum_id) + self.s() + str(s_l) \
            + self.end()
        if self.debug :
            print msg
        return msg
        
    def buildPlay(self, name, ID_list, starting_time, n_rip = 1, \
                    delete = 1, force_flag = 0):
        """
        Build the play_audio message. 
        @param self pointer to the class object
        @param name of the file that has to be played
        @param ID_list list of the projector IDs where to play the file
        @param starting_time HH:MM:SS when to start playing the file
        @param n_rip number of time it has to be consecutively played
        @param delete flag, if 1 erase it after playing, if 0 not 
        @param force_flag if trying to transmit while recording:
            0 (default) not allowed (error feedback)
            1 (force) stop recording and start transmitting
            2 (both) do both the operations together
        @return the message
        """
        cum_id = self.getCumulativeID(ID_list)
        msg = self.start() + "play_audio" + self.s() + str(name) + self.s() + str(cum_id) + \
            self.s() + str(starting_time) +self.s() + str(n_rip) + self.s() + \
            str(delete) + self.s() + str(force_flag) + self.end()
        if self.debug :
            print msg
        return msg
        
    def buildRecordData(self, name, sens_t, ID_list, starting_time, duration, \
                        force_flag = 0):
        """
        Build the record_data message. 
        @param self pointer to the class object
        @param name of the file where to record the audio
        @param sens_t of the sensors that have to record the data:
            1 --> hydrophone, 
            2 --> camera 
            3 --> others
        @param ID_list list of the sensors IDs used to record the audio
        @param starting_time HH:MM:SS when to start recording the file
        @param duration HH:MM:SS of duration of the recording
        @param force_flag if trying to record while transmitting:
            0 (default) not allowed (error feedback)
            1 (force) stop transmitting and start recording
            2 (both) do both the operations together
        @return the message
        """
        cum_id = self.getCumulativeID(ID_list)
        msg = self.start() + "record_data" + self.s() + str(name) + self.s() + \
            str(sens_t) + self.s() + str(cum_id) + self.s() + \
            str(starting_time) + self.s() + str(duration) + self.s() + \
            str(force_flag) + self.end()
        if self.debug :
            print msg
        return msg

    def buildGetRTData(self, sens_t, ID_list, starting_time, duration, chunck_duration, \
        delete = 1, force_flag = 0):
        """
        Build the get_rt_data message. 
        @param self pointer to the class object
        @param ID_list list of the sensors IDs used to record the audio
        @param sens_t of the sensors that have to record the data:
            1 --> hydrophone, 
            2 --> camera 
            3 --> others
        @param starting_time HH:MM:SS when to start recording the file
        @param duration HH:MM:SS of duration of the recording
        @param chunck_duration chunk duration, in seconds
        @param delete flag, if 1 erase it after sending, otherwise if 0 not 
        @param force_flag if trying to record while transmitting:
                0 (default) not allowed (error feedback)
                1 (force) stop transmitting and start recording
                2 (both) do both the operations together
        @return the message
        """
        cum_id = self.getCumulativeID(ID_list)
        msg = self.start() + "get_rt_data" + self.s() + str(sens_t) + self.s() + \
            str(cum_id) + self.s() + str(starting_time) + self.s() + str(duration)+ \
            self.s() + str(chunck_duration)+ self.s() + str(delete) + self.end()
        if self.debug :
            print msg
        return msg
        
    def buildGetStatus(self):
        """
        Build the get_status message. 
        @param self pointer to the class object
        @return the message
        """
        msg = self.start() + "get_status" + self.end()
        if self.debug :
            print msg
        return msg
        
    def buildResetProj(self, ID_list, force_flag = 0):
        """
        Build the reset_proj message. This message will reset the projectors 
        @param self pointer to the class object
        @param ID_list list of the projector IDs that has to be resetted
        @param force_flag if 1 reset also if pending operations, if 0 not 
        @return the message
        """
        cum_id = self.getCumulativeID(ID_list)
        msg = self.start() + "reset_proj" + self.s() + str(cum_id) + self.s() + \
            str(force_flag) + self.end()
        if self.debug :
            print msg
        return msg
    
    def buildResetSensor(self, sens_t, ID_list, force_flag = 0):
        """
        Build the reset_sen message. This message will reset the sensors 
        @param self pointer to the class object
        @param sens_t of the sensors that have to record the data:
            1 --> hydrophone, 
            2 --> camera 
            3 --> others
        @param ID_list list of the projector IDs that has to be resetted
        @param force_flag if 1 reset also if pending operations, if 0 not 
        @return the message
        """
        cum_id = self.getCumulativeID(ID_list)
        msg = self.start() + "reset_sen" + self.s() + str(sens_t) + self.s() \
            + str(cum_id) + self.s() + str(force_flag) + self.end()
        if self.debug :
            print msg
        return msg
    
    def buildResetAll(self, force_flag = 0):
        """
        Build the reset_all message. This message will reset the node 
        @param self pointer to the class object
        @param force_flag if 1 reset also if pending operations, if 0 not 
        @return the message
        """
        msg = self.start() + "reset_all" + self.s() + str(force_flag) + self.end()
        if self.debug :
            print msg
        return msg
        
    def buildDeleteAllRec(self, sens_t):
        """
        Build the delete_all_rec message. This message delete the recorded 
        files at the node 
        @param self pointer to the class object
        @param sens_t of the sensors that have to record the data:
            o --> all,
            1 --> hydrophone, 
            2 --> camera 
            3 --> others
        @return the message
        """
        msg = "delete_all_rec" + self.s() + str(sens_t)
        if self.debug :
            print msg
        return msg
        
    def buildDeleteAllSent(self):
        """
        Build the delete_all_rec message. This message delete the files sent
        by the node 
        @param self pointer to the class object
        @return the message
        """
        msg = self.start() + "delete_all_sent" + self.end()
        if self.debug :
            print msg
        return msg
    
    def getCumulativeID(self,ID_list):
        """
        From list of IDs to a global ID in binary rappresentation
        @param self pointer to the class object
        @return the cumulative id
        """
        cum_id = 0
        for id_i in ID_list:
            if id_i <= 0:
                raise ValueError("each ID must be > 0")
            cum_id += pow(2,id_i-1)
        return cum_id
        
    def getIDlist(self,cum_id):
        """
        From list of IDs to a global ID in binary rappresentation
        @param self pointer to the class object
        @return the cumulative id
        """
        ID_list = []
        while (cum_id > 0):
            ID = int(math.log(cum_id,2))
            cum_id -= pow(2,ID)
            ID_list.insert(0,ID+1)
        return ID_list



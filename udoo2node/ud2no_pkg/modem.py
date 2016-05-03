import socket
import thread
import sys
import binascii
import os
from time import sleep
from interpreter import Interpreter
from connector import Connector

class Modem(object):
    """Class modem to control the node via TCP"""
    
    class Status:
        """Internal class where the status types are defined"""
        IDLE, BUSY2REQ, BUSY2DATA, BUSY2RECV, BUSY2REQ2DATA, KILL = range(6)
    
    class ErrorDict:
        """Internal class to map the error types to their error message"""
        NONE, SYNT_ERR, FILE_NOT_FOUND, TX_WHILE_RX, RX_WHILE_TX = \
        range(5)
        error_dict = {
            NONE : 'none',
            SYNT_ERR : 'command syntax error',
            FILE_NOT_FOUND : 'file not found error',
            TX_WHILE_RX : 'you attempt to transmit while receiving, if \
                you really want, set the force flag to 1',
            RX_WHILE_TX : 'you attempt to receive while transmitting if \
                you really want set the force flag to 1'
         }
          
    def __init__(self, ip, port, automatic = True, control_buf_size = 32, data_buf_size = 128, \
        m_to = 0.01, socket_to = 0.005):
        """
        Constructor, initialize the modem and the connector. Connect the
        modem to the submerged node
        @param self pointer to the class object 
        @param ip string cointaining the IP address of the TCP server 
        @param port string with the port of the TCP server socket 
        @param control_buf_size: int with the control buffer size, in bytes 
        @param data_buf_size: int with the data buffer size, in bytes
        @param m_to: float value time out of the cycle, in [s]
        @param socket_to: time out of the socket checking operation, [s]
        """
        self.conn = Connector(ip, port, control_buf_size, data_buf_size, socket_to)
        self.conn.connect()
        self.m_to = m_to
        self.status = Modem.Status.IDLE
        self.automatic = automatic
        self.interpreter = Interpreter()
        self.mainPID = os.getpid()
        if automatic:
            thread.start_new_thread(self.run,())
        
    def run(self):
        """
        Run cycle, checks if data available
        @param self pointer to the class object
        """
        threadPID = os.getpid()
        index = 0
        while True:
            index += 1
            if ((index * self.m_to) > 1):
                self.check4kill(threadPID)
                index = 1
            if(self.status == Modem.Status.IDLE):
                r, e = self.conn.dataAvailable()
                if(e):
                    break
                if(r):
                    rx = self.recvCommand()
                    print "Rx ",rx
                    if (len(rx) == 0):
                        break
            elif(self.status == Modem.Status.KILL):
                break
            sleep(self.m_to)
        self.close()
        print >>sys.stderr, 'Closing'

    def check4kill(self,threadPID = -1):
        """
        Close the connection from the modem to the submerged node
        @param self pointer to the class object
        """
        #TODO: check in the kill log if my main or my thred PID are there.
        #      In case True, kill all. /var/log/check_status/check_kills.log
        # kill $TOPPID
        # /var/log/check_status/check_off.log
        off_log = "/var/log/check_status/check_off.log"
        kill_log = "/var/log/check_status/check_kills.log"
        try:
            f = open (off_log, "r") 
            l = f.read(self.conn.data_buf_size)
            while (l or self.status != Modem.Status.KILL):
                if l == "poweroff":
                    self.status = Modem.Status.KILL
                l = f.read(self.conn.data_buf_size)
            f.close()
        except IOError:
            print off_log + " not found"
        try:
            f = open (kill_log, "r") 
            l = f.read(self.conn.data_buf_size)
            while (l or self.status != Modem.Status.KILL):
                if (l == ("kill " + str(threadPID)) or \
                    l == ("kill " + str(self.mainPID))):
                    self.status = Modem.Status.KILL
                l = f.read(self.conn.data_buf_size)
            f.close()
        except IOError:
            print kill_log + " not found"
        
    def close(self):
        """
        Close the connection from the modem to the submerged node
        @param self pointer to the class object
        """
        self.conn.close()

    def recvData(self):
        """
        Receive the data as they are from the node, it is a blocking 
        function. To check if data has to be received, query the 
        self.conn.dataAvailable() function
        @param self pointer to the class object
        @return the incoming string from the TCP connection
        """
        prec_state = self.status
        self.status = Modem.Status.BUSY2RECV
        data = self.conn.recvData()
        self.status = prec_state
        self.checkConnection(data)
        return data

    def recvCommand(self):
        """
        Receive and process a command from the node
        @param self pointer to the class object
        @return the incoming string from the TCP connection
        """
        prec_state = self.status
        self.status = Modem.Status.BUSY2RECV
        command = self.conn.recvCommand()
        self.status = prec_state
        self.checkConnection(command)
        self.parseCommand(command.rstrip('\n'))
        return command

    def send(self, msg):
        """
        Send a message to the submerged node
        @param self pointer to the class object
        @param msg message that has to be conveyed to the submerged node
        """
        sleep(self.m_to)
        self.conn.send(msg)

    def sendDataFile(self, file_path):
        """
        Send a file to the submerged node
        @param self pointer to the class object
        @param file_path path of the file that has to be sent
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem sendDataFile unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        self.send(self.interpreter.buildSendFile(name,size))
        #sleep(self.m_to/2) #to give the rx the time to parse the command
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
        self.status = Modem.Status.BUSY2DATA
        f = open (file_path, "rb") 
        l = f.read(self.conn.data_buf_size)
        while (l):
            self.conn.send(l)
            l = f.read(self.conn.data_buf_size)
        f.close()
        self.status = Modem.Status.IDLE
       
    def reqHydData(self, file_name, delete_flag = 1):
        """
        Require a file from the submerged node
        @param self pointer to the class object
        @param file_name name of the required file
        @param delete_flag, if 1 erase it after sending, if 0 not
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem reqHydData unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildGetHydData(file_name, delete_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
       
    def reqAllHydData(self, delete_flag = 1):
        """
        Require all the data from the submerged node
        @param self pointer to the class object
        @param delete_flag, if 1 erase it after sending, if 0 not
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem reqAllHydData unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildGetData(delete_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
    
    def reqRTData(self, ID_list, starting_time, duration, \
        chunck_duration = 1, delete = 1, force_flag = 0):
        """
        Require the data real time from the submerged node.
        @param self pointer to the class object
        @param ID_list list of the projector IDs used to record the audio
        @param starting_time HH:MM:SS when to start recording the file
        @param duration HH:MM:SS of duration of the recording
        @param chunck_duration chunk duration, in seconds
        @param delete flag, if 1 erase it after sending, otherwise if 0 not 
        @param force_flag if trying to record while transmitting:
            0 (default) not allowed (error feedback)
            1 (force) stop transmitting and start recording
            2 (both) do both the operations together
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem reqRTData unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildGetRTHydro(ID_list, starting_time, \
            duration, chunck_duration, delete , force_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()

    def setPower(self, ID_list, s_l):
        """
        Set the projector power. 
        @param self pointer to the class object
        @param ID_list list of the projector IDs where to play the file
        @param s_l source level output power
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem setPower unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildSetPower(ID_list, s_l))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
        
    def playProj(self, name, ID_list, starting_time, n_rip = 1, \
                    delete = 1, force_flag = 0):
        """
        Transmit the file with the projector. 
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
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem playProj unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildPlay(name, ID_list, starting_time, \
            n_rip, delete, force_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
        
    def recordAudio(self, name, ID_list, starting_time, duration, \
                        force_flag = 0):
        """
        record via hydrophones. 
        @param self pointer to the class object
        @param name of the file where to record the audio
        @param ID_list list of the projector IDs used to record the audio
        @param starting_time HH:MM:SS when to start recording the file
        @param duration HH:MM:SS of duration of the recording
        @param force_flag if trying to record while transmitting:
            0 (default) not allowed (error feedback)
            1 (force) stop transmitting and start recording
            2 (both) do both the operations together
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem recordAudio unexpected status:\
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildRecordAudio(name, ID_list, \
            starting_time, duration, force_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()

    def getNodeStatus(self):
        """
        Get the submerged node status. 
        @param self pointer to the class object
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem getNodeStatus unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildGetStatus())
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            res = self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
        return res
        
    def resetProj(self, ID_list, force_flag = 0):
        """
        Reset the projectors 
        @param self pointer to the class object
        @param ID_list list of the projector IDs that has to be resetted
        @param force_flag if 1 reset also if pending operations, if 0 not 
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem resetProj unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildResetProj(ID_list, force_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
    
    def resetHydr(self, ID_list, force_flag = 0):
        """
        Reset the hydrophones 
        @param self pointer to the class object
        @param ID_list list of the projector IDs that has to be resetted
        @param force_flag if 1 reset also if pending operations, if 0 not 
        @return the message
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem resetHydr unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildResetHydr(ID_list, force_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
    
    def resetAll(self, force_flag = 0):
        """
        Build the reset_all message. This message will reset the node 
        @param self pointer to the class object
        @param force_flag if 1 reset also if pending operations, if 0 not 
        @return the message
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem resetAll unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildResetAll(force_flag))
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
        
    def deleteAllRec(self):
        """
        Delete the recorded files from the node 
        @param self pointer to the class object
        @return the message
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem deleteAllRec unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildDeleteAllRec())
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()
        
    def deleteAllSent(self):
        """
        Delete the files sent by the node 
        @param self pointer to the class object
        @return the message
        """
        if self.status != Modem.Status.IDLE:
            raise ValueError("Modem deleteAllSent unexpected status: \
                " + str(self.status))
        self.status = Modem.Status.BUSY2REQ
        self.send(self.interpreter.buildDeleteAllSent())
        while self.status != Modem.Status.IDLE and self.status != Modem.Status.KILL:
            self.recvCommand()
        if self.status == Modem.Status.KILL:
            return self.close()

    def recvDataFile(self, file_name, length_f, confirm_flag):
        """
        Require all the data from the submerged node
        @param self pointer to the class object
        @param file_name name of the required file
        @param length_f of the file, in bytes
        @paran confirm_flag True if confirm needed. When stream is false
        """
        if self.status == Modem.Status.IDLE:
            self.status = Modem.Status.BUSY2DATA
        elif self.status == Modem.Status.BUSY2REQ:
            self.status = Modem.Status.BUSY2REQ2DATA
        else:
            raise ValueError("Modem recvDataFile unexpected status: \
                " + str(self.status))
        if(confirm_flag):
            self.send(self.interpreter.buildConfirm())
        self.status = Modem.Status.BUSY2DATA
        f = open(file_name,'wb') #open in binary
        n_recv = 0;
        print "recvFile", file_name, length_f
        while (n_recv < length_f or self.status != Modem.Status.KILL):
            if self.status == Modem.Status.KILL:
                f.close()
                return self.close()
            l = self.recvData()
            if(n_recv + len(l) < length_f):
                f.write(l)
            else:
                f.write(l[0:length_f - n_recv])
            n_recv += len(l)
        f.close()
        if self.status == Modem.Status.BUSY2DATA:
            self.status = Modem.Status.IDLE
        elif self.status == Modem.Status.BUSY2REQ2DATA:
            self.status = Modem.Status.BUSY2REQ
       
    def confirmedMyIstr(self):
        """
        Confirm the instruction has been correctely processed
        @param self pointer to the class object
        """
        self.status = Modem.Status.IDLE
       
    def error(self, err_id):
        """
        Signal the instruction has not been correctely processed
        @param self pointer to the class object
        @param err_id error identifier
        """
        print >>sys.stderr, 'AN ERROR OCCURS: %s' % Modem.ErrorDict.error_dict[err_id]
        self.status = Modem.Status.IDLE
        
    def reset_myself(self):
        """
        Reset the modem status due to unexpected behavior
        @param self pointer to the class object
        """
        print >>sys.stderr, 'UNEXPECTED VALUE'
        self.status = Modem.Status.IDLE

    # def parseDivCommands(self, msg):
    #     """
    #     Parse the received message from the node and process it
    #     dividing all the commands
    #     @param self pointer to the class object
    #     """
    #     if(self.status == Modem.Status.KILL):
    #         return
    #     commands_list = msg.split(Interpreter.START_COMMAND)
    #     for command in commands_list:
    #         fine_command = command.split(Interpreter.END_COMMAND)
    #         print fine_command[0]
    #         self.parseCommand(fine_command[0])

    def checkConnection(self,msg):
        """
        Check if the socket returned something. If zero string, close
        it
        @param self pointer to the class object
        @param msg to check
        """
        if (len(msg) == 0):
            sleep(self.m_to/2)
            print >>sys.stderr, 'Closing due to possible server fault'
            self.close()

    def parseCommand(self, msg):
        """
        Parse the received message from the node and process it
        @param self pointer to the class object
        """
        if self.interpreter.debug:
            print msg
        if(self.status == Modem.Status.KILL):
            return
        command = msg.split(Interpreter.SEPARATOR)
        if (len(command)==1):
            if (command[0] == 'OK'):
                return self.confirmedMyIstr()
        elif (len(command)==2):
            if (command[0] == 'error'):
                return self.error(int(command[1]))
        elif (len(command)==3):
            if (command[0] == 'send_file'):
                return self.recvDataFile(command[1],int(command[2]),True)
            elif (command[0] == 'send_stream'):
                return self.recvDataFile(command[1],int(command[2]),False)
        return self.reset_myself()

if __name__ == "__main__":
    print("This is the modem class")
    

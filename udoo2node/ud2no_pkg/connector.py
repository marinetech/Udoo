import socket
import select
import sys
import binascii
import os
import math
from time import sleep
from interpreter import Interpreter

class Connector(object):
    """Class to connect the udoo to the node via TCP"""
    
    class Status:
        """Internal class where the status types are defined"""
        IDLE, BUSY = range(2)
    
    def __init__(self, ip, port, command_buf_size, data_buf_size, time_out = 0.005):
        """
        Constructor, initialize the socket and the buffer. 
        @param self pointer to the class object 
        @param ip string cointaining the IP address of the TCP server 
        @param port string with the port of the TCP server socket 
        @param command_buf_size: int with the command buffer size, in bytes (power of 2)
        @param time_out: float with the time out for the checking 
						 operation. 0 means not blocking at all.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (type(ip) is str and type(port) is int and math.log(command_buf_size,2)%1 == 0 and \
            math.log(data_buf_size,2)%1 == 0 and type(time_out) is float):
            self.server_address = (ip, port) # address of the TCP IP server
            self.command_buf_size = command_buf_size
            self.data_buf_size = data_buf_size
            self.to = time_out
            self.status = Connector.Status.IDLE
        else:
            raise ValueError("Connector error. Insert ip: string, port: int, \
                (command_buf_size: power of 2, data_buf_size: power of 2, time_out: float)")
      
    def connect(self):
        """
        Connect the client to the TCP server via socket.
        @param self pointer to the class object 
        """
        try:
            self.sock.connect(self.server_address)
        except socket.error, exc:
            print "Couldnt connect with the socket-server: %s\n terminating program" % exc
            sys.exit(1)
            
    def shutdown(self):
        """
        Shutdown the socket connection.
        @param self pointer to the class object 
        """
        self.sock.shutdown(socket.SHUT_WR)
    
    def close(self):
        """
        Shutdown and close the socket connection.
        @param self pointer to the class object 
        """
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except socket.error, exc:
            print "Socket already closed"
    
    def dataAvailable(self):
        """
        Check whether there are incoming data at the socket
        @param self pointer to the class object
        @return list pairs of sockets with data to received and errors
        """
        try:
            r, w, e = select.select([self.sock], [], [self.sock], self.to)
        except select.error:
            e = True
        return (r, e)
    
    def recvCommand(self):
        """
        Receive command or command answer from socket.
        @param self pointer to the class object 
        @return the command
        """        
        while(self.status == Connector.Status.BUSY):
            sleep(self.to)
        self.status = Connector.Status.BUSY
        command = self.sock.recv(self.command_buf_size)
        self.status = Connector.Status.IDLE
        return command

    # def recv(self):
    #     """
    #     Receive from socket.
    #     @param self pointer to the class object 
    #     @return incoming info from socket
    #     """        
    #     while(self.status == Connector.Status.BUSY):
    #         sleep(self.to)
    #     self.status = Connector.Status.BUSY
    #     command = self.sock.recv(self.command_buf_size)
    #     self.status = Connector.Status.IDLE
    #     return command

    def recvData(self):
        """
        Receive data from socket.
        @param self pointer to the class object 
        @return the data
        """        
        while(self.status != Connector.Status.IDLE):
            sleep(self.to)
        self.status = Connector.Status.BUSY
        data = self.sock.recv(self.data_buf_size)
        self.status = Connector.Status.IDLE
        return data

    def send(self, msg):
        """
        Send data to the socket.
        @param self pointer to the class object 
        """
        while(self.status != Connector.Status.IDLE):
            sleep(self.to)
        self.status = Connector.Status.BUSY
        self.sock.sendall(msg)
        self.status = Connector.Status.IDLE
        sleep(self.to)
        

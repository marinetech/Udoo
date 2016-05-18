import sys
import ud2no_pkg
import os
import time

TCP_IP = "127.0.0.1"
#TCP_IP = "localhost"
TCP_PORT = 44444
BUFFER_SIZE = 32
DATA_BUFFER_SIZE = 128

myPID = os.getpid()
print "HI ", myPID, "!!"
print("Hello")
bridge = ud2no_pkg.Modem(TCP_IP,TCP_PORT,True,BUFFER_SIZE,DATA_BUFFER_SIZE)
try:
    print("Connected")
    file_path = "ciccio"
    #bridge.sendDataFile(file_path)
    bridge.reqDataFile("ciccio4me")
    bridge.reqAllData()
    bridge.reqRTData(1,[1,3], "10",10)
    bridge.reqSetPower([2,3],5)
    bridge.reqPlayProj("ciccio",[1,4],"10")
    bridge.reqRecordData("ciccio",1,[1,4],"10",5)
    bridge.reqNodeStatus()
    bridge.reqResetProj([1,4])
    bridge.reqResetSensors(1,[1,4])
    bridge.reqResetAll()
    bridge.reqDeleteAllRec()
    bridge.reqDeleteAllSent()
    time.sleep(1)
    bridge.recvCommand()
    bridge.recvCommand()
    time.sleep(3)
    bridge.kill()
    #print("Sent")
	#while True:
		#time.sleep( 1 )
		#rx = bridge.recvCommand()
		#print "Rx ",rx
		#if (len(rx) == 0):
		#	break
finally:
    print >>sys.stderr, 'closing socket'
    bridge.close()

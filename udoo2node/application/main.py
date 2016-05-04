import sys
import ud2no_pkg
import os
import time

TCP_IP = "192.168.100.10"
#TCP_IP = "localhost"
TCP_PORT = 55555
BUFFER_SIZE = 32
DATA_BUFFER_SIZE = 128

myPID = os.getpid()
print "HI ", myPID, "!!"
print("Hello")
bridge = ud2no_pkg.Modem(TCP_IP,TCP_PORT,True,BUFFER_SIZE,DATA_BUFFER_SIZE)
try:    
    print("Connected")
    file_path = "ciccio"
    bridge.sendDataFile(file_path)
    bridge.reqHydData("ciccio4me")
    bridge.reqAllHydData()
    bridge.reqRTData([1,3], "10",10)
    bridge.setPower([2,3],5)
    bridge.playProj("ciccio",[1,4],"10")
    bridge.recordAudio("ciccio",[1,4],"10",5)
    bridge.getNodeStatus()
    bridge.resetProj([1,4])
    bridge.resetHydr([1,4])
    bridge.resetAll()
    bridge.deleteAllRec()
    bridge.deleteAllSent()    
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
         

#!/usr/bin/python
import thread
import psutil
import datetime
import time
import socket
from configobj import ConfigObj
thelist = []

class connection:
    def __init__(self, name):
        self.name = name
        print str(datetime.datetime.now().time()) + "," + "open stream  "  + str(self.name)
        
    def close(self):
        print str(datetime.datetime.now().time()) + "," + "close stream "  + str(self.name)
    
    #def __del__(self):
    #    print "del van stream"

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

if __name__ == '__main__':
    try:
        Configfile=ConfigObj("./Client.cfg")
        PROCNAME = Configfile['GENERAL']['procname']
        HOST = Configfile['GENERAL']['host']
        PORT = int(Configfile['GENERAL']['port'])
        NAME = Configfile['GENERAL']['name']
        print "Name: " + str(PROCNAME) + " Host: " + str(HOST) + " Port: " + str(PORT)
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                process = proc
        if not process:
            print "not found tvheadend"
            exit()
        print "Found " + str(process)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        s.send("{connect:" + NAME + "@" + 'client,}')
        print "conected to host"
        
        while(1):
            #print process.get_connections(kind='udp')
            for list in process.get_connections(kind='udp'):
                #print list.local_address[0]
                #if not thelist:
                #    thelist.append(connection(list.local_address[0]))
                    
                if not contains(thelist, lambda x: x.name == list.local_address[0]):
                    thelist.append(connection(list.local_address[0]))
                    s.send("{add:" + str(list.local_address[0]) + ",}")
            time.sleep(0.01)
            for list in thelist:
                #print thelist
                if not contains(process.get_connections(kind='udp'), lambda x: x.local_address[0] == list.name):
                    s.send("{remove:" + str(list.name) + ",}")
                    list.close()
                    thelist.remove(list)
                    #print "removed"
    except socket.error:
        print "conection to server lost"
        s.close()
        exit()
    except (SystemExit, KeyboardInterrupt):
        print "exit"
        s.send("{exit,}")
        exit()

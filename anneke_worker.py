#!/usr/bin/python
import thread
import psutil
import datetime
import time
import socket
from configobj import ConfigObj
import subprocess
thelist = []
decriptworkerlist = []

class connection:
    def __init__(self, name):
        self.name = name
        print "open van stream"  + str(self.name)
        
    def close(self):
        print "close van stream "
    
    def __del__(self):
        print "del van stream"

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

class decriptworker:
    def __init__(self, name):
        self.openchannel = "0"
        self.process = ""
        self.name = name
        
    def decriptopen(self, openchannel, command):
        self.openchannel = openchannel
        print self.name + ": opencommand " + command
        self.process = subprocess.Popen(command, shell=True)
    
    def decriptclose(self, openchannel):
        self.openchannel = "0"
        print self.name + ": closecommand "
        #self.process.kill()
        command = "cat " + str(self.name) + ".socket | xargs kill"
        subprocess.Popen(command, shell=True)


if __name__ == '__main__':
    try:
        Workersfile=ConfigObj("./Workers.cfg")
        PROCNAME = Workersfile['GENERAL']['procname']
        HOST = Workersfile['GENERAL']['host']
        PORT = int(Workersfile['GENERAL']['port'])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        print "connect workers workers"
        for selection in Workersfile['dvbworker']:
            s.send("{connect:" + selection + '@' + 'dvbworker' + \
                   '.' + str(Workersfile['dvbworker'][selection]['priority']) + \
            '.' + str(Workersfile['dvbworker'][selection]['freq']) + ',}')
            
        for selection in Workersfile['decriptworker']:
            decriptworkerlist.append(decriptworker(selection))
            s.send("{connect:" + selection + '@' + 'decriptworker' + \
                   '.' + Workersfile['decriptworker'][selection]['priority'] + ',}')
            #, Workersfile['dvbworker'][selection]['freq'], Workersfile['dvbworker'][selection]['priority']}
        #print "decriptworker found: " + str(decriptworkerlist)
        while 1:
            try:
                data = ''
                while 1:
                    data = data + s.recv(1)
                    if data.find(",}") != -1:
                        data = data.lstrip("{").rstrip(",}")
                        break
                
                if (len(data) < 2) or (data.find("exit") != -1):
                    print "cut " + str(clients.getpeername()),
                    print "conection to server lost"
                    s.close()
                    exit()
                else:
                    #print str(datetime.datetime.now().time()) + "," + data
                    if data.startswith("open:"):
                        data = data[5:]
                        print "open: " + data.split("@")[0] + " at freq = " + data.split("\0")[1]
                        configfile = open(data.split("@")[0] + ".config", "w")
                        configfile.write(data.split("\0")[3])
                        configfile.close()
                        command = Workersfile['dvbworker'][data.split("@")[0]]['basecommand'] + " -c " + data.split("@")[0] + ".config -r " + data.split("@")[0] + ".socket " + data.split("\0")[2] + " >>/home/jorrit/Bureaublad/Anneke/log.dvb"
                        print "Command: "+ command
                        subprocess.Popen(command, shell=True)
                        #subprocess.Popen("ls >> test.txt")
                        #subprocess.Popen(command)
                        print "Config dvblast: " + data.split("\0")[3] + "\r\n"
                        
                    elif data.startswith("update:"):
                        data = data[7:]
                        print "update: " + data.split("@")[0]
                        configfile = open(data.split("@")[0] + ".config", "w")
                        configfile.write(data.split("\0")[1])
                        configfile.close()
                        command = Workersfile['dvbworker'][data.split("@")[0]]['ctlcommand'] + " -r " + data.split("@")[0] + ".socket reload"
                        print subprocess.Popen(command, shell=True)
                        print "Command: " + command
                        
                    elif data.startswith("close:"):
                        data = data[6:]
                        print "close dvbworker " + data.split("@")[0] + " at freq = " + data.split("\0")[1] + "\r\n"
                        command = Workersfile['dvbworker'][data.split("@")[0]]['ctlcommand'] + " -r " + data.split("@")[0] + ".socket shutdown"
                        print subprocess.Popen(command, shell=True)
                        print "Command: " + command
                        
                    ## If open decript
                    elif data.startswith("decriptopen:"):
                        data = data[12:]
                        print "decriptopen: " + data.split("@")[0] + " Channel " + data.split("\0")[1]
                        command = Workersfile['decriptworker'][data.split("@")[0]]['basecommand'] + " -I " + data.split("\0")[1] + ":" + data.split("\0")[3] + " -O " + data.split("\0")[1] + ":" + data.split("\0")[2] + " " + data.split("\0")[4] + " -d " + data.split("@")[0] + ".socket"
                        #print "Command: " + command
                        for w in decriptworkerlist:
                            if w.name == data.split("@")[0]:
                                w.decriptopen(data.split("\0")[1], command)
                                break
                    elif data.startswith("decriptclose:"):
                        data = data[13:]
                        print "decriptclose: " + data.split("@")[0] + " Channel " + data.split("\0")[1]
                        command = Workersfile['decriptworker'][data.split("@")[0]]['basecommand']
                        for w in decriptworkerlist:
                            if w.name == data.split("@")[0]:
                                w.decriptclose(data.split("\0")[1])
                                break
                    else:
                        print str(datetime.datetime.now().time()) + ",ERROR," + data
                    
            except socket.error:
                print "ERROR: conection to server lost"
                s.close()
                exit()
        s.send("{exit,}")
        s.close()
        
    except (SystemExit, KeyboardInterrupt):
        print "exit"
        s.send("{exit,}")
        s.close()
        exit()
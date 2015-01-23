#!/usr/bin/python
import thread
import psutil
import datetime
import time
import socket
from configobj import ConfigObj


thelist = []
channellist = []
dvbworkerlist = []
decriptworkerlist = []
connectionlist = []
clientlist = []
baseadr = 225.1


clientport = 5200

class connection:
    def __init__(self, client, freq, channel):
        self.client = client
        self.freq = freq
        self.channel = channel
        #print "stream open: " + str(self.freq) + "." + str(self.channel) + " from: " + str(self.client)
        
    def close(self):
        print "",
        #print "stream close:" + str(self.freq) + "." + str(self.channel) + " from: " + str(self.client)

class dvbworker:
    #When workerconnects the server wil create this object
    #A connection can have multible workers, every worker has his one object
    def __init__(self, socket, name, priority, freq):
        self.socket = socket
        self.name = name
        self.priority = priority
        self.freq = freq
        self.openfreq = 0
        self.openchannels = []
        self.connections = []
        
        #self.socket.send("Created")
        
    #def __del__(self):
    #    print "del dvbworker"
        
    def newconnection(self, conection, freq):
        self.connections.append(conection)
        if self.openfreq == 0:
            print self.name + ": open freq"
            self.openfreq = freq
        else:
            print self.name + ": freq already open"
         
        if conection.channel not in self.openchannels:
            print self.name + ": open channel"
            self.openchannels.append(conection.channel)
            if not Channelsfile[self.openfreq]['tsdecriptopt']:
                
                print self.name + ": No decripter needed"
            else:
                print self.name + ": Find decripter"
                for w in decriptworkerlist:
                    if w.openchannel == "0":
                        w.decriptopen(baseadr + '.' + str(self.openfreq) + "." + str(conection.channel))
                        break
        else:
            print self.name + ": channel is already open"
             
        config = '#config generate by anneke'
        for c in self.openchannels:
            for i in channellist:
                if i == (baseadr + '.' + str(self.openfreq) + "." + str(c)):
                    config = config + "\r\n" + baseadr + '.' + str(self.openfreq) + "." + str(c) + ":"
                    if Channelsfile[self.openfreq]['tsdecriptopt']:
                        config = config + str(decriptport)
                    else:
                        config = config + str(lisport)
                    config = config + str(Channelsfile[self.openfreq]['Channels'][c])
                    break
        if len(self.connections) == 1:
            print self.name + ": open freq:" + str(self.openfreq) + " config:\r\n" + config + "\r\n"
            self.socket.send("{open:" + str(self.name) + "@" + "dvbworker\0"\
                             + str(self.openfreq) + "\0"\
                             + Channelsfile[str(self.openfreq)]['dvblastopt'] + "\0"\
                             + config + "\0" +",}")
        else:
            print self.name + ": update channel. config:\r\n" + config
            self.socket.send("{update:" + str(self.name) + "@" + "dvbworker\0"\
                             + config + "\0" +",}")
            
    def removeconnection(self, conection):
        for c in self.connections:
            if c.freq == conection.freq and c.channel == conection.channel:
                if c.client == conection.client: 
                    c.close()
                    self.connections.remove(c)
        if len(self.connections) < 2:
            self.openchannels.remove(conection.channel)
            if not Channelsfile[self.openfreq]['tsdecriptopt']:
                print self.name + ": No decripter open"
            else:
                for w in decriptworkerlist:
                    if w.openchannel == baseadr + '.' + str(self.openfreq) + "." + str(conection.channel):
                        w.decriptclose(baseadr + '.' + str(self.openfreq) + "." + str(conection.channel))
                        break
                
        if len(self.connections) < 1:
            print self.name + ": noting to do"
            self.socket.send("{close:" + str(self.name) + "@" + "dvbworker\0"\
                             + str(self.openfreq) +",}")
            self.openfreq = 0
            self.openchannels = []
        else:
            config = '#config generate by anneke'
            for c in self.openchannels:
                for i in channellist:
                    if i == (baseadr + '.' + str(self.openfreq) + "." + str(c)):
                        config = config + "\r\n" + baseadr + '.' + str(self.openfreq) + "." + str(c) + ":"
                        if Channelsfile[self.openfreq]['tsdecriptopt']:
                            config = config + str(decriptport)
                        else:
                            config = config + str(lisport)
                        config = config + str(Channelsfile[self.openfreq]['Channels'][c])
                        break
            print self.name + ": update channel. config:\r\n" + config + "\r\n"
            self.socket.send("{update:" + str(self.name) + "@" + "dvbworker\0"\
                             + config + "\0" +",}")

class decriptworker:
    def __init__(self, socket, name, priority):
        self.socket = socket
        self.name = name
        self.priority = priority
        self.openchannel = "0"
        
    #def __del__(self):
    #    print "del decriptworker"
        
    def decriptopen(self, channel):
        self.openchannel = channel
        print self.name + ":  decriptopen " + self.openchannel
        self.socket.send("{decriptopen:" + str(self.name) + "@" + "decriptworker\0" +\
                         str(self.openchannel) + "\0" +\
                         str(lisport) + "\0" +\
                         str(decriptport) + "\0" +\
                         Channelsfile[channel.split(".")[2]]['tsdecriptopt'] + "\0" +\
                         ",}")
        
    def decriptclose(self, channel):
        if self.openchannel != channel:
            print self.name + ": BUGGGGG..."
        else:
            print self.name + ":  decriptclose " + self.openchannel
            self.socket.send("{decriptclose:" + str(self.name) + "@" + "decriptworker\0" +\
                             str(self.openchannel) + "\0" +\
                             ",}")
            self.openchannel = "0"
    


def contains(list, filter):
    c = 0
    for x in list:
        if filter(x):
            c = c+1
    return c

def serverlissener():
    while 1:
        try:
            (clientsocket, clientaddr) = serversocket.accept()
            print "Accepted connection from: ", clientaddr
            clientlist.append(clientsocket)
        except socket.error:
            pass
        except SystemExit, KeyboardInterrupt:
            print "exit"
            exit()
            
def dvbworkercheck(freq, connection):
    for w in dvbworkerlist:
        if freq == w.openfreq:
            w.newconnection(connection, freq)
            return 1
    print "no worker has freq: " + freq + " open"
    for w in dvbworkerlist:
        if freq in w.freq:
            if w.openfreq == 0:
                w.newconnection(connection, freq)
                return 2
    print "no worker found TODO: wating list"
    return 0

if __name__ == '__main__':
    try:
        Channelsfile=ConfigObj("./Channels.cfg")
        ##Workersfile=ConfigObj("./Workers.cfg")
        print "import channels"
        for selection in Channelsfile:
            if selection == "GENERAL":
                lisport = Channelsfile[selection]['port']
                print "port = "+ lisport
                decriptport = Channelsfile[selection]['decriptport']
                print "decript port = " + decriptport
                baseadr = Channelsfile[selection]['base']
                print "base adress = " + baseadr
            elif selection.isdigit() and int(selection) < 254:
                print "freq found: " + selection
                for channels in Channelsfile[selection]['Channels'].keys():
                    if channels.isdigit() and int(channels) < 254:
                        print "Channel found + " + baseadr + "." + selection + "." + channels
                        channellist.append(str(baseadr) + "." + str(selection) + "." + str(channels))
                    else:
                        print "channel is not a number between 1 and 254: " + channels
            else:
                print "freq is not a number between 1 and 254: " + selection
         
        '''
        print "import workers"
            
        for selection in Workersfile['dvbworker']:
            dvbworkerlist.append(dvbworker(selection,
                                           Workersfile['dvbworker'][selection]['priority'],
                                           Workersfile['dvbworker'][selection]['freq']))
        sorted(dvbworkerlist, key=lambda dvbworker: dvbworker.priority)
                
        for selection in Workersfile['decriptworker']:
            decriptworkerlist.append(selection)
            #, Workersfile['dvbworker'][selection]['freq'], Workersfile['dvbworker'][selection]['priority']}
        print "decriptworker found: " + str(decriptworkerlist)
        ''' 
         
         
         
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('0.0.0.0', clientport))
        serversocket.listen(5)
        print "Server is listening for clients\n"
        serversocket.settimeout(1)
        serversocket.setblocking(0)
        while 1:
            try:
                (clientsocket, clientaddr) = serversocket.accept()
                print "Accepted connection from: ", clientaddr
                clientsocket.setblocking(0)
                connectionlist.append(clientsocket)
            except (socket.error, socket.timeout):
                pass
            for clients in connectionlist:
                data = ''
                try:
                    while 1:
                        data = data + clients.recv(1)
                        if data.find(",}") != -1:
                            data = data.lstrip("{").rstrip(",}")
                            break
                        
                    if (len(data) < 2) or (data.find("exit") != -1):
                        print "cut " + str(clients.getpeername())
                        for i in dvbworkerlist[:]:
                            if i.socket == clients:
                                print " dvbworker: " + str(i.name),
                                dvbworkerlist.remove(i)
                        for i in clientlist[:]:
                            if i == clients:
                                print " Client: " + str(i.getpeername()),
                                clientlist.remove(i)
                        for i in decriptworkerlist[:]:
                            if i.socket == clients:
                                print " decriptworker: " + str(i.name),
                                decriptworkerlist.remove(i)
                        connectionlist.remove(clients)
                        print ""
                        print "stil connected:",
                        print "connection(s): " + str(len(connectionlist))
                        print "dvbworker(s): " + str(len(dvbworkerlist))
                        print "decriptworker(s): " + str(len(decriptworkerlist))
                        print "client(s): " + str(len(clientlist))
                        clients.close()
                            
                    else:
                        print str(datetime.datetime.now().time()) + "," + str(clients.getpeername()[0]) + ","  + data
                        if data.startswith("connect:"):
                            data = data[8:]
                            if data.split("@")[1].startswith("client"):
                                clientlist.append(clients)
                            elif data.split("@")[1].startswith("dvbworker"):
                                dvbworkerlist.append(dvbworker(clients, data.split("@")[0], 
                                           data.split(".")[1], data.split(".")[2].translate(None, '[]\'\ ').split(',')))
                                sorted(dvbworkerlist, key=lambda dvbworker: dvbworker.priority)
                            elif data.split("@")[1].startswith("decriptworker"):
                                #print "ToDo create dicriptworker" + data.split("@")[0]+ ' ' + data.split(".")[1]
                                decriptworkerlist.append(decriptworker(clients, data.split("@")[0],
                                           data.split(".")[1]))
                        elif data.startswith("add:"):
                            if data.count(".") != 3:
                                print "error data: " + data
                                break
                            data = data.lstrip("add:")
                            dvbworkercheck(data.split(".")[2], connection(clients.getpeername(),data.split(".")[2], data.split(".")[3]))
                            #check for free worker
                            #thelist.append(connection(clients.getpeername(),data.split(".")[2], data.split(".")[3]))
                        elif data.startswith("remove:"):
                            if data.count(".") != 3:
                                print "error data: " + data
                                break
                            data = data.lstrip("remove:")
                            #remove connection from worker
                            for i in dvbworkerlist:
                                if i.openfreq == data.split(".")[2]:
                                    i.removeconnection(connection(clients.getpeername(),data.split(".")[2], data.split(".")[3]))
                                    break
                        else:
                            print str(datetime.datetime.now().time()) + "," + str(clients.getpeername()[0]) + ","  + data
                        #thelist.append(connection(data))
                except (socket.error, socket.timeout):
                    pass
            time.sleep(0.01)
        print "exit net"
        for element in connectionlist:
            connectionlist.remove(element)
            element.close()
        serversocket.close()
            
    finally:
        print "exit fout"
        for element in connectionlist:
            connectionlist.remove(element)
            element.close()
        serversocket.close()

        
#(SystemExit, KeyboardInterrupt)
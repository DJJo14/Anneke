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


clientport = 52000

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
    ## TODO need to add connection
    #When workerconnects the server wil create this object
    #A connection can have multible workers, every worker has his one object
    def __init__(self, socket, name, priority, freq):
        self.socket = socket
        self.name = name
        self.priority = priority
        self.freq = freq
        self.openfreq = 0
        self.connections = []
        #self.socket.send("Created")
        
    def __del__(self):
        print "del"
        
    def newconnection(self, conection, freq):
        self.connections.append(conection)
        config = '#config generate by anneke'
        for c in self.connections:
            for i in channellist:
                if i == (baseadr + '.' + str(c.freq) + "." + str(c.channel)):
                    config = config + "\r\n" + baseadr + '.' + str(c.freq) + "." + str(c.channel) + ":"
                    if Channelsfile[c.freq]['tsdecriptopt']:
                        config = config + str(decriptport)
                    else:
                        config = config + str(lisport)
                    config = config + str(Channelsfile[c.freq]['Channels'][c.channel])
                    break
        if len(self.connections) == 1:
            self.openfreq = freq
            print "dvbworker: "+ str(self.name) + " does freq:" + str(self.openfreq) + " config:\r\n" + config + "\r\n"
            self.socket.send("{open:" + str(self.name) + "@" + "dvbworker\0"\
                             + str(self.openfreq) + "\0"\
                             + Channelsfile[str(self.openfreq)]['dvblastopt'] + "\0"\
                             + config + "\0" +",}")
        else:
            print "dvbworker update channel. config:\r\n" + config
            self.socket.send("{update:" + str(self.name) + "@" + "dvbworker\0"\
                             + config + "\0" +",}")
            
    def removeconnection(self, conection):
        for c in self.connections:
            if c.client == conection.client and c.freq == conection.freq and c.channel == conection.channel:
                c.close()
                self.connections.remove(c)
        if len(self.connections) < 1:
            print "dvbworker: "+ str(self.name) + " got noting to do"
            self.socket.send("{close:" + str(self.name) + "@" + "dvbworker\0"\
                             + str(self.openfreq) +",}")
            self.openfreq = 0
        else:
            config = '#config generate by anneke'
            for c in self.connections:
                for i in channellist:
                    if i == (baseadr + '.' + str(c.freq) + "." + str(c.channel)):
                        config = config + "\r\n" + baseadr + '.' + str(c.freq) + "." + str(c.channel) + ":"
                        if Channelsfile[c.freq]['tsdecriptopt']:
                            config = config + str(decriptport)
                        else:
                            config = config + str(lisport)
                        config = config + str(Channelsfile[c.freq]['Channels'][c.channel])
                        break
            print "dvbworker update channel. config:\r\n" + config + "\r\n"
            self.socket.send("{update:" + str(self.name) + "@" + "dvbworker\0"\
                             + config + "\0" +",}")

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
        serversocket.bind(('localhost', clientport))
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
                        print "cut " + str(clients.getpeername()),
                        for i in dvbworkerlist[:]:
                            print str(i.socket) + " == " + str(clients)
                            if i.socket == clients:
                                print " dvbworker: " + str(i.name)
                                dvbworkerlist.remove(i)
                        for i in clientlist:
                            if i == clients:
                                print " Client: " + str(i.name)
                                clientlist.remove(i)
                        #for i in decriptworkerlist:
                        #    if i.socket == clients:
                        #        print " decriptworker: " + str(i.name)
                        #        decriptworkerlist.remove(i)
                        connectionlist.remove(clients)
                        print str(dvbworkerlist)
                        print str(connectionlist)
                        clients.close()
                            
                    else:
                        print str(datetime.datetime.now().time()) + "," + str(clients.getpeername()[0]) + ","  + data
                        if data.startswith("connect:"):
                            data = data.lstrip("connect:")
                            if data.split("@")[1].startswith("client"):
                                clientlist.append(clients)
                            elif data.split("@")[1].startswith("dvbworker"):
                                dvbworkerlist.append(dvbworker(clients, data.split("@")[0], 
                                           data.split(".")[1], data.split(".")[2].translate(None, '[]\'\ ').split(',')))
                                sorted(dvbworkerlist, key=lambda dvbworker: dvbworker.priority)
                            elif data.split("@")[1].startswith("decriptworker"):
                                print "ToDo create dicriptworker" + data.split("@")[0]+ ' ' + data.split(".")[1]
                                #decriptworkerlist.append(decriptworker(data.split("@")[0],
                                #           data.split(".")[1]))
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
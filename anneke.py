#!/usr/bin/python
import thread
import psutil
import time
thelist = []

class connection:
    def __init__(self, name):
        self.name = name
        print "open van stream"  + str(self.name)
    
    def __del__(self):
        print "close van stream "

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

if __name__ == '__main__':
    try:
        PROCNAME = "tvheadend"
        for proc in psutil.process_iter():
            if proc.name == PROCNAME:
                process = proc
        if not process:
            print "not found tvheadend"
            exit()
        print "Found " + str(process)
        
        while(1):
            for list in process.get_connections(kind='udp'):
                #print list.local_address[0]
                #if not thelist:
                #    thelist.append(connection(list.local_address[0]))
                    
                if not contains(thelist, lambda x: x.name == list.local_address[0]):
                    thelist.append(connection(list.local_address[0]))
            for list in thelist:
                print thelist
                if not contains(process.get_connections(kind='udp'), lambda x: x.local_address[0] == list.name):
                    #thelist.remove(list)
                    print "removed"
                #if not process.get_connections(kind='udp'):
                #    thelist.remove(list)
            time.sleep(0.5)
     
    except SystemExit, KeyboardInterrupt:
        exit()
import time
import httplib
from threading import Thread
from escpos import *
import ConfigParser
import json

#url, db, username, password = 'http://localhost:8069', 'queue_dev', 'admin', 'P@ssw0rd'
#common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
#print common.version()
#uid = common.authenticate(db, username, password, {})
#models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))


def print_thread():    
    #type_ids = models.execute_kw(db, uid, password, 'queue.type', 'search',[()])
    #print type_ids
    #types = models.execute_kw(db, uid, password,'queue.type', 'read',[type_ids], {'fields': ['number','name']})
    #print types
    while(True):
        #try:
            print "Check Print Data"
            conn = httplib.HTTPConnection('localhost',8069)
            conn.request("GET","/queue/appprint")
            resp = conn.getresponse()
            print resp.status, resp.reason
            data = resp.read()
            print data
            j = json.loads(data)            
            #    for trans in transs:
            #        try:    
            #            Epson = printer.Serial("/dev/ttyUSB0")
            #            #0557:2008
            #            #Epson = printer.Usb(0x0557,0x2008)
            #            Epson.text("MAL TAMAN ANGGREK\n")    
            #            Epson.text("\n")
            #            Epson.text("\n")
            #            Epson.text("\n")
            #            Epson.text("\n")
            #            Epson.text("\n")        
            #            Epson.cut()
            #        except:
            #            print "No Printer"
            time.sleep(1)
        #except:
        #    print "Server Error"
            
t = Thread(target=print_thread)
t.start()
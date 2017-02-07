import pyaudio
import wave
import sys
import time
import httplib
from threading import Thread
from escpos import *
import ConfigParser
import json


#if len(sys.argv) < 2:
#    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
#    sys.exit(-1)

#wf = wave.open(sys.argv[1], 'rb')
def play_sound(file):
    CHUNK = 1024
    wf = wave.open(file,'rb')
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    
    data = wf.readframes(CHUNK)
    
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    
    p.terminate()
    
#play_sound("/home/wahhid/Music/Sound/nomor_antrian.wav")
#play_sound("/home/wahhid/Music/Sound/1.wav")
#play_sound("/home/wahhid/Music/Sound/1.wav")
#play_sound("/home/wahhid/Music/Sound/4.wav")
#play_sound("/home/wahhid/Music/Sound/silahkan_ke_loket.wav")
#play_sound("/home/wahhid/Music/Sound/0.wav")
#play_sound("/home/wahhid/Music/Sound/0.wav")
play_sound("/home/wahhid/Music/Sound/8.wav")

def sound_thread():    
    #type_ids = models.execute_kw(db, uid, password, 'queue.type', 'search',[()])
    #print type_ids
    #types = models.execute_kw(db, uid, password,'queue.type', 'read',[type_ids], {'fields': ['number','name']})
    #print types
    while(True):
        #try:
            print "Check Sound Data"
            conn = httplib.HTTPConnection('localhost',8069)
            conn.request("GET","/queue/pickupsound")
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
            
#t = Thread(target=sound_thread)
#t.start()
import os
import glob
import time
import traceback
import RPi.GPIO as GPIO
from bluetooth import *

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)


try:
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    advertise_service(server_sock, "McPiServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE],
                      #                   protocols = [ OBEX_UUID ]
                      )
    while True:
        print "Waiting for connection on RFCOMM channel %d" % port

        client_sock, client_info = server_sock.accept()
        print "Accepted connection from ", client_info

        try:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            print "received [%s]" % data

            if data == 'temp':
                data = str(read_temp()) + '!'
            elif data == 'lightOn':
                GPIO.output(17, False)
                data = 'light on!'
            elif data == 'lightOff':
                GPIO.output(17, True)
                data = 'light off!'
            else:
                data = 'WTF!'
            client_sock.send(data)
            print "sending [%s]" % data

        except IOError:
            pass

        except KeyboardInterrupt:

            print "disconnected"

            client_sock.close()
            server_sock.close()
            print "all done"

            break
except:
    traceback.format_exc()
finally:
    GPIO.cleanup()
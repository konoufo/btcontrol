import traceback

from bluetooth import *
from cloudant.client import Cloudant
from cloudant.query import Query


username = "752c0e5d-99e7-4853-9e67-4926ed90cb42-bluemix"
password = "60b1102465ab738176458aebee6b01be8540800a53de3b6b2183666a5573cdd3"
uri = "https://752c0e5d-99e7-4853-9e67-4926ed90cb42-bluemix.cloudant.com"
client = Cloudant(username, password, url=uri)
client.connect()
db = client['users']


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
            print "received {}".format(data)

            # if data in mongodb send wifi pass
            query = Query(db, selector={"id": data}, limit=1)
            # cursor = db.users.find({"id": data})
            passphrase = None
            with open("/etc/hostapd/hostapd.conf", 'r') as f:
                for s in f.read().replace('\r\n', '\n').split('\n'):
                    if s.startswith('wpa_passphrase'):
                        passphrase = s[s.find("=") + 1 :]  + '#' if len(s) > 15 else None
            for user in query.result:
                if passphrase is not None:
                    client_sock.send(passphrase)
                print "sending {}".format(passphrase)
                break

        except IOError:
            print traceback.format_exc()

        except KeyboardInterrupt:

            print "disconnected"

            client_sock.close()
            server_sock.close()
            print "all done"

            break
except:
    print traceback.format_exc()
finally:
    print "disconnected"

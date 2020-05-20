import socket
import logging
import sys

# Opretter UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#logging-fil til at logge info om three-way-handshake
logging.basicConfig(filename="Connections.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


server_address = ('localhost', 10000)
logging.info('Server: starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
sock.settimeout(4.0)


try:
    #Three-way-handshake
    logging.info('Server: waiting to receive message')
    data, address = sock.recvfrom(4096)
    msg = data.decode().split(" ")
    msgHead = str(msg[0])
    clientIP = str(msg[1])
    #Tjekker om besked-præfiks korrekt
    try:
        if msg[0] == 'com-0':
            logging.info('Client: ' + data.decode())
            sock.sendto(('com-0 accept '+ clientIP).encode(), address)
            logging.info('Server: com-0 accept ' + clientIP)
    except:
        logging.info('Server: wrong message from client. Connection closed')
        sock.close()

    data,address = sock.recvfrom(4096)
    new_msg = data.decode().split(" ")
    try:
        if new_msg[1] == 'accept':
            logging.info('Client: ' + data.decode())
            logging.info('Server: three way handshake complete \n')
    except:
        logging.info('Server: three way handshake failed. Connection closed')
        sock.close()

    resNr = 0
    resPrefix = 'res-'
    serverResponse = '=I am server'
    errorMessage = 'err-0=error'
    exitMessage = 'exit-0=exit'
    while (True):
        data, address = sock.recvfrom(4096)

        #serveren registrere heartbeat fra klienten og fortsætter
        if data.decode() == 'con-h 0x00':
            continue
        #nedenstående if-statements er kun til at teste metoden hos klienten, der sender 25 packages
        if data.decode() == 'Repeated message':
            print(data.decode())
            continue
        #splitter besked fra klienten, hvis formatet på beskeden tillader det. Hvis ikke sendes fejl-kode til klienten og forbindelsen lukkes
        try:
            clientMessage = data.decode().split("=")
            messageHead = clientMessage[0].split('-')
            messageBody = clientMessage[1]
            messagePrefix = messageHead[0]
            messageNr = messageHead[1]
        except:
            sock.sendto(errorMessage.encode(), address)
            sock.close()
            sys.exit()

        if messagePrefix == 'msg' and int(messageNr) == resNr:
            resNr = int(messageNr) + 1
            if messageBody == 'exit':
                sock.sendto(exitMessage.encode(), address)
                sys.exit(1)
            print('Besked fra klient: ' + data.decode())
            sock.sendto((resPrefix + str(resNr) + serverResponse).encode(), address)

        elif messagePrefix == 'msg' and int(messageNr) == resNr + 1:
            resNr = int(messageNr) + 1
            if messageBody == 'exit':
                sock.sendto(exitMessage.encode(), address)
                sys.exit(1)
            print('Besked fra klient: ' + data.decode())
            sock.sendto((resPrefix + str(resNr) + serverResponse).encode(), address)
        #Hvis message-prefix eller message-number er ukorrekt, sendes fejlbesked til klienten og forbindelsen lukkes
        else:
            sock.sendto(errorMessage.encode(), address)
            sock.close()
            sys.exit(1)

except socket.timeout:
    sock.sendto(('con-res=0xFE').encode(), address)

finally:
    print('closing socket')
    sock.close()



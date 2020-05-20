import socket
from _datetime import datetime
import time
from threading import Timer

#Læser configFilen
config = open('opt.conf')
line = config.readline()
lineCount = 1

while line:
    if lineCount == 1:
        line = line.strip()
        split_line = line.split(':')
        keepAliveValue = str(split_line[1])
    if lineCount == 2:
        line = line.strip()
        split_line = line.split(':')
        packageNumberValue = int(split_line[1])
    line = config.readline()
    lineCount += 1

def heartBeat():
    try:
        if keepAliveValue == 'True':
            timer = Timer(3.0, heartBeat)
            timer.setDaemon(True)
            timer.start()
            sock.sendto(('con-h 0x00').encode(), server_address)
            return
        else:
            return
    except:
        print('something went wrong')

#metode til at sende et antal packages afsted, som er defineret i opt.conf filen
def sendMultiplePackages():
    start = time.time()
    for x in range(packageNumberValue):
        sock.sendto(('Repeated message').encode(), server_address)
    end = time.time()
    print('total time: ' + str((end-start)))

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)

try:
    # Send data til server
    client_ip = '127.0.0.1'
    sock.sendto(('com-0 {}'.format(client_ip)).encode(), server_address)

    # Modtag og tjek svar fra server
    print('waiting to receive')
    data, server = sock.recvfrom(4096)
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    msg = data.decode().split(" ")

    if msg[0] == 'com-0' and msg[1] == 'accept':
        print(data.decode())
        sock.sendto(('com-0 accept').encode(), server_address)

    #Three way handshake overstået
    msgNumber = 0
    msgPrefix = 'msg-'

    print('Enter message and press enter. To close connection type "exit"')
    clientInput = input()
    clientMsg = msgPrefix + str(msgNumber) + '=' + clientInput
    print(clientMsg)
    sock.sendto(clientMsg.encode(), server_address)

    heartBeat()
    while(True):
        #sendMultiplePackages()
        data,server = sock.recvfrom(4096)
        serverResponse = data.decode().split("=")
        responseHead = serverResponse[0].split('-')
        responseBody = serverResponse[1]
        responsePrefix = responseHead[0]
        responseNr = responseHead[1]

        if responsePrefix == 'res' and int(responseNr) == msgNumber+1:
            print(data.decode())
            msgNumber = int(responseNr) + 1
            print('Enter message and press enter. To close connection type "exit"')
            newMessage = input()
            print(msgPrefix + str(msgNumber) + '=' + newMessage)
            sock.sendto((msgPrefix + str(msgNumber) + '=' + newMessage).encode(), server_address)

        elif responseBody == 'error':
            print('Something went wrong. Connection terminated')

#Når nedenstående package sendes til serveren, er forbindelsen allerede brudt, så vel ikke korrekt løst?
except ConnectionResetError:
    if data.decode()=='con-res=0xFE':
        sock.sendto(('con-res=0xFF').encode(), server_address)
        print('Connection terminated')

finally:
    print('closing socket')
    sock.close()
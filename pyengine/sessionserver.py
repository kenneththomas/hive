import socket
import hive

def Main():
    host = "127.0.0.1"
    port = 20015

    mySocket = socket.socket()
    mySocket.bind((host,port))

    mySocket.listen(1)
    conn, addr = mySocket.accept()
    print ("Connection from: " + str(addr))
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print ("from connected  user: " + str(data))
        #we need to validate this is an actual fix message and wont blow up hive. improve this
        if ';35=' in str(data):
            data = hive.fixgateway(data)
            print ("sending: " + str(data))
            conn.send(data.encode())
        else:
            #do we want to make this a FIX logoff instead?
            conn.send('invalid message'.encode())

    conn.close()

if __name__ == '__main__':
    Main()
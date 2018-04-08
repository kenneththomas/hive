import socket

def Main():
    host = '127.0.0.1'
    port = 20015

    mySocket = socket.socket()
    mySocket.connect((host,port))

    message = input(" -> ")

    while message != 'q':
            mySocket.send(str(message).encode())
            data = mySocket.recv(1024).decode()

            print ('Received from server: ' + data)

            message = input(" -> ")

    mySocket.close()

if __name__ == '__main__':
	Main()

import socket
import threading
import os
import tqdm

host = socket.gethostbyname(socket.gethostname())
port = 2424

service = input("Enter (file transfer) to transfer files or (chatroom) to join a chat: ")
service = service.lower()

if service == 'chatroom':
    username = input("Enter a username for the chatroom: ")

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((host,port))

def receive_message():
    while True:
        try:
            message = client.recv(1024).decode('utf-8') 
            if message == 'service':
                client.send(service.encode('utf-8'))
            if service == 'chatroom':
                if message == 'username':
                    client.send(username.encode('utf-8'))
                if message != '' and message != 'service' and message != 'username':
                    print(message)
            elif service == ' file transfer':
                pass
    
        except:
            client.close()
            if service == 'chatroom':
                print('You have left the chatroom!')
            else:
                print('You have left the server!')
            break

def send_message():
    while True:
        try:
            if service == 'file transfer':
                file = input("Enter full path of file to transfer:\n")
                if os.path.exists(file):
                    fileTransfer(file)
                    break

            elif service == 'chatroom':
                chatroom(client)

        except:
            client.close()
            break

def fileTransfer(file):
    while True:
        try:
            filename = os.path.basename(file)
            filesize = os.path.getsize(file)

            client.send(f'{filename}:{filesize}'.encode())

            progress = tqdm.tqdm(range(filesize),f'sending {filename}',unit='B',unit_scale=True,unit_divisor=1024)

            with open(file,'rb') as f:
                for _ in progress:
                    data = f.read(1024)
                    if not data:
                        break

                    client.sendall(data)

                    progress.update(len(data))
                    
                print(f'\nfile transfered successfully')

            client.close()
            break

        except:
            client.close()
            break

def chatroom(client):
    message = f'{username}: {input("")}'.encode('utf-8')
    client.send(message)

t1 = threading.Thread(target=receive_message)
t1.start()

t2 = threading.Thread(target=send_message)
t2.start()

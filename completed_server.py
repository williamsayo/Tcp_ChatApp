import socket
import threading
import tqdm
import os

clients = []
fileTransfer_clients = []
fileTransfer_clients_name = []
chatroom_clients = []
usernames = []
chatroom_keywords = {'exit':['\exit','\quit','\leave room']}

host = socket.gethostbyname(socket.gethostname())
port = 2424

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

def broadcast_message(message):
    for client in chatroom_clients:
        client.send(f'{message}'.encode('utf-8'))
  
def remove_client(user):    
    if service == 'chatroom':
        ind = chatroom_clients.index(user)
        chatroom_clients.remove(user)
        username = usernames[ind]
        usernames.remove(username)
        broadcast_message(f'{username} left the chat room!')
        print(f'{username} left the server')

    elif service == 'file transfer':
        fileTransfer_clients.remove(user)
        fileTransfer_clients_name.remove(socket.getnameinfo(addr,1)[0])
        print(f'{addr} left the server')
    
    clients.remove(user)
    user.close()

def keyword_handler(message):
    for chatroom_keyword in chatroom_keywords:
        if message in chatroom_keywords.get(chatroom_keyword):        

            return chatroom_keyword

def chatroom_handler(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            formattedMessage = message.split(':')[1].strip()
            formattedMessage = formattedMessage.lower()
            check = False

            for i in chatroom_keywords:
                if formattedMessage in chatroom_keywords.get(i):
                    check = True

            if not check:
                broadcast_message(message)
            else:
                keyword = keyword_handler(formattedMessage)

                if keyword == 'exit':
                    remove_client(client)
                    break

        except:
            remove_client(client)
            break

def fileTransfer_handler(client):
    try:
        current_path = os.path.split(__file__)[0]
        received_path = os.path.join(current_path,'received_files')

        if not os.path.exists(received_path):
            os.mkdir(received_path)

        receive = client.recv(1024).decode()
        filename,filesize = receive.split(':')

        filesize = int(filesize)

        progress = tqdm.tqdm(range(filesize),f'receiving {filename} from {socket.getnameinfo(addr,1)[0]}',unit='B',unit_scale=True,unit_divisor=1024)
        
        file_path = os.path.join(received_path,filename)

        with open(file_path,'wb') as f:
            for _ in progress:
                data = client.recv(1024)
                if not data:
                    break
                f.write(data)
                progress.update(len(data))

        client.close()

    except:
        remove_client(client)

def client_handler(client):
    while True:
        try:
            if service == 'chatroom':
                chatroom_handler(client)

            elif service == 'file transfer':
                fileTransfer_handler(client)

            break

        except:
            remove_client(client)
            break

def listener():
    global service,addr
    
    while True:
        client, addr = server.accept()
        print(f"{addr} connected to the server")

        client.send("service".encode('utf-8'))
        service = client.recv(1024).decode('utf-8')
        service = service.lower()
        client.send("connected to the server".encode('utf-8'))

        if service == 'chatroom':
            client.send("username".encode('utf-8'))
            chatroom_clients.append(client)
            username = client.recv(1024).decode('utf-8')
            print(f'Username of the client is {username}')
            usernames.append(username)
            broadcast_message(f'{username} joined the chat room!')
        
        elif service == 'file transfer':
            print(f'{socket.getnameinfo(addr,1)[0]} connected to the server for file transfer')
            fileTransfer_clients.append(client)
            fileTransfer_clients_name.append(socket.getnameinfo(addr,1)[0])

        clients.append(client)
        print(f'[Active connections] {len(clients)}')

        t2 = threading.Thread(target=client_handler , args=[client])
        t2.start()

print(f'server started at {host} on port {port}')
print(f'Server is running...')
listener()
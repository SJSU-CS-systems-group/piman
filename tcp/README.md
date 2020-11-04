# What is tcp.py?
`tcp.py` is a very simple threaded program running on the TCP protocol used to transfer a single file, `rootfs.tgz`.

`tcp.py` does the following:
* establishing a connection 1st and foremost
* processing requests after a connection has been established
* creates a sperate connection to transfer `rootfs.tgz`

This protocol is purposefully kept simple due to simple nature of its purpose. After each exchange of messages between the Pi and Piman, Piman logs the event that just occurred. This protocol establishes a tcp connection to port 3333 of the piman as a control connection, and another at 4444 which is used as a file transfer connection. Commands and responses are sent through the control connection, while the file transfer connection is used to transfer `rootfs.tgz`.
But it will be different from traditional protocols in that ports will be used to establish a connection instead of IP addresses. Since this is between Ben's vm and the Pis, we already know the IP of the server (piman).

# Why is tcp.py designed like this?
`tcp.py` is designed to like this because its purpose is just to transfer the `/../install/boot/rootfs.tgz` file to the pi.  
But why use `tcp.py` to do this when `/../tftp/tftp.py` already exists to transfer boot files? This is due to `rootfs.tgz` being so large (~500 MB).  
Because of the size, there must be a dedicated connection with the pi and our `piman.py` server.  
It is also important to note that because we are transfering `root.tgz` from ben's VM instead of from a location on the internet, there is no need to use IP addresses.     

# How does tcp.py work?    
TCP works by receiving messages sent from the `hello_protocol.sh` in the Raspberry Pi which should have been transferred through `tftp.py`. Depending on the message sent by the Raspberry pi, it'll send over the next instruction for the Pi to do. Once the TCP starts, the rootfs is also transferred over through another thread. **Note: to reinstall, please reset the `reinstall.txt` file or else it'll reinstall the same Raspberry Pi like how piman was called last time with restart!**

### Function: do_tcp(data_dir, tcp_port, connection_address)
_Description_: this function will begin the TCP implementation as a thread.  
_Called by_: `tcp.py` -> `__main__`  
_Return_: N/A  

| Type | Variable | Description |
|-------|-------|-------|
|String |data_dir |the dirctory that __contains__ the `install` directory |
|int |tcp_port | the port that TCP will run on, given by `piman.py` |
|String |connection_address | the IP address that TCP will connect to, which in this case should be "127.0.0.1" since `rootfs.tgz` is on the local machine |

```python
def __transfer_file(self, client_socket):
        print("TCP - started file_transferring")
        try:
            # opens the specified file in a read only binary form
            transfer_file = open("{}/{}".format(self.data_dir, "rootfs.tgz"), "rb")
            data = transfer_file.read()
            print("TCP - read rootfs.tgz")

            if data:
                # send the data
                print("TCP - sending rootfs.tgz")
                client_socket.send(data)
                print("TCP - finished sending rootfs.tgz")
        except:
            traceback.print_exc()
        print("TCP - finished file_transferring")
        client_socket.close()
```

### Function: start(self)
_Description_: This will start 2 threads, each using different ports. Each thread will serve a different purpose.  
_Called by_: `tcp.py` -> `do_tcp(data_dir, tcp_port, connection_address)`  
_Return_: N/A
#### The 1st thread will be the port that the TCP server will use to listen to the pi and its requests. (..... = omitted code)  
```python
 def start(self):
        try:
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            self.tcp_socket.bind((self.connection_address, self.tcp_port))
            self.tcp_socket.listen()
            .....
            tcp_thread = Thread(target=self.tcp_server_start, name="tcp_thread")
            self.threads.append(tcp_thread)
            tcp_thread.start()
            .....
        except KeyboardInterrupt:
            self.tcp_socket.close()
            self.tcp_file_socket.close()
```
This thread will have its own functions to call on: `tcp_server_start(self)` and `__process_requests(self, client_socket, client_addr)`  
Note that the port used is the TCP port given by `piman.py`.  
#### The 2nd thread will be the port that the TCP server will use to transfer `rootfs.tgz` to the pi. (..... = omitted code)  
```python
 def start(self):
        try:
            .....
            self.tcp_file_socket = socket(AF_INET, SOCK_STREAM)
            self.tcp_file_socket.bind((self.connection_address, 4444))
            self.tcp_file_socket.listen()
            .....
            tcp_file_thread = Thread(target=self.tcp_file_start, name="tcp_file_thread")
            self.threads.append(tcp_file_thread)
            tcp_file_thread.start()
        except KeyboardInterrupt:
            self.tcp_socket.close()
            self.tcp_file_socket.close()
```
This thread will have its own functions to call on: `tcp_server_start(self)` and `__transfer_file(self, client_socket)`  
Note that the port used is a hardcoded port.  

### Function: tcp_server_start(self)
_Description_: This will start the TCP server thread that will service the pi's requests.  
_Called by_: `tcp.py` -> `start(self)`  
_Return_: N/A
```python
def tcp_server_start(self):
        try:
            while True:
                (client_socket, client_addr) = self.tcp_socket.accept()
                tcp_thread = Thread(target=self.__process_requests, args=[client_socket, client_addr], name="tcp_client_thread")
                self.threads.append(tcp_thread)
                tcp_thread.start()
        except KeyboardInterrupt:
            self.tcp_socket.close()
```
The actual function that services requests: `__process_requests(self, client_socket, client_addr)` will be called on by this function.  

### Function: __process_requests(self, client_socket, client_addr)
_Description_: This function dictates how requests from the pi are handled.  
_Called by_: `tcp.py` -> `tcp_server_start(self)`  
_Return_: N/A

| Type | Variable | Description |
|-------|-------|-------|
|String |client_socket |the port that the client is using |
|String |client_addr | the address of the client |

These parameters were already defined and assigned in tcp_server_start(self):
```python
(client_socket, client_addr) = self.tcp_socket.accept()
tcp_thread = Thread(target=self.__process_requests, args=[client_socket, client_addr], name="tcp_client_thread")
```
The 1st part of the function will set up the way the server will receive and read messages from the pi:
```python
 def __process_requests(self, client_socket, client_addr):
        with open('tcp/reinstall.txt', 'r') as f:
            client_addrs = f.readline()
        try:
            print("serving client from: {}".format(client_addr))    
            c = client_socket.makefile()
            req = c.readline()
```
The variable `req` will define whatever request the pi sends to the TCP server.  
There are 3 messages that `req` can be, and therefore there are 3 __supported requests__ which were defined at the beginning of `tcp.py`  
```python
RECV_IS_INSTALLED = "IS_INSTALLED\n"
RECV_IS_UNINSTALLED = "IS_UNINSTALLED\n"
RECV_IS_FORMATTED =  "IS_FORMATTED\n"
```
The responses that the TCP server will send back to the pi are also defined at the beginning of `tcp.py`  
```python
SEND_BOOT = b"boot\n" + b"EOM\n"
SEND_FORMAT = b"format\n" + b"EOM\n"
```
The main part of the function dictates what the TCP server will send back to the pi based on what `req` is:
```python
            while req:    
                print("TCP - recieved request {}".format(req))
                if req == RECV_IS_UNINSTALLED:    
                    print("TCP - uninstalled, sending format")
                    client_socket.send(SEND_FORMAT)
                elif req == RECV_IS_INSTALLED:
                   print(client_addr[0])
                   print('on install: '  + client_addrs)
                   if client_addr[0] == client_addrs:
                        print("TCP - need to reinstall, sending format")
                        client_socket.send(SEND_FORMAT)
                   else:
                        print("TCP - installed, sending boot")
                        client_socket.send(SEND_BOOT)        
                elif req == RECV_IS_FORMATTED:
                    print("TCP - is formatted, sending file")
                    break
                else:
                    print("TCP - not supported request")
                req = c.readline()
```
#### The most important case is elif req == RECV_IS_INSTALLED
Why? Because if the code detects that the pi is installed, then it can begin transferring `rootfs.tgz` to the pi.  

### Function: tcp_file_start(self)
_Description_: This will start the TCP thread that will transfer `rootfs.tgz` to the pi.  
_Called by_: `tcp.py` -> `start(self)`  
_Return_: N/A
```python
def tcp_file_start(self):
        try:
            while True:
                (client_socket, client_addr) = self.tcp_file_socket.accept()
                tcp_file_thread = Thread(target=self.__transfer_file, args=[client_socket], name="tcp_client_file_thread")
                self.threads.append(tcp_file_thread)
                tcp_file_thread.start()
        except KeyboardInterrupt:
            self.tcp_file_socket.close()
```
The actual function that will transfer the `rootfs.tgz` file: `__transfer_file(self, client_socket)` will be called on by this function.  
Like `tcp_server_start`, the `client_socket` parameter in `__transfer_file(self, client_socket)` is defined and assigned in `tcp_file_start(self)`:  
```python
(client_socket, client_addr) = self.tcp_file_socket.accept()
tcp_file_thread = Thread(target=self.__transfer_file, args=[client_socket], name="tcp_client_file_thread")
```

### Function: __transfer_file(self, client_socket)
_Description_: This function sends `rootfs.tgz` to the pi connected at `client_socket`.  
_Called by_: `tcp.py` -> `tcp_file_start(self)`  
_Return_: N/A  

| Type | Variable | Description |
|-------|-------|-------|
|String |client_socket |the port that the client is using |

```python
def __transfer_file(self, client_socket):
        print("TCP - started file_transferring")
        try:
            # opens the specified file in a read only binary form
            transfer_file = open("{}/{}".format(self.data_dir, "rootfs.tgz"), "rb")
            data = transfer_file.read()
            print("TCP - read rootfs.tgz")

            if data:
                # send the data
                print("TCP - sending rootfs.tgz")
                client_socket.send(data)
                print("TCP - finished sending rootfs.tgz")
        except:
            traceback.print_exc()

        print("TCP - finished file_transferring")
        client_socket.close()
```

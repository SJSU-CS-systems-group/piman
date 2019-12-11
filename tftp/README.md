# TFTP

## Navigation
[What is tftp.py](##What-is-tftp.py?)   
[Why tftp.py is designed like this](##What-tftp.py-is-designed-like-this?)   
[How does tftp.py work?](##How-does-tftp.py-work?)   
[Classes and Functions Definitions](##Classes-and-Functions-Definitions)   
*Unfortunately, BitBucket has not fixed header-linking in the README's. Please use `Ctrl + F` to find things in here.*    

## What is tftp.py?
TFTP stands for trivial file transfer protocol. Assuming the file is meant to transfer all the required boot files, located in `build/install` (this directory is only created when you run `make_zipapp.sh`) or located in `install` (not recommended), to the Raspberry pi and starts ***upon execution*** of `build/piman.app/__main__.py` or `piman.py`. Once the TFTP server starts, the TFTP server will wait for a connection on the Pi Manager's IP on port 69 which is set in the `.env` file and the `config.py` located in the root directory.

## Why tftp.py is designed like this?
Fortunately, this is more straightforward then the `dhcp/dhcp.py`. Originally, the TFTP used the same port for listening and for sending which proved to be inefficient. The new tftp is designed to create another ephemeral port to send out the file to the Pi's address and port instead of using the default port that has been assigned in `config.py`. You will notice that the Pi will request for files that are not necessary, therefore, we send an error packet instead to skip over that file and continue sending the other files the Pi requests.
## How does tftp.py work?    
As a brief summary, the TFTP will start a thread to listen on the set TFTP port. Once a packet has been received, TFTP will create another socket that will send bytes of data to the requester's port and address of the requested file. After it has finished sending, it will close the ephemeral port and socket.    
Everything below will detail how each function works according to class and it's functionalities. It is ***highly recommended*** that you step through the code to see how it works and immediately ask for clarification for what everything does since the documentation may not be concise in definition. If you would like to see the packets being sent "live", we recommend executing this command below in a separate terminal to monitor the network. Please refer to the [manpages](https://linux.die.net/man/8/tcpdump) for more uses.    
```tcpdump -i ens4```

We are executing this command assuming that you have the following pre-conditions:

1. That you are logged into the Pi Manager's Virtual Machine (VM) via `ssh`.
2. You are using the *bash shell* to execute these commands.
3. We are assuming that `ens4` is the switch's (the switch that contains all the RPi's) IP address. Otherwise, change accordingly in `.env` file. If you do not see the switch's IP address please inform your supervisor. Execute this following command in the VM to verify:            
```ifconfig```
## Classes and Functions Definitions    
---
This is how the following documentation will be formatted:
```
Class
Function In Class
1. Brief description
2. Called by whom
3. Return values
4. Related Classes and functions
5. Code block (Only Global / Public Functions)
```    
### **Global / Public Functions **
#### Function: do_tftpd(date_dir, connection_address, tftp_port)
*Description*:   
Initializes the TFTP server name with the location of the install directory, the TFTP port, and the address of the TFTP server. 

*Called by*: None         
*Return*: None         

| Type | Variable | Description |
|-------|-------|-------|
| String | data_dir | Location of the boot directory with the boot files |
| Integer | tftp_port | Port to receive data from the Pi |
| String | connection_address | Address of the Pi Manager |

Related Classes and functions: [TFTPServer](###TftpServer)     

```python
def do_tftpd(data_dir, connection_address, tftp_port):
    """ this is a simple TFTP server that will listen on the specified
        port and serve data rooted at the specified data. only read
        requests are supported for security reasons.
    """
    print("Starting TFTP...")
    srvr = TFTPServer(data_dir, tftp_port, connection_address)
    srvr.start()
    srvr.join()
    print("TFTP is terminating")
```
---
### TFTPServer
#### Function: __init__(self,data_dir,tftp_port, connection_address)    
*Description*:   
Initializes the TFTP server name with the location of the install directory, the TFTP port, and the address of the TFTP server. 

*Called by*:    
`tftp.py` -> `TFTPServer` -> `do_tftpd(data_dir, connection_address, tftp_port)`   

*Return*: None         

| Type | Variable | Description |
|-------|-------|-------|
| String | data_dir | Location of the boot directory with the boot files |
| Integer | tftp_port | Port to receive data from the Pi |
| String | connection_address | Address of the Pi Manager |

Related Classes and functions: [TFTPServer.start()](####Function:-start(self))     

#### Function: res_open(self,name)    
*Description*:   
TFTP will look inside the `/build/install/boot` for the the file named in the parameter and return a file handler for the thread.      

*Called by*:    
`tftp.py` -> `TFTPServer` -> `__process_requests(self)`   

*Return*: (File Descriptor/File handle) fd         

| Type | Variable | Description |
|-------|-------|-------|
| String | name | Name of the file requested by the Pi |

Related Classes and functions: [TFTPServer.start()](####Function:-start(self)), [TFTPServer.__process_requests()](####Function:-__process_requests(self))     


#### Function: start(self)    
*Description*:   
Starts the TFTP server with a socket that sends UDP packets. It will bind to port 69, or whatever port you have set in `config.py` to listen to the Pi's request in `__process_requests(self)`.

*Called by*:    
`tftp.py` -> `TFTPServer` -> `do_tftpd(data_dir, connection_address, tftp_port)`   

*Return*: None         

Related Classes and functions: [TFTPServer.start()](####Function:-start(self))     


#### Function: __process_requests(self)    
*Description*:   
Listens to the TFTP server's socket for incoming requests. Once a request has been receieved, it creates a new thread with the target function of __process_client_requests. The actual request is
processed in that function while __process_requests continues listening to incoming requests.     

*Called by*:    
`tftp.py` -> `TFTPServer` -> `start(self)`   

*Return*: None         

Related Classes and functions: [TFTPServer.start()](####Function:-start(self)), [TFTPServer.res_open(self, name)](####Function:-res_open(self,name)), [TFTPServer.__process_client_requests(self, pkt, addr)](####Function:__process_client_requests(self,pkt,addr))     

#### Function: __process_client_requests(self)    
*Description*:   
Creates a new UDP socket with an ephemeral port for communication to a client's request. This function will then listen for requests on the new ephemeral port (selected by binding to 0). This function will read the opcode and begin to pack data to prepare for transfer. It will open the file that specified by the packet and read 512 bytes of data at a time and send.
If there is data the block number will be increase by 1 and the block number will be saved for the loop in case there are files greater than 512 bytes. If the files are bigger than 512 bytes, it will continuously loop to send all the bytes to the Pi. If anywhere in the steps the file is not found, an error packet will be sent to the Pi. After there is no more data to send, the ephemeral port will close and the function will terminate.

*Called by*:    
`tftp.py` -> `TFTPServer` -> `__process_requests(self)`   

*Return*: None         

Related Classes and functions: [TFTPServer.start()](####Function:-start(self)), [TFTPServer.res_open(self, name)](####Function:-res_open(self,name)), [TFTPServer.__process_requests(self)](####Function:__process_requests(self))     

#### Function: join(self)    
*Description*:   
Waits for the tftp thread to end its process and return back to the main thread.

*Called by*:    
`tftp.py` -> `do_tftpd(data_dir, connection_address, tftp_port)`   

*Return*: None         

Related Classes and functions: [TFTPServer.start()](####Function:-start(self))     
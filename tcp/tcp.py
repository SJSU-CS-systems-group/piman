from threading import Thread
from socket import AF_INET, SOCK_STREAM, socket
from struct import unpack, pack
import traceback
from piman import logger

RECV_IS_INSTALLED = "IS_INSTALLED"
RECV_IS_UNINSTALLED = "IS_UNINSTALLED"
RECV_IS_FORMATTED =  "IS_FORMATTED"

# message sent to PI
SEND_BOOT = b"boot\n" + b"EOM\n"
SEND_FORMAT = b"format\n" + b"EOM\n"

class TCPServer:
    """
    TCPServer creates two TCP sockets, control and file socket.
    The control socket is used to serve control command, such as INSTALLED, NEED FILE
    The file socket is used to transfer to root file to the pis
    """
    def __init__(self, data_dir, tcp_port, connection_address):
        self.data_dir = data_dir
        self.tcp_port = tcp_port
        self.connection_address = connection_address
        self.threads = []


    def start(self):
        """
        This function starts the control and file socket by creating one thread for each
        """
        try:
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            self.tcp_socket.bind((self.connection_address, self.tcp_port))
            self.tcp_socket.listen()

            self.tcp_file_socket = socket(AF_INET, SOCK_STREAM)
            self.tcp_file_socket.bind((self.connection_address, 4444))
            self.tcp_file_socket.listen()

            tcp_thread = Thread(target=self.tcp_server_start, name="tcp_thread")
            self.threads.append(tcp_thread)
            tcp_thread.start()

            tcp_file_thread = Thread(target=self.tcp_file_start, name="tcp_file_thread")
            self.threads.append(tcp_file_thread)
            tcp_file_thread.start()

        except KeyboardInterrupt:
            self.tcp_socket.close()
            self.tcp_file_socket.close()


    def tcp_server_start(self):
        """
        This function serves the control socket. The thread will call this function.
        """
        try:
            while True:
                (client_socket, client_addr) = self.tcp_socket.accept()
                tcp_thread = Thread(target=self.__process_requests, args=[client_socket, client_addr], name="tcp_client_thread")
                self.threads.append(tcp_thread)
                tcp_thread.start()
        except KeyboardInterrupt:
            self.tcp_socket.close()

    
    def tcp_file_start(self):
        """
        This function serves the file socket. The thread will call this function.
        """
        try:
            while True:
                (client_socket, client_addr) = self.tcp_file_socket.accept()
                tcp_file_thread = Thread(target=self.__transfer_file, args=[client_socket], name="tcp_client_file_thread")
                self.threads.append(tcp_file_thread)
                tcp_file_thread.start()
        except KeyboardInterrupt:
            self.tcp_file_socket.close()


    def __process_requests(self, client_socket, client_addr):
        """
        This function serves the control socket's coming requests.
        """
        try:
            logger.warning("serving client from: {}".format(client_addr))    
            fd = client_socket.makefile()
            req = fd.readline()
            while req:    
                req = req.strip()
                logger.debug("TCP - recieved request {}".format(req))
                if req == RECV_IS_UNINSTALLED:
                    logger.warning("TCT - uninstalled, sending format")
                    client_socket.send(SEND_FORMAT) #  this line of code is suggested by team fire
                elif req == RECV_IS_INSTALLED:
                    if client_addr[0] in []:
                        logger.warning("TCP - need to reinstall, sending format")
                        client_socket.send(SEND_FORMAT)
                    else:
                        logger.warning("TCP - installed, sending boot")
                        client_socket.send(SEND_BOOT)        
                elif req == RECV_IS_FORMATTED:
                    logger.warning("TCP - is formatted, sending file")
                    break
                else:
                    pass
                    #print("TCP - not supported request")
                req = fd.readline()
        except:
            logger.debug(traceback.print_exc())
        client_socket.close()


    def __transfer_file(self, client_socket):
        """
        This function serves the file socket's coming requests.
        """
        logger.warning("TCP - started file_transferring")
        try:
            # opens the specified file in a read only binary form
            transfer_file = open("{}/{}".format(self.data_dir, "rootfs.tgz"), "rb")
            data = transfer_file.read()
            logger.debug("TCP - read rootfs.tgz")

            if data:
                # send the data
                logger.debug("TCP - sending rootfs.tgz")
                client_socket.send(data)
                logger.debug("TCP - finished sending rootfs.tgz")
        except:
            logger.error(traceback.print_exc())

        logger.warning("TCP - finished file_transferring")
        client_socket.close()


    def join(self):
        for thread in self.threads:
            thread.join()

def do_tcp(data_dir, tcp_port, connection_address):
    """ this is a simple TCP server that will listen on the specified
        port and serve data rooted at the specified data. only read
        requests are supported for security reasons.
    """
    logger.warning("tcp running...")
    srvr = TCPServer(data_dir, tcp_port, connection_address)
    srvr.start()
    srvr.join()
    

if __name__ == "__main__":
    do_tcp(".", 3333, "127.0.0.1")

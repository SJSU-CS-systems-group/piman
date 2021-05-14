from threading import Thread
from socket import AF_INET, SOCK_STREAM, socket
from struct import unpack, pack
import traceback
from piman import logger
from datetime import datetime

RECV_IS_INSTALLED = "IS_INSTALLED"
RECV_IS_UNINSTALLED = "IS_UNINSTALLED"
RECV_IS_FORMATTED = "IS_FORMATTED"
RECV_RECEIVED_DATE = "RECEIVED_DATE"
RECV_SET_DATE = "SET_DATE"
RECVD_MOUNTING = "MOUNTING"
RECVD_MOUNTED = "FINISHED_MOUNTING"
RECVD_UNMOUNTING = "UNMOUNTING"
RECVD_UNMOUNTED = "FINISHED_UNMOUNTING"
RECVD_BOOT = "RECEIVED_BOOT"
RECVD_FORMAT = "RECEIVED_FORMAT"
RECVD_REINSTALL = "RECEIVED_REINSTALL"

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

            tcp_thread = Thread(
                target=self.tcp_server_start, name="tcp_thread")
            self.threads.append(tcp_thread)
            tcp_thread.start()

            tcp_file_thread = Thread(
                target=self.tcp_file_start, name="tcp_file_thread")
            self.threads.append(tcp_file_thread)
            tcp_file_thread.start()

        except KeyboardInterrupt:
            logger.exception("keyboard interrupt")
            self.tcp_socket.close()
            self.tcp_file_socket.close()

    def tcp_server_start(self):
        """
        This function serves the control socket. The thread will call this function.
        """
        try:
            while True:
                (client_socket, client_addr) = self.tcp_socket.accept()
                tcp_thread = Thread(target=self.__process_requests, args=[
                                    client_socket, client_addr], name="tcp_client_thread")
                self.threads.append(tcp_thread)
                tcp_thread.start()
        except KeyboardInterrupt:
            logger.exception("keyboard interrupt")
            self.tcp_socket.close()

    def tcp_file_start(self):
        """
        This function serves the file socket. The thread will call this function.
        """
        try:
            while True:
                (client_socket, client_addr) = self.tcp_file_socket.accept()
                tcp_file_thread = Thread(target=self.__transfer_file, args=[
                                         client_socket], name="tcp_client_file_thread")
                self.threads.append(tcp_file_thread)
                tcp_file_thread.start()
        except KeyboardInterrupt:
            logger.exception("keyboard interrupt")
            self.tcp_file_socket.close()

    def __process_requests(self, client_socket, client_addr):
        """
        This function serves the control socket's coming requests.
        """
        reinstall_file = list()
        with open('reinstall.txt', "r+") as fp:
            reinstall_file = fp.read()
            fp.seek(0)
            fp.truncate(0)
        try:
            logger.info("serving client from: {}".format(client_addr))
            fd = client_socket.makefile()
            date = datetime.now()
            dt_string = date.strftime('%Y%m%d%H%M.%S')
            dt_string = 'busybox date -s ' + dt_string + "\n" + "EOM\n"
            req_dict = {   # this dict is used only when the received command results in logging only
                RECV_RECEIVED_DATE: lambda: logger.info("TCP - pi successfully received date string"),
                RECV_SET_DATE: lambda: logger.info("TCP - pi successfully set local datetime"),
                RECVD_MOUNTING: lambda: logger.info("TCP - pi mounting has started"),
                RECVD_MOUNTED: lambda: logger.info("TCP - pi successfully mounted filesystem"),
                RECVD_UNMOUNTING: lambda: logger.info("TCP - pi unmounting has started"),
                RECVD_UNMOUNTED: lambda: logger.info("TCP - pi successfully unmounted filesystem"),
                RECVD_BOOT: lambda: logger.info("TCP - pi successfully received boot command"),
                RECVD_FORMAT: lambda: logger.info("TCP - pi successfully received format command"),
                RECVD_REINSTALL: lambda: logger.info("TCP - pi successfully received reinstall command")
            }
            print("Sending date command to pi:", dt_string)
            client_socket.send(dt_string.encode())
            req = fd.readline()
            while req:
                req = req.strip()
                if req == RECV_IS_UNINSTALLED:
                    logger.info("TCT - uninstalled, sending format")
                    # this line of code is suggested by team fire
                    client_socket.send(SEND_FORMAT)
                elif req == RECV_IS_INSTALLED:
                    if client_addr[0] in reinstall_file:
                        logger.info("TCP - need to reinstall, sending format")
                        client_socket.send(SEND_FORMAT)
                    else:
                        logger.info("TCP - installed, sending boot")
                        client_socket.send(SEND_BOOT)
                elif req == RECV_IS_FORMATTED:
                    logger.info("TCP - is formatted, sending file")
                    break
                else:
                    if req in req_dict:
                        req_dict[req]() # log changed state if command is valid and not handled above
                    else:
                        logger.info("TCP - unsupported request: {}".format(req)) # otherwise log unsupported command
                req = fd.readline()
        except:
            logger.error(traceback.print_exc())
        logger.info("tcpdump")
        client_socket.close()

    def __transfer_file(self, client_socket):
        """
        This function serves the file socket's coming requests.
        """
        logger.info("TCP - started file_transferring")
        try:
            # opens the specified file in a read only binary form
            transfer_file = open(
                "{}/{}".format(self.data_dir, "rootfs.tgz"), "rb")
            data = transfer_file.read()
            logger.debug("TCP - read rootfs.tgz")

            if data:
                # send the data
                logger.debug("TCP - sending rootfs.tgz")
                client_socket.send(data)
                logger.debug("TCP - finished sending rootfs.tgz")
        except:
            logger.error(traceback.print_exc())

        logger.info("TCP - finished file_transferring")
        client_socket.close()
        transfer_file.close()
        
    def join(self):
        for thread in self.threads:
            thread.join()


def do_tcp(data_dir, tcp_port, connection_address):
    """ this is a simple TCP server that will listen on the specified
        port and serve data rooted at the specified data. only read
        requests are supported for security reasons.
    """
    logger.info("tcp running...")
    srvr = TCPServer(data_dir, tcp_port, connection_address)
    srvr.start()
    srvr.join()


if __name__ == "__main__":
    do_tcp(".", 3333, "127.0.0.1")

'''
-*- coding: utf-8 -*-
@Author  : LiZhichao
@Time    : 2019/8/12 19:24
@Software: PyCharm
@File    : server.py
'''
from socket import *
import signal
import time
import os
import sys

#确定文件库位置
File_Path = "/home/tarena/pythonweb"

class TftpServer(object):
    def __init__(self,connfd):
        self.connfd = connfd

    def do_list(self):
        filelist = os.listdir(File_Path)
        if not filelist:
            self.connfd.send(b'N')
            return
        else:
            self.connfd.send(b'Y')
        time.sleep(0.1)
        files = ""
        for filename in filelist:
            if filename[0] != '.' and os.path.isfile(File_Path +
                                                             filename):#判断文件是否是普通文件
                files = files + filename + "#"
        self.connfd.send(files.encode())

    def do_get(self,filename):
        try:
            fd = open(File_Path + filename,'rb')
        except:
            self.connfd.send(b'N')
            return
        self.connfd.send(b'Y')
        time.sleep(0.1)
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)
        fd.close()
        print("发送文件成功")

    def do_put(self,filename):
        try:
            fd = open(File_Path + filename,'wb')
        except:
            self.connfd.send(b'N')
            return
        self.connfd.send(b'Y')
        while True:
            data = self.connfd.recv(1024).decode()
            if data == '##':
                break
            fd.write(data)
        fd.close()
        print("接收文件完毕")

    def do_quit(self):
        print("客户端退出")
        sys.exit(0)

def main():
    # if len(sys.argv) < 3:
    #     print("argv is error")
    #     sys.exit(1)
    # Host = sys.argv[1]
    # Port = int(sys.argv[2])
    # Addr = (Host,Port)
    Host = ""
    Port = 8888
    Addr = (Host,Port)
    Buffersize = 1024

    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(Addr)
    s.listen(5)
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit(0)
        except Exception:
            continue
        print("客户端登录:",addr)

        pid =os.fork()
        if pid < 0:
            print("创建子进程失败")
            c.close()
            continue
        elif pid == 0:
            s.close()
            print("客户端链接")
            #创建客户端通信对象
            tftp = TftpServer(c)
            while True:
                #接收客户端请求类型
                data = c.recv(Buffersize).decode()
                if data[0] == 'L':
                    tftp.do_list()
                elif data[0] == 'G':
                    filename = data.split(' ')[-1]
                    tftp.do_get(filename)
                elif data[0] == 'P':
                    filename = data.split(' ')[-1]
                    tftp.do_put(filename)
                elif data[0] == 'Q':
                    tftp.do_quit()
        else:
            c.close()
            continue

if __name__ == '__main__':
    main()



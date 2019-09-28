'''
-*- coding: utf-8 -*-
@Author  : LiZhichao
@Time    : 2019/8/12 19:24
@Software: PyCharm
@File    : client.py
'''
from socket import *
import sys
import time

class TftpClient(object):
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')#发送请求类型

        #服务器回复Y/N
        data = self.sockfd.recv(1024).decode()
        if data == 'Y':
            data = self.sockfd.recv(4096).decode()
            files = data.split("#")
            for file in files:
                print(file)
            print("文件列表展示完毕")
        else:
            print("请求文件列表失败")

    #下载
    def do_get(self,filename):
        self.sockfd.send(("G " + filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'Y':
            fd = open(filename,'wb')
            while True:
                data = self.sockfd.recv(1024).decode()
                if data == '##':
                    break
                fd.write(data)
            fd.close()
            print("%s下载完成"%filename)

        else:
            print("下载文件失败")


    def do_put(self,filename):
        try:
            fd = open(filename,'rb')
        except:
            print("上传文件不存在")
            return
        self.sockfd.send(("P "+ filename).encode())
        data = self.sockfd.recv(4096).decode()
        if data == 'Y':
            while True:
                data = fd.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
            print("上传%s完成"%filename)
        else:
            print("上传文件失败")

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
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
    Addr = (Host, Port)
    Buffersize = 1024

    sockfd = socket()
    sockfd.connect(Addr)

    #创建客户端请求对象
    tftp = TftpClient(sockfd)

    while True:
        print("==========命令选项==========")
        print("************List************")
        print("**********Get File**********")
        print("**********Put File**********")
        print("************Quit************")
        print("============================")
        data = input("请输入命令>>")
        if data.strip() == "List":
            tftp.do_list()
        elif data[:3] == "Get":
            filename = data.split(' ')[-1]
            tftp.do_get(filename)
        elif data[:3] == "Put":
            filename = data.split(' ')[-1]
            tftp.do_put(filename)
        elif data.strip() == "Quit":
            tftp.do_quit()
        else:
            print("请输入正确的命令！！！")


        sockfd.send()
        connfd,addr = sockfd.accept()
        data = connfd.recv(1024)
    sockfd.close()


if __name__ == '__main__':
    main()

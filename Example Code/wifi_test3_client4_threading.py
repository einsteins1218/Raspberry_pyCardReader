from socket import *
import threading
import time


def send(sock):
    while True:
        sendData = input('>>>')
        sock.send(sendData.encode('utf-8'))


def receive(sock):
    while True:
        recvData = sock.recv(1024)
        if(recvData.decode('utf-8') == '-1'):
          # server 가 -1 을 주면 연결 종료라고 가정
          break
        print('receive >> ', recvData.decode('utf-8'))

#소캣통신 연결로 설정
port = 1471
host = '192.168.11.165'
clientSock = socket(AF_INET, SOCK_STREAM)


try:
  #소캣통신 연결
  clientSock.connect((host, port))
#쓰레드 사용지정
  sender = threading.Thread(target=send, args=(clientSock,))
  receiver = threading.Thread(target=receive, args=(clientSock,))
#쓰레드 시작
  sender.start()
  receiver.start()

  while True:
    time.sleep(1)
    pass

finally:
  clientSock.close()




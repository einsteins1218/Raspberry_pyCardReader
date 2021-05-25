# https://nalara12200.tistory.com/153 참고
# https://blog.naver.com/PostView.nhn?blogId=kkrdiamond77&logNo=221276401746&categoryNo=68&parentCategoryNo=0&viewDate=&currentPage=1&postListTopCurrentPage=1&from=postView
# https://nowonbun.tistory.com/668
# 쓰레드
# https://m.blog.naver.com/PostView.naver?blogId=kkrdiamond77&logNo=221276401746&proxyReferer=https:%2F%2Fwww.google.com%2F
'''
  메시지를 추상화한 클래스.

  MESSAGE VERSION 1 -----
  
  1. STX - CMD - MSG - ETX
    1byte  2byte 8byte 1byte
  
  STX : 0x02 메시지의 시작을 알림
  CMD = GPIO 제어 방식 선택
  MSG = Output 핀 제어 Mask
  ETX : 0x03, 고정 값,메시지 끝을 알림

'''
import socket
import threading
import struct
import time

SOCK_VERSION = 1

if SOCK_VERSION == 1:
	#문자열 포맷1
	SOCK_STX = 0x02
	SOCK_ETX = 0x03
	

class SockMsgRecvThread(threading.Thread, QObject):

	if SOCK_VERSION == 1:
		STATE_STX = 0			# STX 수신 대기중.
		STATE_CMD = 1		    # STX을 수신했고, CMD 수신 중
		STATE_MSG = 2			# CMD을 수신했고, MSG 수신 중
		STATE_ETX = 3			# MSG을 수신했고, ETX 수신 대기중

	# QR 및 링크를 정상적으로 읽어냈다면, GUI로 알리기 위한 기능 emit()하면 데이터를 보낼 수 있음
	recv_cplt = pyqtSignal(str, str)

    def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.recv_cmd = ''
		self.recv_msg = ''
		
		if SOCK_VERSION == 1:
			self.state = self.STATE_STX
		
	def run(self):
		self.running = True
		
		while self.running:
		
			if SOCK_VERSION == 1:
			
				packet = self.socket.recv(1024)
				data = packet.decode('utf-8')
				
				if len(data) == 12: # 1 + 2 + 8 + 1 <- 패킷 길이 안맞으면 처리 안함
					for i in range(len(data)):
						if self.state == self.STATE_STX: # STX 수신 대기
						
							if data[i] == SOCK_STX:
								self.state = STATE_CMD
							else
								break
							
						elif self.state == self.STATE_CMD: # CMD 메시지 수신 상태
						
							self.recv_cmd += data[i]
							if len(self.recv_cmd) == 2:
								self.state = STATE_MSG
						
						elif self.state == self.STATE_MSG:
						
							self.recv_msg += data[i]
							if len(self.recv_msg) == 8:
								self.state = STATE_ETX
								
						elif self.state == self.STATE_ETX:
						
								if data[i] == SOCK_ETX:
									self.recv_cplt.emit(self.recv_cmd, self.recv_msg)
									print('recv cmd :', self.recv_cmd)
									print('recv msg :', self.recv_msg)
								else
									break
				
				# 패킷 종료, 스테이터스 초기화
				self.state = self.STATE_STX
				self.recv_cmd = ''
				self.recv_msg = ''

	def Stop(self):
		self.running = False

			
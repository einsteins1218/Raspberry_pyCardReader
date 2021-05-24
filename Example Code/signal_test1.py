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
from PyQt5.QtCore import *

class SockMsgRecvThread(threading.Thread, QObject):

	# QR 및 링크를 정상적으로 읽어냈다면, GUI로 알리기 위한 기능 emit()하면 데이터를 보낼 수 있음
	recv_cplt = pyqtSignal(str)

	def __init__(self, data):
		threading.Thread.__init__(self)
		QObject.__init__(self)
		self.data = data

		
	def run(self):
		self.running = True
		
		while self.running:
			time.sleep(1)
			self.recv_cplt.emit(self.data)
			print(self.data)

	def Stop(self):
		self.running = False
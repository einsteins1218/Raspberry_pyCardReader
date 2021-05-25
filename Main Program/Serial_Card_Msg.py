'''
  메시지를 추상화한 클래스.

  MESSAGE VERSION 1 -----
  
  1. STX - CARD_ID - ETX
  1 byte   ?? byte   1 byte
  
  STX : 0x02, 고정 값,메시지 시작을 알림
  CARD_ID = 카드 아이디
  ETX : 0x03, 고정 값,메시지 끝을 알림
  -----------------------
  
  2. CARD_ID - END1 - END2
  ?? byte   1 byte   1 byte
  
  CARD_ID = 카드 아이디
  END1 : '\r' 문자, 메시지 끝을 알림
  END2 : '\n' 문자, 메시지 끝을 알림


'''

import threading
import struct
import time

SERIAL_VERSION = 1

if SERIAL_VERSION == 1:
	#문자열 포맷1
	SERIAL_STX = 0x02
	SERIAL_ETX = 0x03
	
	#문자열 포맷2, 끝문자 2바이트가 엔터일 경우
	SERIAL_END1 = ord("\r") # 대응하는 문자를 ASCII로 바꿈, 반대의 경우는 chr(13)
	SERIAL_END2 = ord("\n") # 대응하는 문자를 ASCII로 바꿈, 반대의 경우는 chr(10)



class M4MsgSender():

	def __init__(self, port):
		self.port = port
		
	def DbgPrintPacket(self, packet):

		print('\nSend len = %d' % len(packet))
		for c in packet:
			print('  0x%02X' % (c))
		print('\n')


# serial port에 listen하고있는 thread
class CardMsgRecvThread(threading.Thread, QObject):
	if SERIAL_VERSION == 1:
		STATE_IDLE = 0				  # 대기중. STX 또는 CARD_ID 수신 대기중.
		STATE_ETX_CARD_ID = 1		   # STX을 수신했고, ETX 수신할 때 까지 CARD_ID 수신 중
		STATE_END1_CARD_ID = 2			# END1 수신할 때 까지 CARD_ID 수신 중
		STATE_END2_CARD_ID = 3			# END2 수신 대기 중

	# 카드 ID을 정상적으로 읽어냈다면, GUI로 알리기 위한 기능 emit()하면 데이터를 보낼 수 있음
	recv_cplt = pyqtSignal(int, str)

	def __init__(self, port, index):
		threading.Thread.__init__(self)
		self.port = port
		self.index = index # 쓰레드를 구분하기 위한 ID
		
		if SERIAL_VERSION == 1:
			self.state = self.STATE_IDLE

	def run(self):
	
		self.running = True
		self.recv_buff = ''
		
		while self.running:

			if SERIAL_VERSION == 1:
			
				if self.state == self.STATE_IDLE:
					data = self.port.read(1)		 # 1바이트 읽음
                    data = data.decode()

					if len(data) == 0:
						continue
					elif ord(data) < 0 or ord(data) > 250:
						self.state = self.STATE_IDLE		  # 잘못된 패킷. 버림.
						self.recv_buff = ''
						continue

					if ord(data) == SERIAL_STX:
						self.state = self.STATE_ETX_CARD_ID	# STX 수신 완료, ETX 수신 할 때 까지 CARD ID 읽음
						self.recv_buff = ''
					else:
						self.state = self.STATE_END1_CARD_ID	# STX 수신 없음, END1 수신 할 때 까지 CARD ID 읽음
						self.recv_buff = data
						
				elif self.state == self.STATE_ETX_CARD_ID: 		# STX 수신 완료, ETX 수신 할 때 까지 CARD ID 읽음
					data = self.port.read(1)
                    data = data.decode()                    

					if len(data) == 0:
						continue
					elif ord(data) < 0 or ord(data) > 250:
						self.state = self.STATE_IDLE		  # 잘못된 패킷. 버림.
						self.recv_buff = ''
						continue

					if ord(data[0]) == SERIAL_ETX:
						# ** 수신 완료! GUI로 CARD ID 수신되었음을 알림, 처음 STATE로 돌아감
						self.recv_cplt.emit(self.index, self.recv_buff)
						print('(recv data) card_id :', self.recv_buff)
						
						self.state = self.STATE_IDLE
						self.recv_buff = ''
						
					else:
						self.recv_buff += data	#CARD_ID 수신 중...
						
						
				elif self.state == self.STATE_END1_CARD_ID:
					data = self.port.read(1)
                    data = data.decode()

					if len(data) == 0:
						continue
					elif ord(data) < 0 or ord(data) > 250:
						self.state = self.STATE_IDLE		  # 잘못된 패킷. 버림.
						self.recv_buff = ''
						continue

					if ord(data[0]) == SERIAL_END1:
						# ** END1 수신 완료! END2 대기 상태로 들어감
						self.state = self.STATE_END2_CARD_ID
						
					else:
						self.recv_buff += data	#CARD_ID 수신 중...
							
							
				elif self.state == self.STATE_END2_CARD_ID:
					data = self.port.read(1)
                    data = data.decode()

					if len(data) == 0:
						continue
					elif ord(data) < 0 or ord(data) > 250:
						self.state = self.STATE_IDLE		  # 잘못된 패킷. 버림.
						self.recv_buff = ''
						continue

					if ord(data[0]) == SERIAL_END2:
						# ** END2 수신 완료! GUI로 CARD ID 수신되었음을 알림, 처음 STATE로 돌아감
						self.recv_cplt.emit(self.index, self.recv_buff)
						print('(recv data) card_id :', self.recv_buff)
						
						self.state = self.STATE_IDLE
						self.recv_buff = ''
						
					else:
						#잘못된 패킷 수신됨. IDLE로 돌아감
						self.state = self.STATE_IDLE
						self.recv_buff = ''



	def Stop(self):
		self.running = False

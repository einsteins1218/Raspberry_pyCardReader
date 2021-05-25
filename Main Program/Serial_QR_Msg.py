# QR 웹 파싱하는 코드 구현 예정
# “처래처@품명@차량번호@입고량” 을 웹 파싱.
# https://docs.python-requests.org/en/master/user/quickstart/

'''
  메시지를 추상화한 클래스.

  MESSAGE VERSION 1 -----

  QR_DATA - END1 - END2
  ?? byte   1 byte   1 byte
  
  QR_DATA = 파싱할 데이터
  END1 : '\r' 문자, 메시지 끝을 알림
  END2 : '\n' 문자, 메시지 끝을 알림

'''

import threading
import struct
import time

SERIAL_VERSION = 1

if SERIAL_VERSION == 1:
	#QR 문자열 포맷, 끝문자 2바이트가 엔터일 경우
	SERIAL_END1 = ord("\r") # 대응하는 문자를 ASCII로 바꿈, 반대의 경우는 chr(13)
	SERIAL_END2 = ord("\n") # 대응하는 문자를 ASCII로 바꿈, 반대의 경우는 chr(10)
	

class QRMsgRecvThread(threading.Thread, QObject):

	if SERIAL_VERSION == 1:
		STATE_END1_QR_ID = 0			# END1 수신할 때 까지 QR Link 데이터 수신 중
		STATE_END2_QR_ID = 1			# END2 수신 대기 중

	# QR 및 링크를 정상적으로 읽어냈다면, GUI로 알리기 위한 기능 emit()하면 데이터를 보낼 수 있음
	recv_cplt = pyqtSignal(int, str, str, str, str)

    def __init__(self, port, index):
		threading.Thread.__init__(self)
		self.port = port
		self.index = index # 쓰레드를 구분하기 위한 ID
		self.recv_buff = ''
		self.results = ['거래처', '품명', '차량번호', '입고량',] # 파싱 결과를 넣기 위한 리스트
		
		if SERIAL_VERSION == 1:
			self.state = self.STATE_END1_QR_ID
		
	def run(self):
		self.running = True
		
		while self.running:
		
			if SERIAL_VERSION == 1:
			
				if self.state == self.STATE_END1_QR_ID: #엔터 수신할 때 까지 데이터 읽음
		
					data = self.port.read(1)
					
					if len(data) == 0:
						continue
					elif len(data) >= 255:
						self.state = self.STATE_END1_QR_ID		  # 잘못된 패킷. 다시 처음부터 받기 시작
						self.recv_buff = ''
						continue
					elif ord(data) < 0 or ord(data) > 250:
						self.state = self.STATE_END1_QR_ID		  # 잘못된 패킷. 다시 처음부터 받기 시작
						self.recv_buff = ''
						continue
						
					if ord(self.recv_buff[0]) == SERIAL_END1:
						self.state = self.STATE_END2_QR_ID	# \r 수신, \n 대기 상태로 돌입
					else:
						self.state = self.STATE_END1_QR_ID	# \r 수신 할 때 까지 QR Link 읽음
						self.recv_buff += data
					
				if self.state == self.STATE_END2_QR_ID: # \n 수신 대기
		
					data = self.port.read(1)		 

					if len(data) == 0:
						continue
					elif len(data) >= 255:
						self.state = self.STATE_END1_QR_ID		  # 잘못된 패킷. 다시 처음부터 받기 시작
						self.recv_buff = ''
						continue
					elif ord(data) < 0 or ord(data) > 250:
						self.state = self.STATE_END1_QR_ID		  # 잘못된 패킷. 다시 처음부터 받기 시작
						self.recv_buff = ''
						continue

					if ord(data[0]) == SERIAL_END2:
						# ** END2 수신 완료! QR로부터 받은 링크를 파싱 및 GUI로 알림
						
						self.parsing_data(self.recv_buff)  # link에 있는 요소 파싱
						
						self.state = self.STATE_END1_QR_ID
						self.recv_buff = ''
						
					else:
						#잘못된 패킷 수신됨. IDLE로 돌아감
						self.state = self.STATE_END1_QR_ID
						self.recv_buff = ''
					

	def Stop(self):
		self.running = False
	
	#url로부터 데이터를 파싱함
	def parsing_data(self, data):
	
        self.results = ['', '', '', '', '', '', '', '', '', '']
        parsing_index = 0
        
        for i in range(len(data)):
            
            if data[i] == '|':
                parsing_index += 1
                
                if parsing_index > 9: # @ 가 4개 이상 들어오면 에러 처리
                    print("QR: Wrong Data")
                    return
            else:
                self.results[parsing_index] += data[i]
                
        if parsing_index == 9: # @가 3개 들어오면, 정상적으로 들어왔음
            #GUI 로 파싱한 데이터 전송
            recv_cplt.emit(self.index, self.results[6], self.results[7], self.results[4], self.results[9])
        
        else:
            print("QR: Wrong Data")
        


			
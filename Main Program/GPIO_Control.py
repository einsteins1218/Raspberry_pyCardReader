import RPi.GPIO as GPIO #GPIO 라이브러리 불러오기
# 설치 안될 경우 "https://m.blog.naver.com/PostView.naver?blogId=simplex245&logNo=220647994727&proxyReferer=https:%2F%2Fwww.google.com%2F"
# 참고.. 윈도우 환경이라 구현만 해두고 안쓸거임, 설치했는데도 IMPORT 안되는 것 같음.

class GPIO_Control():

	GPIOIO_DO = [22,6,13,19,26,11,27,4]
	GPIOIO_DI = [17,12,16,21,20,18,23,24]

	def __init__(self):
	
		#불필요한 WARNING 제거
		GPIO.setwarnings(False)
        
		#GPIO 핀의 번호모드 설정
		GPIO.setmode(GPIO.BCM)
		
		#GPIO_INPUT 핀 설정
		for channel in GPIOIO_DI:
			GPIO.setup([pin_number], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
			
		#GPIO_OUTPUT 핀 설정
		for channel in GPIOIO_DO:
			GPIO.setup([pin_number], GPIO.OUT, initial=GPIO.LOW)

	def gpio_write_pin(channel, pin_state):
		GPIO.output(self.GPIOIO_DO[channel], pin_state)
		
	def gpio_read_pin(channel, pin_state):
		if GPIO.input(self.GPIOIO_DI[channel]) == GPIO.LOW:
			return 0
		else:
			return 1
			
	def gpio_toggle_pin(channel):
		# STM32 에서는 OUTPUT 핀도 읽을 수 있는데, 되는지 확인 필요
		if GPIO.input(self.GPIOIO_DO[channel]) == GPIO.LOW:
			GPIO.output(self.GPIOIO_DO[channel], GPIO.HIGH)
		else:
			GPIO.output(self.GPIOIO_DO[channel], GPIO.LOW)

import RPi.GPIO as GPIO #GPIO 라이브러리 불러오기
import time #시간 라이브러리 불러오기
import datetime

#I/O 리스트로 지정
IO_do = [22,6,13,19,26,11,27,4]
IO_di = [17,12,16,21,20,18,23,24]
#불필요한 WARNING 제거
GPIO.setwarnings(False)

#GPIO 핀의 번호모드 설정
GPIO.setmode(GPIO.BCM)

#버튼 리스트 변수를 INPUT설정,PULLDOWN 저항 설정
for i in IO_di:
    GPIO.setup([i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
#LED 리스트 변수를 OUTPUT설정
for j in IO_do:
    GPIO.setup([j], GPIO.OUT)

#boolean 변수설정
light_ons = [ False for _ in range(8)]

#프로그램 시작을 알림
print("start")

#버튼 콜백 함수를 정의함 글로벌 함수 적용
def button_callback_(ch):
    print(ch)
    global light_ons
    if light_ons[i] == False:
        GPIO.output(IO_do[i], 1)
        print("LED%d ON"%(i+1))
    else:
        GPIO.output(IO_do[i], 0)
        print("LED%d OFF"%(i+1))
    light_ons[i] = not light_ons[i]

# 이벤트 알림 방식 버튼핀의 Rising신호를 감지하면 콜백함수를 실행
# 바운스타임을 설정하여 잘못된 신호를 방지합니다.
for i in Num:
    GPIO.add_event_detect(IO_di[i],GPIO.RISING,callback=button_callback(i), bouncetime=300)

while 1:
    time.sleep(0.1)
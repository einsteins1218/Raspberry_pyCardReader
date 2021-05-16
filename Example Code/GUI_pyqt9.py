import sys, datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import RPi.GPIO as GPIO
import serial
import threading
from PyQt5.QtCore import pyqtSlot, QTimer

led_1 = 5
led_2 = 6

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

GPIO.setup(led_1, GPIO.OUT)
GPIO.setup(led_2, GPIO.OUT)

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout = 1)

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("/home/pi/Desktop/untitled2.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.currentDateTime = datetime.datetime.now()
        self.sigan.setDateTime(self.currentDateTime)
        #타이머에 넣기
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout_run)
        self.timer.timeout.connect(self.timeout_run2)
        self.timer.timeout.connect(self.thread_card1)

        self.Btn1On.clicked.connect(self.button1onFunction)
        self.Btn1Off.clicked.connect(self.button1offFunction)
        self.Btn2On.clicked.connect(self.button2onFunction)
        self.Btn2Off.clicked.connect(self.button2offFunction)

        self.Btn1On.setStyleSheet("border-image:url(/home/pi/Desktop/delete.png);")
        self.Btn1Off.setStyleSheet("border-image:url(/home/pi/Desktop/image.png);")
        
        #self.lblCard1.setText('{}:{}im'.format(self.t2,self.t3))

    def timeout_run2(self):
        currentDateTime = datetime.datetime.now()
        self.sigan.setDateTime(currentDateTime)

    def timeout_run(self):
        current_time = datetime.datetime.now()
        self.sigan2.setText(str(current_time))

    def thread_card1(self):
        response = ser.readline()
        len1 = len(response)
        if len1 <= 30 :
            response1 = response[7:11]
            response2 = response1.decode('utf-8')
        #response3 = int(float(response2))
            self.DisplayCardNo1.append(str(response2))


    '''def thread_card2():
        while 1:
            response1 = ser.readline()
            print(response1)

    t1 = threading.Thread(target=thread_card2)
    t1.start()'''

    def button1onFunction(self) :
        GPIO.output(led_1,1)
        print("LED1 ON")

    def button1offFunction(self) :
        GPIO.output(led_1,0)
        print("LED1 Off")

    def button2onFunction(self) :
        GPIO.output(led_2,1)
        print("LED2 ON")
        self.BtnColor1.setStyleSheet("Color:blue;")

    def button2offFunction(self) :
        GPIO.output(led_2,0)
        print("LED2 Off")
        self.BtnColor1.setStyleSheet("Color:red;")

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()
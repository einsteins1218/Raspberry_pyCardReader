import RPi.GPIO as GPIO 
import time 
import datetime

IO_do = [22,6,13,19,26,11,2,4]
IO_di = [27,12,16,21,20,18,23,24]

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

for i in IO_di:
    GPIO.setup([i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
for j in IO_do:
    GPIO.setup([j], GPIO.OUT)

light_1_on = False
light_2_on = False
light_3_on = False
light_4_on = False
light_5_on = False
light_6_on = False
light_7_on = False
light_8_on = False

print("start")

def button_1_callback(ss):
    global light_1_on
    if light_1_on == False:
        GPIO.output(IO_do[0],1)
        print("LED1 ON")
    else:
        GPIO.output(IO_do[0],0)
        print("LED1 OFF")
    light_1_on = not light_1_on

def button_2_callback(ss):
    global light_2_on
    if light_2_on == False:
        GPIO.output(IO_do[1],1)
        print("LED2 ON")
    else:
        GPIO.output(IO_do[1],0)
        print("LED2 OFF")
    light_2_on = not light_2_on

def button_3_callback(ss):
    global light_3_on
    if light_3_on == False:
        GPIO.output(IO_do[2],1)
        print("LED3 ON")
    else:
        GPIO.output(IO_do[2],0)
        print("LED3 OFF")
    light_3_on = not light_3_on

def button_4_callback(ss):
    global light_4_on
    if light_4_on == False:
        GPIO.output(IO_do[3],1)
        print("LED4 ON")
    else:
        GPIO.output(IO_do[3],0)
        print("LED4 OFF")
    light_4_on = not light_4_on

def button_5_callback(ss):
    global light_5_on
    if light_5_on == False:
        GPIO.output(IO_do[4],1)
        print("LED5 ON")
    else:
        GPIO.output(IO_do[4],0)
        print("LED5 OFF")
    light_5_on = not light_5_on

def button_6_callback(ss):
    global light_6_on
    if light_6_on == False:
        GPIO.output(IO_do[5],1)
        print("LED6 ON")
    else:
        GPIO.output(IO_do[5],0)
        print("LED6 OFF")
    light_6_on = not light_6_on

def button_7_callback(ss):
    global light_7_on
    if light_7_on == False:
        GPIO.output(IO_do[6],1)
        print("LED7 ON")
    else:
        GPIO.output(IO_do[6],0)
        print("LED7 OFF")
    light_7_on = not light_7_on

def button_8_callback(ss):
    global light_8_on
    if light_8_on == False:
        GPIO.output(IO_do[7],1)
        print("LED8 ON")
    else:
        GPIO.output(IO_do[7],0)
        print("LED8 OFF")
    light_8_on = not light_8_on    

GPIO.add_event_detect(IO_di[0],GPIO.RISING,callback=button_1_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[1],GPIO.RISING,callback=button_2_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[2],GPIO.RISING,callback=button_3_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[3],GPIO.RISING,callback=button_4_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[4],GPIO.RISING,callback=button_5_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[5],GPIO.RISING,callback=button_6_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[6],GPIO.RISING,callback=button_7_callback, bouncetime=300)
GPIO.add_event_detect(IO_di[7],GPIO.RISING,callback=button_8_callback, bouncetime=300)

while 1:
    time.sleep(0.1)
    
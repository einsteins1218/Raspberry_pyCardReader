import serial
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout = 1)
#ser.open()
str = bytes('testing'.encode())

try:
    while 1:
        ser.write(str)
        response = ser.readline()
        t3 = len(response)
        if t3 <= 15 :
            print(response)
        print('111',response)
except KeyboardInterrupt:
    ser.close


#str = bytes('this is test'.encode())
#ser.write(bytes(str.encode()))

#while True:
 #   ser.write(str)
  #  s = ser.read(10)
   # if s != '': 
    #    print(s)
   # time.sleep(100)
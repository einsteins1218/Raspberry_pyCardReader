'''
  메시지를 추상화한 클래스.

  MESSAGE VERSION 1 -----
  STX - CMD - MSG - ETX
  1 byte   2 byte   10byte     1 byte

  STX : 0x02, 고정 값,메시지 시작을 알림
  CMD : CMD에 따라 DO을 제어함
  MSG : MSG을 GUI 카드 정보에 출력함
  ETX : 0x03, 고정 값,메시지 끝을 알림



'''

import threading
import struct
import time

SERIAL_VERSION = 1

if SERIAL_VERSION == 1:
	SERIAL_STX = 0x02
	SERIAL_ETX = 0x03
elif SERIAL_VERSION == 2:
    SERIAL_STX = 0x02
	SERIAL_ETX = 0x03

SERIAL_CONTENT_CMD_DO_ALL_ON = 0x10
SERIAL_CONTENT_CMD_DO_ALL_OFF = 0x20
SERIAL_CONTENT_CMD_DO_ONOFF = 0x01



class M4MsgSender():

    def __init__(self, port):
        self.port = port


    def SendPayload(self, payload):
        packet = struct.pack('<BBB', SERIAL_STX, HEADER_VER, len(payload)) + payload
        packet = self.AppendCRC(packet)
        packet += chr(SERIAL_ETX).encode()
        packet = self.ByteStuffing(packet)
        self.DbgPrintPacket(packet)
        if self.port:
            self.port.write(packet)


    def RequestMsg(self, content_CMD):
        payload = struct.pack('<BB', SERIAL_MSG_TYPE_REQUEST, content_CMD)
        self.SendPayload(payload)


    def ReplyMsg(self, content_CMD):
        payload = struct.pack('<BB', SERIAL_MSG_TYPE_RESPONSE, content_CMD)
        self.SendPayload(payload)


    def ReplyHeartbeat(self):
        self.ReplyMsg(SERIAL_CONTENT_CMD_HEARTBEAT)


    def ReadRobotInfo(self):
        self.RequestMsg(SERIAL_CONTENT_CMD_READ_ROBOT_INFO)


    def PowerControl(self, shutdown):
        payload = struct.pack('<BBB', SERIAL_MSG_TYPE_REQUEST, SERIAL_CONTENT_CMD_POWER_CTRL, shutdown)
        self.SendPayload(payload)


    def ReadProximity(self):
        self.RequestMsg(SERIAL_CONTENT_CMD_READ_PROXIMITY)


    def ReadEStopSW(self):
        self.RequestMsg(SERIAL_CONTENT_CMD_READ_ESTOP_SW)


    def ReadBattery(self):
        self.RequestMsg(SERIAL_CONTENT_CMD_READ_BATTERY)


    def ReadWheelPosVel(self):
        self.RequestMsg(SERIAL_CONTENT_CMD_READ_WHEEL_POS_VEL)


    def ReadWheelOdo(self):
        self.RequestMsg(SERIAL_CONTENT_CMD_READ_ODO)


    def SetDriveMode(self, mode):
        payload = struct.pack('<BBB', SERIAL_MSG_TYPE_REQUEST, SERIAL_CONTENT_CMD_SET_DRV_MODE, mode)
        self.SendPayload(payload)
		
    def DbgPrintPacket(self, packet):

        print('\nSend len = %d' % len(packet))
        for c in packet:
            print('  0x%02X' % (c))
        print('\n')






# serial port에 listen하고있는 thread
class M4MsgRecvThread(threading.Thread):
    if SERIAL_VERSION == 1:
        STATE_HEADER1 = 0               # 대기중. header 수신 대기중.
        STATE_HEADER2 = 1               # STX 수신 완료.
        STATE_LENGTH = 2                # CMD 수신됨. length 수신 대기중.
        STATE_PAYLOAD = 3               # length 수신됨. payload 수신중.
        STATE_CRC = 4                   # payload 수신 완료. CRC 대기중
    elif SERIAL_VERSION == 2:
        STATE_CMDLE = 0
        STATE_RECEIVING = 1
        STATE_STUFFING = 2

    def __init__(self, port, cb, f_out=None, timestamp=False, sender=None):
        threading.Thread.__init__(self)
        self.port = port
        self.cb = cb
        if SERIAL_VERSION == 1:
            self.state = self.STATE_HEADER1
        elif SERIAL_VERSION == 2:
            self.state = self.STATE_CMDLE
        self.f_out = f_out
        self.timestamp = timestamp
        self.sender = sender
        print('Log file : ')
        print(f_out)

    def run(self):
        self.running = True
        self.recv_buff = ''
        while self.running:
            #try:
            if SERIAL_VERSION == 1:
                if self.state == self.STATE_HEADER1:
                    self.recv_buff = self.port.read(1)         # 여기서 timeout 까지 waiting...

                    if len(self.recv_buff) == 0:
                        continue

                    #print('+%02X' % (ord(self.recv_buff[0])))
                    if ord(self.recv_buff[0]) == SERIAL_STX:
                        self.state = self.STATE_HEADER2
                elif self.state == self.STATE_HEADER2:
                    data = self.port.read(1)         # 여기서 timeout 까지 waiting...

                    if len(data) == 0:
                        continue

                    #print('+%02X' % (ord(data)))
                    if ord(data[0]) == HEADER_VER:
                        self.recv_buff += data
                        self.state = self.STATE_LENGTH
                elif self.state == self.STATE_LENGTH:
                    data = self.port.read(1)
                    #print('-%02X' % (ord(data)))
                    if ord(data) < 0 or ord(data) > 250:
                        self.state = self.STATE_HEADER1          # 잘못된 패킷. 버림.
                    else:
                        self.length = ord(data)
                        self.recv_buff += data
                        if self.length > 0:
                            self.state = self.STATE_PAYLOAD
                        else:
                            self.state = self.STATE_CRC
                elif self.state == self.STATE_PAYLOAD:
                    self.recv_buff += self.port.read(self.length)
                    #print(len(self.payload))

                    if len(self.recv_buff) == self.length + 3:
                        self.state = self.STATE_CRC

                elif self.state == self.STATE_CRC:
                    data = self.port.read(2)
                    if len(data) == 0:
                        self.state = self.STATE_HEADER
                        continue

                    self.recv_buff += data
                    if wonik_crc16.crc16(self.recv_buff) == 0:

                        #print('received')
                        self.DecodePacket(self.recv_buff)
                    else:
                        print('CRC mismatch')

                    self.state = self.STATE_HEADER1



            elif SERIAL_VERSION == 2:
                recv_char = self.port.read(1)         # 여기서 timeout 까지 waiting...

                if len(recv_char) == 0:
                    continue

                #print('0x%02X' % ord(recv_char))

                if len(recv_char) != 1:
                    continue

                if recv_char[0] == SERIAL_STX:
                    if self.state != self.STATE_CMDLE:
                        print('E,Out of state SOF. Force start a new packet')
                    self.recv_buff = recv_char
                    self.state = self.STATE_RECEIVING
                else:
                    if self.state == self.STATE_CMDLE:
                        continue

                    if recv_char[0] == SERIAL_ETX:
                        if self.state != self.STATE_RECEIVING:
                            print('E,Out of state EOF.')
                            self.state = self.STATE_CMDLE
                            continue
                        self.state = self.STATE_CMDLE
                        self.recv_buff += recv_char

                        # receive done. check length, CRC field
                        if len(self.recv_buff) != self.recv_buff[2] + 6:
                            print('E,packet length field is not match. %d/%d' % (len(self.recv_buff), self.recv_buff[2] + 6))
                            bb=[bytes([b]) for b in self.recv_buff]
                            #print(bb)
                            self.state = self.STATE_CMDLE
                            continue

                        if wonik_crc16.crc16(self.recv_buff[:-1]) == 0:
                            #print('received')
                            self.DecodePacket(self.recv_buff)
                        else:
                            print('E,CRC mismatch')


                    elif recv_char[0] == SERIAL_STUFF[0]:
                        if self.state != self.STATE_RECEIVING:
                            print('E,Out of state stuff character. drop message')
                            self.state = self.STATE_CMDLE
                            continue

                        self.state = self.STATE_STUFFING

                    else:
                        if self.state == self.STATE_RECEIVING:
                            self.recv_buff += recv_char
                        elif self.state == self.STATE_STUFFING:
                          try:
                            recovered = False
                            for org, rep in SERIAL_STUFFING_DIC.items():
                                #print(type(recv_char[0:1]))
                                #print(type(rep))

                                if recv_char[0:1] == rep:
                                    self.recv_buff += org
                                    recovered = True
                                    self.state = self.STATE_RECEIVING
                                    break
                            if not recovered:
                                print('E,stuffed byte is not match with stuffing table.')
                                self.state = self.STATE_CMDLE
                                continue
                          except:
                            print('recv char = 0x%02x' % (recv_char[0]))








            #except:
            #    self.parent.parent.portConfWnd.CloseSerialPort()
            #    self.Stop()
            #    break
            #if data != '':
            #    self.cb(data)

    def Stop(self):
        self.running = False

    def PrintLine(self, str):
        if self.timestamp:
            str = '%.3f,' % time.time() + str
        if self.f_out:
            self.f_out.write(str)
            self.f_out.write('\n')
            self.f_out.flush()
        print(str)

    def DecodePacket(self, data):
        msg_type, content_CMD, = struct.unpack('BB', self.recv_buff[3:5])

        self.PrintLine("RX:%d,%d,len=%d" % (msg_type, content_CMD, len(self.recv_buff)))

        if msg_type == SERIAL_MSG_TYPE_REQUEST:
            if content_CMD == SERIAL_CONTENT_CMD_HEARTBEAT:
                self.PrintLine("Heartbeat")
                if self.sender:
                    self.sender.ReplyHeartbeat()
            else:
                self.PrintLine('Request Msg,0x%02X' % content_CMD)
        elif msg_type == SERIAL_MSG_TYPE_RESPONSE:
            if content_CMD == SERIAL_CONTENT_CMD_READ_ROBOT_INFO:
                self.PrintLine('Robot Info reply,0x%04X,0x%08X' % struct.unpack('<HI', self.recv_buff[5:11]))
            elif content_CMD == SERIAL_CONTENT_CMD_POWER_CTRL:
                self.PrintLine('Power control reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_PROXIMITY:
                self.PrintLine('Read Proximity,%d' % struct.unpack('<B', self.recv_buff[5:6]))
                self.PrintLine('  %d,%d,%d,%d|%d,%d,%d,%d|%d,%d,%d,%d|%d,%d,%d,%d' % struct.unpack('<HHHHHHHHHHHHHHHH', self.recv_buff[6:38]))
            elif content_CMD == SERIAL_CONTENT_CMD_PAYLOAD_WEIGHT:
                self.PrintLine('Read PayloadWeight,%d' % struct.unpack('<B', self.recv_buff[5:6]))
                self.PrintLine('  %d,%d,%d,%d' % struct.unpack('<HHHH', self.recv_buff[6:6+8]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_ESTOP_SW:
                self.PrintLine('Read EStop SW,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_DRV_MODE:
                self.PrintLine('Set Driving mode reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_BATTERY:
                self.PrintLine('Read Battery,%d,%d,%d,%d' % struct.unpack('<BBBH', self.recv_buff[5:10]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_IMU:
                self.PrintLine('Read IMU,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' % struct.unpack('<hhhhhhhhhhhhh', self.recv_buff[5:5+2*13]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_IMU_QUATERNION:
                self.PrintLine('Read IMU Quaternion,%d,%d,%d,%d' % struct.unpack('<hhhh', self.recv_buff[5+3*3*2:5+2*13]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_MOTOR_POWER:
                self.PrintLine('Set Motor Power reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_SERVO_STATE:
                self.PrintLine('Set Servo state reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_CONFIG_PERIODIC_COMM:
                self.PrintLine('Config Periodic Comm reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_CONFIG_PERIODIC_NOTIFY:
                self.PrintLine('Config Periodic Notify reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_WHEEL_TORQUE:
                self.PrintLine('Set Wheel Torque reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_WHEEL_VEL:
                self.PrintLine('Set Wheel Velocity reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_BASE_TWIST:
                self.PrintLine('Set Base Twist reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_FEEDFORWARD_PARAM:
                self.PrintLine('Set Feedforward Param reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            #elif content_CMD == SERIAL_CONTENT_CMD_SET_SYSTEM_STATE:
            #    self.PrintLine('Set System state reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_LPT_READ_STATUS:
                self.PrintLine('LPT Read Status reply,%d-0x%04X' % struct.unpack('<BH', self.recv_buff[5:8]))
            elif content_CMD == SERIAL_CONTENT_CMD_LPT_SET_POWER:
                self.PrintLine('LPT Set Power reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_LPT_SET_SERVO:
                self.PrintLine('LPT Set Servo reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_LPT_SET_POSITION:
                self.PrintLine('LPT Set Position reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_LPT_SET_VELOCITY:
                self.PrintLine('LPT Set Velocity reply,%d' % struct.unpack('<B', self.recv_buff[5:6]))
            elif content_CMD == SERIAL_CONTENT_CMD_LPT_READ_FEEDBACK:
                fb =  struct.unpack('<ffBffBffB', self.recv_buff[5:32])
                self.PrintLine('  Lift: %f,%f,%d' % (fb[0:3]))
                self.PrintLine('  Pan : %f,%f,%d' % (fb[3:6]))
                self.PrintLine('  Tilt: %f,%f,%d' % (fb[6:9]))
            elif content_CMD == SERIAL_CONTENT_CMD_SET_DECO_LED:
                self.PrintLine('DecoLED:%d' % struct.unpack('<B', self.recv_buff[5:6]))  
            elif content_CMD == SERIAL_CONTENT_CMD_READ_ENV_SENSOR:
                self.PrintLine('Response ENV SENSOR')
            elif content_CMD == SERIAL_CONTENT_CMD_READ_WHEEL_VELOCITY:
                self.PrintLine('Wheel Vel reply,%2.1f,%2.1f' % struct.unpack('<ff', self.recv_buff[5:13]))
            elif content_CMD == SERIAL_CONTENT_CMD_GET_SONARGW_REPORT_CONFIG:
                self.PrintLine('Get Sonar Period:%d Hz' % struct.unpack('<B', self.recv_buff[5:6]))    
            else:
                self.PrintLine('Unknown Response, 0x%02X' % (content_CMD))
        elif msg_type == SERIAL_MSG_TYPE_NOTIFY:
            if content_CMD == SERIAL_CONTENT_CMD_READ_ODO:
                self.PrintLine('Notify Odo:%f,%f,%f,%f,%f,%f' % struct.unpack('<ffffff', self.recv_buff[5:5+24]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_BATTERY:
                self.PrintLine('Notify Battery,%d,%d,%d,%d' % struct.unpack('<BBBH', self.recv_buff[5:10]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_PROXIMITY:
                self.PrintLine('Notify Proximity,%d' % struct.unpack('<B', self.recv_buff[5:6]))
                self.PrintLine('  %d,%d,%d,%d|%d,%d,%d,%d|%d,%d,%d,%d|%d,%d,%d,%d' % struct.unpack('<HHHHHHHHHHHHHHHH', self.recv_buff[6:38]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_IMU:
                self.PrintLine('Notify IMU,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' % struct.unpack('<hhhhhhhhhhhhh', self.recv_buff[5:5+2*13]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_IMU_QUATERNION:
                self.PrintLine('Notify IMU Quaternion,%d,%d,%d,%d' % struct.unpack('<hhhh', self.recv_buff[5:5+2*4]))
            elif content_CMD == SERIAL_CONTENT_CMD_PAYLOAD_WEIGHT:
                self.PrintLine('Notify PayloadWeight,%d' % struct.unpack('<B', self.recv_buff[5:6]))
                self.PrintLine('  %d,%d,%d,%d' % struct.unpack('<HHHH', self.recv_buff[6:6+8]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_WHEEL_VELOCITY:
                self.PrintLine('Notify Wheel Vel:%f,%f' % struct.unpack('<ff', self.recv_buff[5:5+4*2]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_WHEEL_POS_VEL:
                self.PrintLine('Notify Wheel PosVel:%f,%f,%f,%f' % struct.unpack('<ffff', self.recv_buff[5:5+4*4]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_ROBOT_STATUS:
                self.PrintLine('Notify RobotStatus:%d,0x%04x' % struct.unpack('<BH', self.recv_buff[5:5+3]))
            elif content_CMD == SERIAL_CONTENT_CMD_READ_ENV_SENSOR:
                self.PrintLine('Notify ENV SENSOR:%d,%d,%d,%d' % struct.unpack('<HHhH', self.recv_buff[5:5+2*4]))    
            elif content_CMD == SERIAL_CONTENT_CMD_SONARGW_REPORT_FEEDBACK:
                self.PrintLine('Notify Sonar:%d,%d,%d,%d,%d,%d,%d,%d' % struct.unpack('<BBBBBBBB', self.recv_buff[5:5+1*8]))    
            else:
                self.PrintLine('Unknown Notify Msg,0x%02X' % content_CMD)
        else:
            self.PrintLine('Unknown message type [0x%02X]' % (msg_type))


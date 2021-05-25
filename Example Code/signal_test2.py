'''
import sys
import test1
import time
from PyQt5.QtCore import *

@pyqtSlot(str)
def cb_sock_recv_cplt(self, data):
	print("ok!")

test = test1.SockMsgRecvThread("hello world!")

test.recv_cplt.connect(cb_sock_recv_cplt)
test.start()

try:
	while True:
		time.sleep(1)
		print("1s!")
except KeyboardInterrupt:
	test.Stop()
'''
############################################
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import signal_test1


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        mainsignal = signal_test1.SockMsgRecvThread("hello world!")
        mainsignal.recv_cplt.connect(self.signal1_emit)
        mainsignal.start()

    @pyqtSlot(str)
    def signal1_emit(self, data):
        print("signal test")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

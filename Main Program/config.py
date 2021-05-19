import configparser


CONFIG_FILE_NAME = 'setting.cfg'

class Env_Config():
	def __init__(self):

		fp = None
		try:
			fp = open(CONFIG_FILE_NAME, 'r')
		except:
			self.BuildDefault()
		finally:
			if fp:
				fp.close()

		cnt = 1
		while cnt > 0:
			try:
				cp = configparser.ConfigParser()
				cp.read(CONFIG_FILE_NAME, encoding='utf-8')
				print('load config file success')
				
				self.COM_PORT = cp['DEFAULT']['COM_PORT']
				self.CARD1 = cp['DEFAULT']['CARD1_COM']
				self.CARD2 = cp['DEFAULT']['CARD2_COM']
				self.QR1 = cp['DEFAULT']['QR1_COM']
				self.QR2 = cp['DEFAULT']['QR2_COM']
				self.OS = cp['DEFAULT']['OS']
				
				print(self.CARD1)
				
				cnt = 0
			except KeyError:
				cnt -= 1
				self.BuildDefault()
				fp.close()

	def BuildDefault(self):
		print('Cannot read config file. Creating default...')

		newcp = configparser.ConfigParser()
		newcp.set('DEFAULT', 'COM_PORT', 'COM1')
		newcp.set('DEFAULT', 'CARD1_COM', '/dev/ttyAMA0')
		newcp.set('DEFAULT', 'CARD2_COM', '/dev/ttyAMA1')
		newcp.set('DEFAULT', 'QR1_COM', '/dev/ttyAMA2')
		newcp.set('DEFAULT', 'QR2_COM', '/dev/ttyAMA3')
		newcp.set('DEFAULT', 'OS', 'UBUNTU')

		fp = open(CONFIG_FILE_NAME, 'w')
		newcp.write(fp)


if __name__ == "__main__":
	cfg = Env_Config()

	print('COM port = ' + cfg.COM_PORT)


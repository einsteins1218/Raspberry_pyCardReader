# QR 웹 파싱하는 코드 구현 예정
# “처래처@품명@차량번호@입고량” 을 웹 파싱.
# https://docs.python-requests.org/en/master/user/quickstart/

import requests
from requests.exceptions import HTTPError

try:
	response = requests.get("http://ecoss.co.kr/qr.txt")
	response.encoding = 'UTF-8-SIG' # UTF-8 로 하니까 UTF-8 BOM 이 포함되어 맨 앞에 이상한 글자가 붇어서, 이를 해결
	
	# If the response was successful, no Exception will be raised
	response.raise_for_status()
	
	
	print(response.text)
	
	results = ['', '', '', '']
	parsing_index = 0
	
	for i in range(len(response.text)):
		
		if response.text[i] == '@':
			parsing_index += 1
			
			if parsing_index > 3: # @ 가 4개 이상 들어오면 에러 처리
				print("QR: Wrong Parsing Data")
				print("break")
				break
		else:
			results[parsing_index] += response.text[i]
			
	if parsing_index == 3: # @가 3개 들어오면, 정상적으로 들어왔음
		#GUI 로 파싱한 데이터 전송
		print(results[0])
		print(results[1])
		print(results[2])
		print(results[3])
		print(ord(results[0][0]))
	else:
		print("QR: Wrong Parsing Data")
	
	
except HTTPError as http_err:
	print(f'QR: HTTP error occurred: {http_err}')  # Python 3.6
except Exception as err:
	print(f'QR: Other error occurred: {err}')  # Python 3.6
else:
	print('QR: Parsing Success!')

			
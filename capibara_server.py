import socket, threading
import pyautogui
import time
import zlib
screen_size = 0.7		#스크린샷 사이즈

def send(client_socket, addr):		#전송함수
	global screen_size
	print('connect: ', addr)
	time.sleep(1)					#연결 직후 1초 대기
	try:
		while(True):
			image = pyautogui.screenshot()			#스크린샷 촬영
			image = image.resize(( int( image.size[0]*(screen_size) ), int( image.size[1]*(screen_size) ) ))	#크기조정
			data = image.tobytes()				#바이트화
			data = zlib.compress(data)			#압축
			length = len(data)
			client_socket.sendall(length.to_bytes(4, byteorder="little"))		#데이터 크기 전송
			client_socket.sendall(data)				#데이터 전송
			time.sleep(0.01)		#딜레이
	except:
		print("except: " , addr)
	finally:
		client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			#서버 생성
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 9001))
server_socket.listen()

try:
	while True:
		client_socket, addr = server_socket.accept()			#연결 기다리기
		th_send = threading.Thread(target=send, args = (client_socket,addr))
		th_send.start()			#send함수 실행
except:
	server_socket.close()
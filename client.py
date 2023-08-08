import sys
import time
from PIL import Image
import socket
import zlib
import threading
from PyQt6 import QtCore, QtWidgets, QtGui
from PIL.ImageQt import ImageQt
#from PyQt5.QtGui import QMovie
HOST = '127.0.0.1'			#접속ip
PORT = 9001			#접속포트
cursur_xy = [0,0]			#커서 좌표
rel_cusur_ratio = [0,0]		#커서 위치 비율
screen_size = 0.7			#스크린샷 크기
screen_width = 1920			#스크린샷 가로길이
screen_height = 1080			#스크린샷 세로길이
img_data =  Image.open( 'stanby.jpg' )	#초기이미지 설정
rec_count = 0				#통신횟수

class character(QtWidgets.QMainWindow):
	def __init__(self, size=1.0, on_top=False):
		super(character, self).__init__()
		self.opacity=1								#투명도
		self.name = "원격제어"						#창 이름
		self.size = size							#크기
		self.on_top = on_top						#항상 위에 있을지
		self.run_watch = 0							#실행타이머
		self.setupUi()
		self.show()

	def imagemanager_pil(self):			#이미지 변경
		global img_data, cursur_xy, rel_cusur_ratio
		self.img = ImageQt(img_data).copy()
		self.pixmap = QtGui.QPixmap.fromImage(self.img)		#pixmap 생성
		self.pixmap = self.pixmap.scaled(int(self.pixmap.width()*self.size), int(self.pixmap.height()*self.size))	#사이즈 변경
		self.label.setPixmap(self.pixmap)	#적용
		self.label.resize(self.pixmap.width(), self.pixmap.height())	#라벨 크기 변경
		self.label.move(int(cursur_xy[0] - rel_cusur_ratio[0]*self.label.width()), int(cursur_xy[1] - rel_cusur_ratio[1]*self.label.height()))	#이동

	def setupUi(self):
		global screen_size, screen_width, screen_height
		self.centralWidget = QtWidgets.QWidget(self)
		self.setCentralWidget(self.centralWidget)
		self.setflag(opacity=1)
		self.setWindowTitle(self.name)						#윈도우 제목 지정
		self.label = QtWidgets.QLabel(self.centralWidget)

		self.width = int(screen_width*screen_size)
		self.height = int(screen_height*screen_size)
		self.setGeometry(0, 0, self.width, self.height)
		self.imagemanager_pil()

	def setflag(self, Tool=False, FWH=False, opacity=1):				#플래그 및 투명도 지정함수
		if (Tool): self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.Tool)							#작업표시줄에 아이콘이 표시되지 않음
		else: self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.Tool)
		if (FWH): self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)			#윈도우 틀과 타이틀바 제거
		else: self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.FramelessWindowHint)
		if (self.on_top): self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)		#윈도우가 항상 맨 위에 있음
		else: self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)
		self.setWindowOpacity(opacity)

	def resizeEvent(self, event):
		self.width = self.centralWidget.frameGeometry().width()
		self.height = self.centralWidget.frameGeometry().height()

	def wheelEvent(self, event):			#마우스휠 확대
		global cursur_xy, rel_cusur_ratio
		cursur_xy = [event.pos().x(), event.pos().y()]		#커서 위치 저장
		rel_cusur_ratio = [(event.pos().x()-self.label.x())/self.label.width(), (event.pos().y()-self.label.y())/self.label.height()]	#커서 상대위치% 저장
		print (rel_cusur_ratio)
		if (event.angleDelta().y() < 0 and not self.size-0.15 <= 0.15):			#크기변수 수정
			print(self.size)
			self.size -= 0.15
		elif (event.angleDelta().y() > 0 and not self.size+0.15 >= 5):
			self.size += 0.15

	
	def mousePressEvent(self, event):
		global cursur_xy, rel_cusur_ratio
		cursur_xy = [event.pos().x(), event.pos().y()]
		rel_cusur_ratio = [(event.pos().x()-self.label.x())/self.label.width(), (event.pos().y()-self.label.y())/self.label.height()]
	def mouseMoveEvent(self, event):
		global cursur_xy, rel_cusur_ratio
		self.label.move(int(self.label.x() + (event.x() - cursur_xy[0])), int(self.label.y() + (event.y() - cursur_xy[1])))
		cursur_xy = [event.x(), event.y()]
		rel_cusur_ratio = [(event.pos().x()-self.label.x())/self.label.width(), (event.pos().y()-self.label.y())/self.label.height()]

	def run(self):				#행동함수
		self.run_timer = QtCore.QTimer(self)
		self.run_timer.timeout.connect(self.__runCore)				#0.01초마다 self.__runCore 호출
		self.run_timer.start(10)
	def __runCore(self):
		self.imagemanager_pil()
		self.run_watch += 0.01
		self.run_watch = round(self.run_watch, 2)





def receive(client_socket, addr):		#데이터 받기 함수
	global img_change, img_data, rec_count, screen_size, screen_width, screen_height
	while (True):
		start = time.process_time()		#시작시간 기록
		try:
			data = client_socket.recv(4)	#데이터 길이를 먼저 받음
			length = int.from_bytes(data, "little")
			buf = b''
			step = length
			a=0
			while True:				#데이터가 전부 받아질 때까지 반복
				a += 1
				data = client_socket.recv(step)
				buf += data
				if len(buf) == length:
					break
				elif len(buf) < length:
					step = length - len(buf)
			data = zlib.decompress(buf)			#압축풀기
			img_data = Image.frombytes('RGB', (int(screen_width*screen_size), int(screen_height*screen_size)), data)	#이미지 저장
			rec_count += 1
		except Exception as ex:
			if (ex == "Error -3 while decompressing data: invalid code lengths set"):	#압축해제 실패 에러
				print("connection fail : " , addr)
				break
			else:				#다른 에러는 소켓 관련으로 간주
				print("screenshot loading fail")
		finally:
			end = time.process_time()		#끝 시간 기록
			print(str(length) + " : " + str(a) + " : " + str(end - start))		#소요시간 출력









client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))			#접속

th_receive = threading.Thread(target=receive, args = (client_socket, HOST))		#받기함수 쓰레드
th_receive.start()

app = QtWidgets.QApplication(sys.argv)		#윈도우 창
window = character(size=1, on_top=False)
window.run()
sys.exit(app.exec())
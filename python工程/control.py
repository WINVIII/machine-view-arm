import serial
import time
import re

def tranformbyte(str):  # 串口发送数据格式转换
    return str.encode('ascii')


def main():
    ser = serial.Serial()
    ser.baudrate = 9600  # 设置波特率
    ser.port = 'COM6'  # 端口是COM6
    ser.open()  # 打开串口
    if ser.is_open:
        print("蓝牙连接成功")
        print("1.命令模式")
        print("2.文件模式")
        select = int(input())
        if select == 1:
            while (True):
                command = input("请输入命令:")
                print()
                ser.write(tranformbyte(command))
                time.sleep(1)
                print("指令已执行")
                print("---------")
                if command == "exit":
                    exit()
        if select == 2:
            f = open('command.txt', 'r')
            list_temp = f.readlines()
            if len(list_temp)==0:
                f.close()
                print("本地文件无内容，请输入文件路径")
                f = open(input(), 'r')
                list_temp = f.readlines()
            print(list_temp)
            loop=1
            if 'loop' in list_temp[0]:
                temp = 0
                for i in list_temp[0]:
                    if i>='0' and i<='9':
                        temp = int(i)+temp*10
                loop=temp
                print("循环"+str(loop)+"遍")
                t=1
            else:
                print("循环1遍")
                t=0
            for i in range(int(loop)):
                for command in list_temp[t:]:
                    print(command)
                    ser.write(tranformbyte(command))
                    time.sleep(2)
                    print("命令执行成功")
                    print("-----------")
            print('循环结束')

    else:
        print("请检查蓝牙连接")


if __name__ == "__main__":
    main()

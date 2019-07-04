# coding:utf-8
import numpy as np
import cv2 as cv
import serial
import math

global image, ser,roller
global x1, x2, x3, y1, y2, y3, x, y
global start_center, roller_center, final_center
ser = serial.Serial()


def contrast_img(img1, c, b):  # 亮度调节模块
    rows, cols, channels = img1.shape
    blank = np.zeros([rows, cols, channels], img1.dtype)
    dst = cv.addWeighted(img1, c, blank, 1 - c, b)
    return dst


def tranformbyte(str):  # 串口发送数据格式转换
    return str.encode('ascii')


def pointlen(a):
    b = math.sqrt((a[0] - a[2]) ** 2 + (a[1] - a[3]) ** 2)
    return int(b)


def nextstep(store, pointlen):
    print(pointlen)
    if store is not False:
        if pointlen >= 100:
            ser.write(tranformbyte("y" + str(store - 30)))
            print(store - 40)
            if store - 40 >= 0:
                return store - 40
            else:
                return False
        elif pointlen >= 50:
            ser.write(tranformbyte("y" + str(store - 20)))
            print(store - 20)
            if store - 20 >= 0:
                return store - 20
            else:
                return False
        elif pointlen >= 25:
            ser.write(tranformbyte("y" + str(store - 10)))
            if store - 25 >= 0:
                return store - 10
            else:
                return False
        elif pointlen < 25:
            return False


def main():
    cap = cv.VideoCapture(0)
    tracker = cv.TrackerCSRT_create()  # CSRT追踪模块
    # 串口初始化
    ser.baudrate = 9600  # 设置波特率
    ser.port = 'COM6'  # 蓝牙端口是COM6
    print(ser)
    ser.open()  # 打开串口
    print(ser.is_open)  # 检验串口是否打开

    def grapnelfind(image):  # 识别模块
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        find = cv.CascadeClassifier("H:\\Desktop\\final.xml")  # 训练所得数据集
        grapnel = find.detectMultiScale(gray, 5.1, 17, minSize=(40, 40), maxSize=(150, 150))
        for x, y, w, h in grapnel:
            if y < 250 and x > 100 and x < 300:
                cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                grapneled = (x, y, w, h)
        cv.imshow("Auto Select", image)
        if (cv.waitKey(1) & 0xFF == 13) and grapnel is not None:
            grapnel_back = grapneled
            roller = cv.selectROI(image)
            cv.circle(image, ((int(roller[0] + roller[2] / 2), int(roller[1] + roller[3] / 2))), 220, (0, 225, 0,), 1)
            cv.circle(image, ((int(roller[0] + roller[2] / 2), int(roller[1] + roller[3] / 2))), 280, (0, 225, 0,), 1)
            start = cv.selectROI(image)
            final = cv.selectROI(image)
            back = grapnel_back + start + final + roller
            return back
        if cv.waitKey(1) & 0xff == ord('s'):
            grapnel = cv.selectROI(image)
            start = cv.selectROI(image)
            final = cv.selectROI(image)
            roller = cv.selectROI(image)
            back = grapnel + start + final + roller
            print(back)
            return back

    while (True):  # 摄像头读取模块
        ret, frame = cap.read()
        frame = contrast_img(frame, 1.3, 80)
        back = grapnelfind(frame)
        if (back is not None) and (len(back) > 8 and len(back) <= 16):
            bbox = (int(back[0]), int(back[1]), int(back[2]), int(back[3]))  # 机械抓起点信息
            start = (int(back[4]), int(back[5]), int(back[6]), int(back[7]))  # 起点信息
            final = (int(back[8]), int(back[9]), int(back[10]), int(back[11]))  # 终点信息
            roller = ((int(back[12]), int(back[13]), int(back[14]), int(back[15])))  # 转轴信息
            print(bbox)
            print(start)
            print(final)
            cv.destroyAllWindows()
            break

        t = 15
        i = 1
    while (True):  # 追踪模块
        i += 1  # 用于记录时间
        ret, frame = cap.read()
        frame = contrast_img(frame, 1.1, 80)
        tracker.init(frame, bbox)
        timer = cv.getTickCount()
        ok, bbox = tracker.update(frame)
        fps = cv.getTickFrequency() / (cv.getTickCount() - timer)
        start_center = (int(start[0] + start[2] / 2), int(start[1] + start[3] / 2))
        cv.circle(frame, start_center, 20, (0, 242, 255), 3)
        final_center = (int(final[0] + final[2] / 2), int(final[1] + final[3] / 2))
        cv.circle(frame, final_center, 20, (234, 255, 0), 3)
        roller_center = ((int(roller[0] + roller[2] / 2), int(roller[1] + roller[3] / 2)))
        cv.circle(frame, roller_center, 5, (0, 255, 0), 3)
        cv.circle(frame, roller_center, 220, (0, 255, 0), 1)
        cv.circle(frame, roller_center, 280, (0, 225, 0,), 1)
        if ok:
            global p1, p2
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            bbox_center = (int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2))
            cv.circle(frame, bbox_center, 2, (0, 0, 255), 2)
            cv.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        else:
            cv.putText(frame, "Tracking failure detected", (100, 80), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        cv.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)  # 计算FPS
        cv.namedWindow("Tracking", cv.WINDOW_AUTOSIZE)
        cv.imshow("Tracking", frame)
        # i+=1
        # if i == 8:
        #     x1 = bbox_center[0]
        #     y1 =bbox_center[1]
        #     ser.write(tranformbyte("d70"))
        # if i == 50:
        #     x2 = bbox_center[0]
        #     y2 = bbox_center[1]
        #     ser.write(tranformbyte("d110"))
        # if i == 80:
        #     x3 = bbox_center[0]
        #     y3 = bbox_center[1]
        #     ser.write(tranformbyte("d90"))
        # #计算机械臂主轴
        #     x = ((y2 - y1) * (y3 * y3 - y1 * y1 + x3 * x3 - x1 * x1) - (y3 - y1) * (
        #                 y2 * y2 - y1 * y1 + x2 * x2 - x1 * x1)) / (
        #                     2.0 * ((x3 - x1) * (y2 - y1) - (x2 - x1) * (y3 - y1)))
        #
        #     y = ((x2 - x1) * (x3 * x3 - x1 * x1 + y3 * y3 - y1 * y1) - (x3 - x1) * (
        #                 x2 * x2 - x1 * x1 + y2 * y2 - y1 * y1)) / (
        #                     2.0 * ((y3 - y1) * (x2 - x1) - (y2 - y1) * (x3 - x1)))
        #
        #     x=int(x)
        #     y=int(y)
        #     print(x,y)
        if i == t * 1:
            ser.write(tranformbyte("q130"))
        elif i == t * 2:
            ser.write(tranformbyte("z180"))
        elif i == t * 3:
            a = ((480-start_center[1]) - (480-roller_center[1])) / (start_center[0] - roller_center[0])
            print(start_center)
            print(roller_center)
            print(a)
            b = math.atan(a)
            print(b)
            degree = int(math.degrees(b))
            if degree <0:
                degree = 180+degree
            print(degree)
            str1 = "d" + str(degree)
            print(str1)
            print(tranformbyte(str1))
            ser.write(tranformbyte(str1))
        elif i == t * 4:
            far = pointlen(bbox_center + start_center)
            print(far)
            now = nextstep(70, far)
            if now is False:
                i = i + 3 * t
        elif i == t * 5:
            far = pointlen(bbox_center + start_center)
            now = nextstep(now, far)
            if now is False:
                i = i + 2 * t - 5
        elif i == t * 6:
            far = pointlen(bbox_center + start_center)
            nextstep(now, far)
        if i == t * 7:
            ser.write(tranformbyte("z70"))
        elif i == t * 8:
            ser.write(tranformbyte("y90"))
        elif i == t * 9:
            ser.write(tranformbyte("reset"))
        elif i == t * 10:
            a = ((480 - final_center[1]) - (480 - roller_center[1])) / (final_center[0] - roller_center[0])
            print(final_center)
            print(roller_center)
            print(a)
            b = math.atan(a)
            print(b)
            degree = int(math.degrees(b))
            if degree<0:
                degree = 180+degree
            str1 = "d" + str(degree)
            print(str1)
            print(tranformbyte(str1))
            ser.write(tranformbyte(str1))
        elif i == t * 11:
            ser.write(tranformbyte("q130"))
        elif i == t * 12:
            far = pointlen(bbox_center + final + final_center)
            print(far)
            now = nextstep(70, far)
            if now is False:
                i = i + 3 * t-5
        elif i == t * 13:
            far = pointlen(bbox_center + final_center)
            now = nextstep(now, far)
            print(far)
            if now is False:
                i = i + 2 * t-5
        elif i == t * 14:
            far = pointlen(bbox_center + final_center)
            nextstep(now, far)
        if i == t * 15:
            ser.write(tranformbyte("z180"))
        elif i == t * 16:
            ser.write(tranformbyte("y90"))
        elif i == t * 17:
            ser.write(tranformbyte("reset"))
        if cv.waitKey(1) & 0xFF == 13:
            cap.release()
            cv.destroyAllWindows()
            break


if __name__ == '__main__':
    main()

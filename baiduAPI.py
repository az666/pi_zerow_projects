from picamera import PiCamera
import time
import RPi.GPIO
import requests
import base64
import sys
import serial
import os

def getaccess_token():
## 获取access_token

    host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=4fVKa7AqDYNApi6Lz8Z2ZeMv&client_secret=gRVy9GcRRGCMiU2GgT20IbbaMu7QfA8P'

    header_1 = {'Content-Type':'application/json; charset=UTF-8'}

    request=requests.post(host,headers =header_1)

    access_token=request.json()['access_token']
    print(access_token)
    return access_token


def take_picture():
 #拍摄当前图片   
    camera.start_preview()

    time.sleep(0.5)

    camera.capture('image.jpg')

    camera.stop_preview()
def open_pic():
#打开工程拍摄的图片并转换成字符串
    f = open('image.jpg', 'rb')

    img = base64.b64encode(f.read())

    return img

def search (img,access_token):
##    人脸搜索白度api_v3以后就叫做“人脸搜索”了
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {"image":img,"image_type":"BASE64","group_id_list":"wenzheng","quality_control":"LOW","liveness_control":"NORMAL"}
    request_url = request_url + "?access_token=" + access_token
    ##发送数据利用requests.post（）的方法－－比较简单
    response = requests.post(request_url, data=params)
    ##输出json数据
    output = response.json()
    return output
def chuli (output):
    print(output)
    print(type(output)) ##输出数据类型为－字典
    if output['error_msg'] == 'SUCCESS':
        ##判断是否成功
        ##找到字典里的result－以及内层字典里的user_list
        user_list= output['result']['user_list']
        print(user_list)
        ##输出数据类型，发现其为列表
        print(type(user_list))
        ##利用列表的检索方式找到列表里的人脸检测分数－score
        score = user_list[0]['score']
        print(score)
        ##串口发送
        ser.write(str(score).encode()) 
        #panduan(score)
        user = user_list[0]['user_info']
        time.sleep(1)
        print(user)
        ser.write(user.encode())
    else:
        print(output['error_msg'])
        print(type(output['error_msg']))
        ser.write(output['error_msg'].encode())
"""
反馈的数据：利用他来解析
可知此次的人脸对比分数为：93分
{'error_code': 0, 'error_msg': 'SUCCESS', 'timestamp': 1528009295, 'log_id': 3173075542, 'cached': 0,
'result': {'face_token': '7fd111f61fb07e034577b277c7caca3f',
'user_list': [{'user_id': 'wenzheng', 'user_info': 'pengwenzheng', 'score': 93.49373626709, 'group_id': 'wenzheng'}]}}
"""
def panduan(score): 
    if score > 80:
        #print(type(score))
        ser.write(str(score).encode())          
    else :
        ser.write(b'2')
def led():
## led
    RPi.GPIO.output(18, True)
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0',115200,timeout=1)
    ser.close()
    ser.open()
    print("串口已开启")
    camera = PiCamera()
    count=0
    access_token=getaccess_token()
    while True :
        take_picture()
        img=open_pic()
        output = search(img,access_token)
        chuli(output)
        count=count+1
        print(count)
        #加入自动重启命令，防止程序运行时间过长死机
        if count == 2000 :
            os.system('sudo reboot')
            count = 0

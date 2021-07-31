from cv2 import cv2
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector as mysql
from datetime import datetime
import time
from micropyGPS import MicropyGPS
from rpi_lcd import LCD
from num2words import num2words
from subprocess import call

lcd=LCD()
my_gps = MicropyGPS()
cmd_beg= 'espeak '

mydb = mysql.connect(host="www.remotemysql.com", user="z05MTRZiao", passwd="NOHXoXfXjV", database="z05MTRZiao")
if(mydb):
    print("Connection to DataBase Successful")
else:
    print("Connection to DataBase Unsuccessful")

mycursor=mydb.cursor(buffered=True)
mycursor.execute("SET time_zone = '+05:30'")

#a= "C:\\Users\\USER\\Desktop\\ML using Python\\VS project\\yolov3_custom.cfg"
#b= "C:\\Users\\USER\\Desktop\\ML using Python\\VS project\\yolov3_custom_6000.weights"
#net = cv2.dnn.readNetFromDarknet(a,b)
#net = cv2.dnn.readNetFromDarknet("yolov4_custom.cfg",r"yolov4_custom_6000.weights")
net = cv2.dnn.readNetFromDarknet("yolov3_custom.cfg",r"yolov3_custom_6000.weights")
#classes = ['Red','Yellow','Green']
classes = ['Green','Red','Yellow']
flag=0
cap = cv2.VideoCapture(0)

while 1:
    _, img = cap.read()
    img = cv2.resize(img,(1280,720))
    hight,width,_ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1/255,(416,416),(0,0,0),swapRB = True,crop= False)

    net.setInput(blob)

    output_layers_name = net.getUnconnectedOutLayersNames()

    layerOutputs = net.forward(output_layers_name)

    boxes =[]
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.7:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3]* hight)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                boxes.append([x,y,w,h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes,confidences,.5,.4)

    boxes =[]
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3]* hight)

                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x,y,w,h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes,confidences,.8,.4)
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0,255,size =(len(boxes),3))
    if  len(indexes)>0:
        for i in indexes.flatten():
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i],2))
            color = colors[i]
            print(label +" Signal")
            lcd.text(label+" Signal",1)
            time.sleep(5.0)
            lcd.clear()
            if(label=="Red"):
                text = "Red Signal, Please stop the car within 10 meters."
                text = text.replace(' ', '_')
                call([cmd_beg+text], shell=True)
                print("Plz Stop the car within 10 meters...")
                lcd.text("Plz Stop the car within 10 meters...",1)
                time.sleep(5.0)
                lcd.clear()
                print(my_gps.speed_string('kph'))
                lcd.text(my_gps.speed_string('kph'),1)
                time.sleep(5.0)
                lcd.clear()
                if (my_gps.speed_string('kph')=="0.0 km/h"):
                    print("Car has stopped")
                    lcd.text("Car has stopped",1)
                    time.sleep(5.0)
                    lcd.clear()
                else:
                    mycursor.execute("Insert into timedetails values(now())")
                    mycursor.execute("Insert into defaulters Select * from (select S_id,OwnerName, Model_No, Model_Name, Phn_No, D_License, CarLicense, Penalty, Charges, Time from rto,finedetails,timedetails where S_id=1 and Penalty='Signal Disobey') as T ;")
                    mycursor.execute("Truncate table timedetails")
                    mydb.commit()
            elif(label=="Green"):
                text = "Green Signal, You can go."
                text = text.replace(' ', '_')
                call([cmd_beg+text], shell=True)
                print("You can go...")
                lcd.text("You can go...",1)
                time.sleep(5.0)
                lcd.clear()
            elif(label=="Yellow"):
                text = "Yellow Signal, Please slow down the car."
                text = text.replace(' ', '_')
                call([cmd_beg+text], shell=True)
                print("Plz slow down the car...")
                lcd.text("Plz slow down the car...",1)
                time.sleep(5.0)
                lcd.clear()
            print(confidence)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
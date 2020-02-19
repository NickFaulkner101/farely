import requests, json
import csv
import sys
import datetime
from datetime import timedelta
import base64
import cv2
import numpy as np

USERNAME= "nicholasfaulkner@btinternet.com"
PASSWORD= "Vitriolino01!"

def lighten_image(input_file):
    outputFile=input_file+"edit.png"
    img=cv2.imread(input_file)
    alpha=2
    beta=50
    result=cv2.addWeighted(img,alpha,np.zeros(img.shape,img.dtype), 0, beta)
    cv2.imwrite(outputFile, result)
    return outputFile

def encode_image(input):
    with open(input, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('UTF-8')
        return encoded_string

def request_data(string):
    key="AIzaSyDoo7pnIw37V-1219PkCHKGOFV4Ya2Txxk"
    URL="https://eu-vision.googleapis.com/v1/images:annotate?key="+key
    
    data={
        "requests":[
            {
            "image":{
                "content": string
            },
            "features": [
                {
                "type":"DOCUMENT_TEXT_DETECTION",
                "maxResults":1
                }
            ]
            }
        ]
        }
    r = requests.post(URL, json = data)
    result=r.json()
    # print(r.text)
    result=json.dumps(r.json(), indent=2)
    writeFile =open("ocrtest.json", 'w')
    writeFile.write(result)

def route_display():
    route=[]
    with open("ocrtest.json") as json_file:                 #open json file
        data = json.load(json_file) 
        x=data['responses'][0]["textAnnotations"][0]["description"]
        # print(x)
        #iterate through each line, if the first 2 characters = "to", return the next part of the string on that line
        z=int(-1)
        for line in x.splitlines():
            if str(line[:4])=="from":
                z=z+1
                route.insert(z,line[5:])
            elif str(line[:2])=="to":
                z=z+1
                route.insert(z,line[3:])   #insert is important as it provides a standard list format for main() to interpret where 0th element is from, 1st element is to, 2nd element is initial date, 3rd element is last date
            # if str(line[2])=="-":
            #     z=len(route)
            #     print(z)
            #     route.insert(z,line)
        
        return route

def get_days(): #get 2 dates ticket is valid for
    with open("ocrtest.json") as json_file:                 #open json file
        data = json.load(json_file) 
        x=data['responses'][0]["textAnnotations"][0]["description"]
        dates=[]
        
        for line in x.splitlines():   
            if str(line[2:3])=="-": #cycles through looking for each month. This is the identifier for dates at the moment
                                  #might not need improvements since all formats have the - apart from singles https://www.nationalrail.co.uk/times_fares/ticket_types/144168.aspx
                if line[3:6]=="AUG":
                    x="20"+line[7:10]+"-08-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="NOV":
                    x="20"+line[7:10]+"-11-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="MAY":
                    x="20"+line[7:10]+"-05-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="JNR":
                    x="20"+line[7:10]+"-01-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="DMR":
                    x="20"+line[7:10]+"-12-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="FBY":
                    x="20"+line[7:10]+"-02-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="MCH":
                    x="20"+line[7:10]+"-03-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="APR":
                    x="20"+line[7:10]+"-04-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="JUN":
                    x="20"+line[7:10]+"-06-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="JLY":
                    x="20"+line[7:10]+"-07-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="SEP":
                    x="20"+line[7:10]+"-09-"+line[0:2]
                    dates.append(x)
                elif line[3:6]=="OCT":
                    x="20"+line[7:10]+"-09-"+line[0:2]
                    dates.append(x)
        return dates
def get_time():
    
    with open("ocrtest.json") as json_file:                 #open json file
        data = json.load(json_file) 
        x=data['responses'][0]["textAnnotations"][0]["description"]
        dates=[]
        # print(x)
        
        for line in x.splitlines():
            if line[:8] == "Valid at":
                time=line[9:13]
            elif line[:8] =="valid at":
                time=line[9:13]
    return time

def getrid(fromloc,toloc,from_time,to_time,from_date,to_date,days):
    
    data={
    "from_loc":fromloc,
    "to_loc":toloc,
    "from_time":from_time,
    "to_time":to_time,
    "from_date":from_date,
    "to_date":from_date,
    "days":days,
    }
    headers = {'content-type': 'application/json'}
    auth=requests.auth.HTTPBasicAuth(USERNAME, PASSWORD)
    r = requests.post('https://hsp-prod.rockshore.net/api/v1/serviceMetrics', auth=auth,data=json.dumps(data),headers=headers)
    traindata=r.json()
    # print(traindata)
    x=traindata['Services'][0]['serviceAttributesMetrics']['rids']
    rid=''.join(x)
    # print("rid: "+rid)
    traindata=json.dumps(r.json(), indent=2)
    writeFile =open('Timetableinfo'+fromloc+'to'+toloc+'data.json', 'w')
    writeFile.write(traindata)
    return rid


def delayapi(rid,fromloc,toloc):
    data={
        "rid":rid                                                   #input rid
        }
    headers = {'content-type': 'application/json'}
    auth=requests.auth.HTTPBasicAuth(USERNAME, PASSWORD)
    r = requests.post('https://hsp-prod.rockshore.net/api/v1/serviceDetails', auth=auth,data=json.dumps(data),headers=headers)
    delaydata=r.json()
    delaydata=json.dumps(r.json(), indent=2)
    writeFile =open('delayinfo'+fromloc+'to'+toloc+'data.json', 'w')
    writeFile.write(delaydata)

def DelayData(fromloc,toloc,from_station,to_station,from_time,from_date):
    with open('delayinfo'+fromloc+'to'+toloc+'data.json') as json_file:                 #open json file
        data = json.load(json_file) 
        x=data['serviceAttributesDetails']['locations']
        
        for i in range(0,len(x)):
            if x[i]["location"]==toloc:
                # print(x[i]["location"])
                Planned_Arrival=str(x[i]["gbtt_pta"])
                Actual_Arrival=str(x[i]["actual_ta"])
                minutes_A=(int(Planned_Arrival[:2])*60)+int(Planned_Arrival[2:])
                minutes_B=(int(Actual_Arrival[:2])*60)+int(Actual_Arrival[2:])
                delay=str(minutes_B-minutes_A)
                
                hrA=int(Planned_Arrival[:2])
                mnA=int(Planned_Arrival[2:])
                hrB=int(Actual_Arrival[:2])
                mnB=int(Actual_Arrival[2:])               

                t1 = timedelta(hours=hrA, minutes=mnA)
                t2 = timedelta(hours=hrB, minutes=mnB)
                delay=t2-t1
                print(".")
                print(".")
                print(".")
                print(".")
                print(".")
                print("           Searching for delay data")
                print("")
                print("")
                print("Delay information for the "+from_time+" from "+from_station+" to "+to_station+" on "+from_date+":")
                print("")
                print("Planned arrival time at "+to_station+": "+Planned_Arrival)
                print("Actual arrival time at "+to_station+": "+Actual_Arrival)
                print("")
                delay=delay.total_seconds()/60
                delay=float(delay)

                if delay>15:
                    print("Delay length: "+str(delay)+" minutes")
                    print("")
                    print("        Elligible for delay repay!")
                    print("")
                elif delay<15:
                    print("Delay length: "+str(delay)+" minutes")
                    print("Sorry, not elligible for delay repay")
        
def operator(fromloc,toloc):
    with open('Timetableinfo'+fromloc+'to'+toloc+'data.json') as json_file:                 #open json file
        data = json.load(json_file) 
        toc_code=data['Services'][0]['serviceAttributesMetrics']["toc_code"]
        print("Operator: "+toc_code)

def getweekday(date): #since darwin wants it in this specific input
    inputdate=date
    year=inputdate[0:4] #YYYY
    month=inputdate[5:7] #MM
    day=inputdate[8:10] #DD
    weekDays = ("WEEKDAY","WEEKDAY","WEEKDAY","WEEKDAY","WEEKDAY","SATURDAY","SUNDAY") #in order of monday through to sunday, strangely HSP wants the day type specified
    in_date_time = datetime.date(int(year),int(month),int(day))
    in_date_time = in_date_time.weekday() #finds the reference date returned as a digit representing days of the week
    day_name = weekDays[in_date_time]
    returnvalue=[]
    returnvalue.append(day_name)
    returnvalue.append(inputdate)
    return returnvalue



def main(input_file):
    #///Make Brighter\\\
    outputFile=lighten_image(input_file)
    
    
    #///Optical Character Recognition Functions\\\
    string=encode_image(outputFile)   #encode into base64
    request_data(string)    #Sends encoded image to API and saves as JSON
    
    #///Parse JSON Response From Google Vision API\\\
    route=route_display()   #Parses and finds station names
    date=get_days()         #Gets ticket validity date(s)
    day_name=getweekday(date[0])   #add functionality later, if date[0] and date[1] are different
    time=get_time()         #returns the time HHmm

    #///Extract Key Information from Parsed Data\\\
    from_station=route[0]
    to_station=route[1]
    
    #convert to station code
    csv_file = csv.reader(open('station_codes.csv', "r"), delimiter=",") #open csv of train station codes
    for row in csv_file:
        if from_station == row[0]:   #if name is equal to anything in the 
            fromloc=str(row[1])         #first column of csv, return corresponding 2nd column
        elif to_station == row[0]:
            toloc=str(row[1])

    from_time = time
    to_time = str(int(from_time)+1)
    
    if from_time[0] == "0":
        to_time=str(int(from_time)+1)
        to_time="0"+to_time    #without this, the zero gets removed in the HrHr 
    
    from_date=date[1]
    to_date=from_date #this is current requirement of HSP, just search for this specific train atm
    day_type=day_name[0]
    
    #/// Use these to check inputs\\\
    # print(fromloc)
    # print(toloc)
    # print(from_time)
    # print(to_time)
    # print(from_date)
    # print(to_date)
    # print(day_type)
    
    #///Connecting to HSP API from National Rail\\\
    #Connect to Services API for unique RID Number
    firstRid=getrid(fromloc,toloc,from_time,to_time,from_date,to_date,day_type) #each train has a unique rid number
    #Then connect to Metrics API for delay data
    delayapi(firstRid,fromloc,toloc)
    #Parse JSON for Delay Info
    DelayData(fromloc,toloc,from_station,to_station,from_time,from_date) #are you sure about the "delay info for "station" because it takes the inputs from the image, not the inputs from the JSON response. IT's to check that the response JSON is checking the stations we specified. Maybe have something like "ticket input station strings are x" "JSON stations are X" hopefully they're the same?
    #Get operator Symbol
    operator(fromloc,toloc)
if __name__ =='__main__':
    main(sys.argv[1])

#add ability to read type of ticket
#authenticate journey, if it's fake or not
#if valid for any time, or off-peak, request manual input
#ABILITY TO MAKE NORMAL TICKETS BRIGHTER//////////////////////<----------
#what about cancelled trains, do you check the next train that is not cancelled and then see if that one's destination (to_time+15) arrival is more than 15 after original?
#https://en.wikipedia.org/wiki/Station_group_(railway)#Terminology_and_appearance_on_tickets abreviations 
#London St Pancras International
from flask import Flask, request, session
import requests
import json
import datetime
from datetime import timedelta
app = Flask(__name__)
# import datetime
# from datetime import timedelta
#    ?fromloc=BHI&toloc=WVH&fromtime=1100&totime=1130&fromdate=2020-01-13
@app.route('/')
def welcome():
    return "?fromloc=BHI&toloc=WVH&fromtime=1100&totime=1130&fromdate=2020-01-13"

@app.route('/base64')
def welcome():
    return 

@app.route('/dtest')
def hello():
    # auth for national rail api
    USERNAME= "nicholasfaulkner@btinternet.com"
    PASSWORD= "Vitriolino01!" 
    # get arguments from url search, needed for national rail api
    fromloc=request.args.get('fromloc')
    toloc=request.args.get('toloc')
    fromtime=request.args.get('fromtime')
    totime=request.args.get('totime')
    fromdate=request.args.get('fromdate')
    # api has a set of requirements. as searching for specific train, just need same date
    #need to input a "weekday" for the api in set format so this gets that for each input day
    inputdate=fromdate
    year=inputdate[0:4] #YYYY
    month=inputdate[5:7] #MM
    day=inputdate[8:10] #DD
    weekDays = ("WEEKDAY","WEEKDAY","WEEKDAY","WEEKDAY","WEEKDAY","SATURDAY","SUNDAY") #in order of monday through to sunday, strangely HSP wants the day type specified
    in_date_time = datetime.date(int(year),int(month),int(day))
    in_date_time = in_date_time.weekday() #finds the reference date returned as a digit representing days of the week
    day_name = weekDays[in_date_time]
    #data for api
    data={
    "from_loc":fromloc,
    "to_loc":toloc,
    "from_time":fromtime,
    "to_time":totime,
    "from_date":fromdate,
    "to_date":fromdate,
    "days":day_name,
    }
    #only way which seems to work for logging in at the moment
    headers = {'content-type': 'application/json'}
    auth=requests.auth.HTTPBasicAuth(USERNAME, PASSWORD)
    r = requests.post('https://hsp-prod.rockshore.net/api/v1/serviceMetrics', auth=auth,data=json.dumps(data),headers=headers)
    traindata=r.json()

    x=traindata['Services'][0]['serviceAttributesMetrics']['rids']
    rid=''.join(x)
    
    data={
        "rid":rid                                                   #input rid
        }
    
    headers = {'content-type': 'application/json'}
    auth=requests.auth.HTTPBasicAuth(USERNAME, PASSWORD)
    r = requests.post('https://hsp-prod.rockshore.net/api/v1/serviceDetails', auth=auth,data=json.dumps(data),headers=headers)
    delaydata=r.json()
    
    
    
    
    full_route_data=delaydata['serviceAttributesDetails']['locations']
    
    for i in range(0,len(full_route_data)):
        if full_route_data[i]["location"]==toloc:
            # # print(x[i]["location"])
            Planned_Arrival=str(full_route_data[i]["gbtt_pta"])
            Actual_Arrival=str(full_route_data[i]["actual_ta"])
            minutes_A=(int(Planned_Arrival[:2])*60)+int(Planned_Arrival[2:])
            minutes_B=(int(Actual_Arrival[:2])*60)+int(Actual_Arrival[2:])
            # delay=str(minutes_B-minutes_A)

            hrA=int(Planned_Arrival[:2])
            mnA=int(Planned_Arrival[2:])
            hrB=int(Actual_Arrival[:2])
            mnB=int(Actual_Arrival[2:]) 
            t1 = timedelta(hours=hrA, minutes=mnA)
            t2 = timedelta(hours=hrB, minutes=mnB)
            delay=t2-t1
            delay=delay.total_seconds()/60
            delay=float(delay)
            # output=[]
            # output.append(str(delay))

            if delay<15:
                return str(delay)+" minute delay. Sorry, not elligible for delay repay."
                    
            elif delay>15:
                return str(delay)+" minutes delay. Elligible for delay repay"
                    




if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_warmup_app]

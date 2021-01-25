import bs4 as bs
import urllib.request
import sqlite3
import time
from datetime import datetime, timezone
from decouple import config

#https://www.worldometers.info/coronavirus/
#https://www.worldometers.info/coronavirus/#nav-yesterday
#https://www.worldometers.info/coronavirus/usa/texas/ County level

conn = sqlite3.connect('COVID.db')  # You can create a new database by changing the name within the quotes
c = conn.cursor() # The database will be saved in the location where your 'py' file is saved

#Create table - CLIENTS
# c.execute('CREATE TABLE STATES ([generated_id] INTEGER PRIMARY KEY,[State] text, [Total_Cases] INTEGER,[New_Cases] INTEGER,[Total_Deaths] INTEGER,[New_Deaths] INTEGER, [Date] date)')

def LoadUSAData():
    url = 'https://www.worldometers.info/coronavirus/country/us/'
    req = urllib.request.Request(url)
    req.add_header('Content-Type','application/json')
    req.add_header('User-agent','COVID 1.0')

    source = urllib.request.urlopen(req,timeout=120)
    page = source.read()

    soup = bs.BeautifulSoup(page,'html.parser')
    table = soup.findAll("table")
    th = table[0].find("tr")

    headings = []
    for heads in th.findAll("th"):
        headings.append(heads.text)

    states = {}
    for row in table[0].findAll("tr"):
        th = row.find('th')
        td = row.findAll("td")
        index = 0
        stateInfo = ''
        stateName = ''
        totalCases = ''
        newCases = ''
        totalDeaths = ''
        newDeaths = ''
        now = str(datetime.now().date())
        for tds in td:
            if(tds.text.strip() != ''):
                if index == 1:
                    state = tds.text.replace('\n','')
                    stateName = tds.text.replace('\n','').replace(' ','')
                elif index == 2:
                    totalCases = tds.text.replace('\n','').replace(' ','')
                elif index == 3:
                    newCases = tds.text.replace('\n','').replace(' ','') 
                    
                    if newCases != '':
                        newCases = newCases[1:]
                elif index == 4:
                    totalDeaths = tds.text.replace('\n','').replace(' ','')
                elif index == 5:
                    newDeaths = tds.text.replace('\n','').replace(' ','')
                    
                    if newDeaths != '':
                        newDeaths = newDeaths[1:]
                    
            index += 1
        if stateName != '':
            task = (stateName, totalCases,newCases,totalDeaths,newDeaths,now)
            updateTask = (totalCases,newCases,totalDeaths,newDeaths)
            CheckForNewStateData(stateName,newDeaths,newCases,task,updateTask,now)
            LoadCountyLevel(state.lower())
    return states

def LoadCountyLevel(state):
    if ' ' in state:
        state = state.replace(' ','-')
        if state[-1] == '-':
            state = state[:-1]
    url = 'https://www.worldometers.info/coronavirus/usa/' + state
    req = urllib.request.Request(url)
    req.add_header('Content-Type','application/json')
    req.add_header('User-agent','COVID 1.0')

    source = urllib.request.urlopen(req,timeout=120)
    page = source.read()

    soup = bs.BeautifulSoup(page,'html.parser')
    table = soup.findAll("table")
    if(len(table) == 0):
        return
    th = table[0].find("tr")

    headings = []
    for heads in th.findAll("th"):
        headings.append(heads.text)

    states = {}
    for row in table[0].findAll("tr"):
        th = row.find('th')
        td = row.findAll("td")
        index = 0
        countyName = ''
        stateName = ''
        totalCases = ''
        newCases = ''
        totalDeaths = ''
        newDeaths = ''
        now = str(datetime.now().date())
        for tds in td:
            if(tds.text.strip() != ''):
                if index == 0:
                    countyName = tds.text.replace('\n','').replace(' ','')
                elif index == 1:
                    totalCases = tds.text.replace('\n','').replace(' ','')
                elif index == 2:
                    newCases = tds.text.replace('\n','').replace(' ','') 
                    
                    if newCases != '':
                        newCases = newCases[1:]
                elif index == 3:
                    totalDeaths = tds.text.replace('\n','').replace(' ','')
                elif index == 4:
                    newDeaths = tds.text.replace('\n','').replace(' ','')
                    
                    if newDeaths != '':
                        newDeaths = newDeaths[1:]
                    
            index += 1
        if countyName.lower() != '' and 'NotFoundtherequestedwebpagewasnotfound' not in countyName:
            task = (countyName.lower(), totalCases,newCases,totalDeaths,newDeaths,now,state)
            updateTask = (totalCases,newCases,totalDeaths,newDeaths)
            CheckForNewCountyData(countyName,newDeaths,newCases,task,updateTask,now,state)
    return states


def InsertData(task):
    sql = 'INSERT INTO STATES(State,Total_Cases,New_Cases,Total_Deaths,New_Deaths,Date) VALUES(?,?,?,?,?,?)'
    c.execute(sql, task)
    conn.commit()
    
def UpdateData(task, RowID):
    sql = 'UPDATE STATES SET Total_Cases=?,New_Cases=?,Total_Deaths=?,New_Deaths=? WHERE generated_id =' + RowID
    c.execute(sql, task)
    conn.commit()
    
def InsertCountyData(task):
    sql = 'INSERT INTO COUNTIES(County,Total_Cases,New_Cases,Total_Deaths,New_Deaths,Date, state) VALUES(?,?,?,?,?,?,?)'
    c.execute(sql, task)
    conn.commit()
    
def UpdateCountyData(task, RowID):
    sql = 'UPDATE COUNTIES SET Total_Cases=?,New_Cases=?,Total_Deaths=?,New_Deaths=? WHERE pk_id =' + RowID
    c.execute(sql, task)
    conn.commit()

import tweepy
auth = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),config('TWITTER_CONSUMER_SECRET'))
auth.set_access_token(config('TWITTER_ACCESS_KEY'), config('TWITTER_ACCESS_SECRET'))

api = tweepy.API(auth)

def ReplyToTweets(tweetMessage_GOV, message_LT_GOV):
    tweets = api.user_timeline(screen_name='GregAbbott_TX', count=3, exclude_replies=True)
    for tweet in tweets:
        id = tweet.id
        api.update_status(status = tweetMessage_GOV, in_reply_to_status_id = id , auto_populate_reply_metadata=True)
        time.sleep(1)

    tweetsLTGov = api.user_timeline(screen_name='DanPatrick', count=3, exclude_replies=True)
    for tweetLTGov in tweetsLTGov:
        id_LT_GOV = tweetLTGov.id
        api.update_status(status = message_LT_GOV, in_reply_to_status_id = id_LT_GOV , auto_populate_reply_metadata=True)
        time.sleep(1)


def ReplyToRightWingTweets(tweetMessage_OANN, message_NewsMax, message_Cruz):
    tweets = api.user_timeline(screen_name='OANN', count=3, exclude_replies=True)
    for tweet in tweets:
        id = tweet.id
        api.update_status(status = tweetMessage_OANN, in_reply_to_status_id = id , auto_populate_reply_metadata=True)
        time.sleep(1)

    tweetsLTGov = api.user_timeline(screen_name='newsmax', count=3, exclude_replies=True)
    for tweetLTGov in tweetsLTGov:
        id_LT_GOV = tweetLTGov.id
        api.update_status(status = message_NewsMax, in_reply_to_status_id = id_LT_GOV , auto_populate_reply_metadata=True)
        time.sleep(1)
    
    tweetsCruz = api.user_timeline(screen_name='tedcruz', count=3, exclude_replies=True)
    for tweetCruz in tweetsCruz:
        id_Cruz = tweetCruz.id
        api.update_status(status = message_Cruz, in_reply_to_status_id = id_Cruz , auto_populate_reply_metadata=True)
        time.sleep(1)

newData = False
def CheckForNewCountyData(county, newDeaths,newCases, insertTask,updateTask,date,state):
    c.execute("SELECT New_Deaths,New_Cases,Date, pk_id FROM COUNTIES WHERE COUNTY = ? AND STATE = ?  AND Date = ?  ORDER BY pk_id DESC LIMIT 1",
                ("{}".format(county.lower()),state,date))
    row = c.fetchall()
    if len(row) > 0:
        if (str(row[0][0]) != newDeaths and newDeaths.replace(' ','') != '') or (str(row[0][1]) != newCases and newCases.replace(' ','') != ''):
            if date != str(row[0][2]):
                InsertCountyData(insertTask)
                print('New Data Inserted Into Database For: ' + state + ' County: ' + county)
            else:
                UpdateCountyData(updateTask,str(row[0][3]))
                print('Updated Database Entry For: ' + state + ' County: ' + county)
    else:
        InsertCountyData(insertTask)
        print('New Data Inserted Into Database for: ' + state + ' County: ' + county)

def CheckForNewStateData(state, newDeaths,newCases, insertTask,updateTask,date):
    c.execute("SELECT New_Deaths,New_Cases,Date, generated_id FROM STATES WHERE STATE = ? and Date = ?  ORDER BY generated_id DESC LIMIT 1",
                ("{}".format(state),date))
    row = c.fetchall()  
    if len(row) > 0:
        if (str(row[0][0]) != newDeaths and newDeaths != '') or (str(row[0][1]) != newCases and newCases != ''):
            if date != str(row[0][2]):
                InsertData(insertTask)
                print('New Data Inserted Into Database For: ' + state)
            else:
                response = api.rate_limit_status()
                requestsRemaining = response['resources']['application']['/application/rate_limit_status']['remaining']
                resetTimeLeft = response['resources']['application']['/application/rate_limit_status']['reset']
                resetTime = datetime.fromtimestamp(resetTimeLeft)
                try:
                    dt = datetime.now() 
                    utc_time = dt.replace(tzinfo = timezone.utc) 
                    utc_timestamp = utc_time.timestamp()
                    
                    if(state.lower() == 'usatotal') and int(requestsRemaining) >= 12:
                        #message = '@OANN @newsmax ' + newDeaths + ' New Deaths and ' + newCases + ' New Cases in the USA today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse'
                        #api.update_status(message)
                        #time.sleep(1)
                        replyMessage = newDeaths + ' New Deaths and ' + newCases + ' New Cases in the USA today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse'
                        replyMessage2 = newDeaths + ' New Deaths and ' + newCases + ' New Cases in the USA today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse'
                        replyMessageCruz = newDeaths + ' New Deaths and ' + newCases + ' New Cases in the USA today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse #traitor #sedition'
                        ReplyToRightWingTweets(replyMessage,replyMessage2,replyMessageCruz)
                        
                        response = api.rate_limit_status()
                        requestsRemaining = response['resources']['application']['/application/rate_limit_status']['remaining']
                        resetTimeLeft = response['resources']['application']['/application/rate_limit_status']['reset']
                        resetTime = datetime.fromtimestamp(resetTimeLeft)
                        print('Twitter Requests Remaining: ' + str(requestsRemaining) + ' resets at: ' + str(resetTime))
                    elif (state.lower() == 'usatotal') and int(requestsRemaining) <= 12:
                        resetTime = datetime.fromtimestamp(resetTimeLeft).strftime("%I:%M %p")
                        print('Hit Rate Limit, resets at: ' + str(resetTime)) 
                        
                    if(state.lower() == 'texas') and int(requestsRemaining) >= 12:
                        
                            #message = '@GregAbbott_TX @DanPatrick ' + newDeaths + ' New Deaths and ' + newCases + ' New Cases in Texas today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse #AbbottSucks'
                            #api.update_status(message)
                            #time.sleep(1)
                            replyMessage = newDeaths + ' New Deaths and ' + newCases + ' New Cases in Texas today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse #AbbottSucks'
                            replyMessage_LT_GOV = newDeaths + ' New Deaths and ' + newCases + ' New Cases in Texas today (' + str(datetime.today())[:-7] + ') #wearamask #covid #failedresponse #DanPatrickSucks'
                            ReplyToTweets(replyMessage,replyMessage_LT_GOV)
                            response = api.rate_limit_status()
                            requestsRemaining = response['resources']['application']['/application/rate_limit_status']['remaining']
                            resetTimeLeft = response['resources']['application']['/application/rate_limit_status']['reset']
                            resetTime = datetime.fromtimestamp(resetTimeLeft).strftime("%I:%M %p")
                            print('Twitter Requests Remaining: ' + str(requestsRemaining) + ' resets at: ' + str(resetTime))
                            
                    elif (state.lower() == 'texas') and int(requestsRemaining) <= 12:
                        resetTime = datetime.fromtimestamp(resetTimeLeft)
                        print('Hit Rate Limit, resets at: ' + str(resetTime)) 
                except Exception as e:
                    print('Twitter Error:' + str(e))
                    print('Twitter Requests Remaining: ' + str(requestsRemaining) + ' resets at: ' + str(resetTime))
                    pass                  
                UpdateData(updateTask,str(row[0][3]))
                print('Updated Database Entry For: ' + state)
    else:
        InsertData(insertTask)
        print('New Data Inserted Into Database for: ' + state)
while True:
    try:
        data = LoadUSAData()
        print('CHecked For New Data at: ' + '(' + str(datetime.today())[:-7] + ')')
        time.sleep(60)
    except Exception as e:
        print('Failed network connection')
        time.sleep(10)    



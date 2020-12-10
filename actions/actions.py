from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import AllSlotsReset

import requests
import mysql.connector
import json
from mysql.connector import Error

import dateparser
from dateparser.search import search_dates
import datetime
from datetime import datetime


class ResetAllSlots(Action):

    def name(self)-> Text:
        return "action_reset_slot"
    
    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]

class checkweatherform(Action):
    def name(self)-> Text:
        return "check_weather"
    
    def run(self, dispatcher, tracker, domain):
        api_key = 'ac786f44c4392ca790661642d4b9a06b'
        user = tracker.sender_id
        loc = tracker.get_slot('GPE')
        current = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(loc, api_key)).json()
        print(current)
        country = current['sys']['country']
        city = current['name']
        condition = current['weather'][0]['main']
        temperature_c = current['main']['temp']
        temperature = int(temperature_c-273)
        humidity = current['main']['humidity']
        wind_mph = current['wind']['speed']
        response = """It is currently {} in {} at the moment. The temperature is {} degrees, the humidity is {}% and the wind speed is {} mph.""".format(condition, city, temperature, humidity, wind_mph)
        dispatcher.utter_message(response)
        return [SlotSet('GPE', loc)]

class ActionRecommendRestaurant(Action):

    def name(self)-> Text:
        return "action_recommend_restaurant"
    
    def run(self, dispatcher, tracker, domain):
        account = 'L7RMFP60'
        token = 'pej8xrl3qwlaa4bqe4bj2w5ofqe9mrj4'
        loc =  tracker.get_slot('GPE')
        user = tracker.sender_id
        loc = loc.title()
        current = requests.get('https://www.triposo.com/api/20200803/poi.json?location_id={}&tag_labels=eatingout&count=3&fields=id,name,score,intro,tag_labels,best_for&order_by=-score&account={}&token={}'.format(loc, account, token)).json()

        print(json.dumps(current, indent=1))
        for i in range(0,3):
            name=current['results'][i]['name']
            print(name)
            intro=current['results'][i]['intro']
            print(intro)
            response = """ {} =>  {}""".format(name,intro)
            dispatcher.utter_message(response)
        return [SlotSet('GPE', loc)]


class CreateListform(Action):

    def name(self)-> Text:
        return "action_create_list"

    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        list_name = tracker.get_slot('list_name')
        user = tracker.sender_id
        item_name = tracker.get_slot('item')
        item_list = item_name.split(",")
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        for i in item_list:
            sql = "INSERT INTO ToDoList (id,username,listname,item,status) VALUES (%s,%s,%s,%s,%s)"
            val = (0,user, list_name, i, 0)
            cur.execute(sql, val)
            print("done")
            conn.commit() 
        cur.close()           
        conn.close()

        res = """{} List Created with item {}""".format(list_name,item_name)
        dispatcher.utter_message(res)
        return [SlotSet('list_name', list_name)]

class SaveActivityForm(Action):

    def name(self)-> Text:
        return "action_save_activity"

    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        user = tracker.sender_id
        act_type = tracker.get_slot('act_type')
        act = tracker.get_slot('activity')
        date_time = tracker.get_slot('date_time')
        other = tracker.get_slot('others')
        
        b=dateparser.parse(date_time, settings={'TIMEZONE': '+0530'})
        date=b.date()
        time=b.time()
        if(time==""):
            time = datetime.now().time()
        if(date==""):
            date = date.today()

        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql = "INSERT INTO timeline (id,user,tripname,activity,date_activity,time_activity,other) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (0,user,act_type,act,date,time,other)
        cur.execute(sql, val)
        print("done")
        conn.commit() 
        cur.close()           
        conn.close()

        res = """ {} details saved""".format(act_type)
        dispatcher.utter_message(res)
        return 

class ShowList(Action):

    def name(self)-> Text:
        return "action_show_list"
    
    def run(self, dispatcher, tracker, domain):
        
        list_name= tracker.get_slot('list_name')
        user = tracker.sender_id
        if (list_name=="all"):
            conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
            cur=conn.cursor()
            sql1 = "SELECT listname FROM ToDoList WHERE username=%s"
            val1=(user,)
            cur.execute(sql1,val1)
            result=cur.fetchall()
            result = list(dict.fromkeys(result))
            i = 0
            print(result)
            for x in result:
                i=i+1
            for y in range(0,i):
                print(result[y][0])
            for z in range (0,i):
                response = """{}""".format(result[z][0])
                dispatcher.utter_message(response)
            conn.commit()
            cur.close()       
            conn.close()
            return [SlotSet('list_name', list_name)]


        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql1 = "SELECT item FROM ToDoList WHERE username=%s and listname=%s and status=%s"
        val1=(user,list_name,0)
        cur.execute(sql1,val1)
        result=cur.fetchall()
        i = 0
        print(result)
        for x in result:
            i=i+1
        for y in range(0,i):
            print(result[y][0])
        for z in range (0,i):
            response = """{}""".format(result[z][0])
            dispatcher.utter_message(response) 
        conn.commit()
        cur.close()       
        conn.close()

        res = """Theese are the items in {}""".format(list_name)
        dispatcher.utter_message(res)
        return [SlotSet('list_name', list_name)]

class AddToList(Action):

    def name(self)-> Text:
        return "action_add_to_list"
    
    def run(self, dispatcher, tracker, domain):
        
        list_name = tracker.get_slot('list_name')
        user = tracker.sender_id
        item_name = tracker.get_slot('item')
        item_list = item_name.split(",")
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        for i in item_list:
            sql = "INSERT INTO ToDoList (id,username,listname,item,status) VALUES (%s,%s,%s,%s,%s)"
            val = (0, user, list_name, i, 0)
            cur.execute(sql, val)
            print("done")
            conn.commit()      
        cur.close() 
        conn.close()       
        response = """{} the following item is added to {}""".format(item_name,list_name)
        dispatcher.utter_message(response)
        return [SlotSet('list_name', list_name)]

class MarkItem(Action):

    def name(self)-> Text:
        return "action_mark_item"
    
    def run(self, dispatcher, tracker, domain):
        
        list_name = tracker.get_slot('list_name')
        user = tracker.sender_id
        item_name = tracker.get_slot('item')
        item_list = item_name.split(",")       
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        for i in item_list:
            sql = "UPDATE ToDoList SET status=1 where username=%s and listname=%s and item=%s"
            val = (user,list_name,i)
            cur.execute(sql,val)
            conn.commit()
        cur.close()     
        conn.close()
        
        res = """{} item marked in {}""".format(item_name,list_name)
        dispatcher.utter_message(res)
        return [SlotSet('list_name', list_name)]

class AddExpenseform(Action):

    def name(self)-> Text:
        return "action_add_expense"

    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        user = tracker.sender_id
        act = tracker.get_slot('activity')
        date_time = tracker.get_slot('date_time')
        money = tracker.get_slot('MONEY')
        
        b=dateparser.parse(date_time, settings={'TIMEZONE': '+0530'})
        date=b.date()
        time=b.time()
        if(time==""):
            time = datetime.now().time()
        if(date==""):
            date = date.today()
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql = "INSERT INTO budget (id,username,money,activity,date,time,status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (0,user,money,act,date,time,0)
        cur.execute(sql, val)
        print("done")
        conn.commit() 
        cur.close()           
        conn.close()

        res = """ {} money spent on {} """.format(money,act)
        dispatcher.utter_message(res)
        return

class DeleteList(Action):

    def name(self)-> Text:
        return "action_delete_list"
    
    def run(self, dispatcher, tracker, domain):
        
        list_name= tracker.get_slot('list_name')
        user = tracker.sender_id
        if (list_name=="all"):
            conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
            cur=conn.cursor()
            sql1 = "DELETE FROM ToDoList WHERE username=%s"
            val1=(user,)
            cur.execute(sql1,val1)
            response = """All the list for user {} has been deleted""".format(user)
            dispatcher.utter_message(response)
            conn.commit() 
            cur.close()       
            conn.close()
            return [SlotSet('list_name', list_name)]


        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql1 = "DELETE FROM ToDoList WHERE username=%s and listname=%s"
        val1=(user,list_name)
        cur.execute(sql1,val1)
        response = """{} has been deleted for user {}""".format(list_name,user)
        dispatcher.utter_message(response)
        conn.commit() 
        cur.close()       
        conn.close()
        return [SlotSet('list_name', list_name)]

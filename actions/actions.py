from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

import requests
import mysql.connector
import json
from mysql.connector import Error

import dateparser
from dateparser.search import search_dates
import datetime
from datetime import datetime


class ActionCheckWeather(Action):

    def name(self)-> Text:
        return "action_get_weather"
    
    def run(self, dispatcher, tracker, domain):
        api_key = 'ac786f44c4392ca790661642d4b9a06b'
        loc = tracker.get_slot('GPE')
        current = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(loc, api_key)).json()
        print(current)
        country = current['sys']['country']
        city = current['name']
        condition = current['weather'][0]['main']
        temperature_c = current['main']['temp']
        humidity = current['main']['humidity']
        wind_mph = current['wind']['speed']
        response = """It is currently {} in {} at the moment. The temperature is {} degrees, the humidity is {}% and the wind speed is {} mph.""".format(condition, city, temperature_c, humidity, wind_mph)
        dispatcher.utter_message(response)
        return [SlotSet('GPE', loc)]

class ActionRecommendRestaurant(Action):

    def name(self)-> Text:
        return "action_recommend_restaurant"
    
    def run(self, dispatcher, tracker, domain):
        account = 'L7RMFP60'
        token = 'pej8xrl3qwlaa4bqe4bj2w5ofqe9mrj4'
        loc =  tracker.get_slot('GPE')
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


class validateCreateListform(Action):

    def name(self)-> Text:
        return "validate_create_list_form"

    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        required_slots = ["list_name", "item"]
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]
        
        list_name = tracker.get_slot('list_name')
        user = tracker.get_slot('user')
        item_name = tracker.get_slot('item')
        
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql = "INSERT INTO ToDoList (id,username,listname,item,status) VALUES (%s,%s,%s,%s,%s)"
        val = (0,"aayush", list_name, item_name, 0)
        cur.execute(sql, val)
        print("done")
        conn.commit() 
        cur.close()           
        conn.close()

        res = """{} List Created with item {}""".format(list_name,item_name)
        dispatcher.utter_message(res)
        return [SlotSet('list_name', list_name)]

class validateSaveActivityForm(Action):

    def name(self)-> Text:
        return "validate_save_activity_form"

    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        required_slots = ["act_type", "activity", "date_time"]
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]
        
        act_type = tracker.get_slot('act_type')
        act = tracker.get_slot('activity')
        date_time = tracker.get_slot('date_time')
        other = tracker.get_slot('others')
        
        b=dateparser.parse(date_time, settings={'TIMEZONE': '+0530'})
        date=b.date()
        time=b.time()
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql = "INSERT INTO timeline (id,user,tripname,activity,date_activity,time_activity,other) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (0,"test",act_type,act,date,time,other)
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
        user= tracker.get_slot('user')

        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql1 = "SELECT item FROM ToDoList WHERE listname=%s and status=%s"
        val1=(list_name,0)
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
        user = tracker.get_slot('user')
        item_name = tracker.get_slot('item')

        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql = "INSERT INTO ToDoList (id,username,listname,item,status) VALUES (%s,%s,%s,%s,%s)"
        val = (0, "aayush", list_name, item_name, 0)
        cur.execute(sql, val)
        print("done")
        conn.commit()
               
        conn.close()
        
        response = """{} the following item is added to {}""".format(item_name,list_name)
        dispatcher.utter_message(response)
        return [SlotSet('item', item_name)],[SlotSet('list_name'), list_name]

class MarkItem(Action):

    def name(self)-> Text:
        return "action_mark_item"
    
    def run(self, dispatcher, tracker, domain):
        
        list_name = tracker.get_slot('list_name')
        user = tracker.get_slot('user')
        item_name = tracker.get_slot('item')

        
        conn = mysql.connector.connect(host='remotemysql.com',
                                         database='znQpgumjmV',
                                         user='znQpgumjmV',
                                         password='p55RkgsiKw')
        cur=conn.cursor()
        sql = "UPDATE ToDoList SET status=1 where listname=%s and item=%s"
        val = (list_name,item_name)
        cur.execute(sql,val)
        conn.commit()
        cur.close()     
        conn.close()
        
        res = """{} item marked in {}""".format(item_name,list_name)
        dispatcher.utter_message(res)
        return [SlotSet('list_name', list_name)]



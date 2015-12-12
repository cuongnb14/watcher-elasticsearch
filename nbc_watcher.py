#! /usr/bin/env python3
import threading
import logging
import json
import schedule 
import smtplib
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Watcher:
    """Class watching the logs
    
    Class will base conditions to implement actions
    """
    actions = []
    conditions = []
    def __init__(self,configs_file):
        """Init Object base on file config
    
        @param string configs_file, name of file json config
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Loading config file...")
        with open(configs_file) as configs_file:    
            self.configs = json.load(configs_file)
        self.logger.info("Create searcher...")
        self.searcher = Elasticsearch(self.configs["eslaticsearch"])

    def add_action(self,action):
        """Add action for watcher

        @param function action, is a function have only one param (response of Elasticsearch.search)
        """
        self.logger.info("add action "+action.__name__)
        self.actions.append(action)

    def add_condition(self,condition):
        """Add condition for watcher

        @param function condition, is a function have only one param (response of Elasticsearch.search) and return boolean value
        """
        self.logger.info("add condition "+condition.__name__)
        self.conditions.append(condition)

    def add_send_gmail_action(self):
        """Action buil-in class Watcher, send gmail action"""
        def send_gmail_action(response):
            msg = MIMEMultipart()
            msg['Subject'] = 'NBC Watcher Notification'
            msg['From'] = self.configs["action"]["gmail"]["from"]["user"]
            msg['To'] = self.configs["action"]["gmail"]["to"]["user"]
            text_msg = MIMEText(self.configs["action"]["gmail"]["msg"].format(response=response), 'plain')
            msg.attach(text_msg)

            gmail = smtplib.SMTP('smtp.gmail.com:587')
            gmail.ehlo()
            gmail.starttls()
            gmail.login(self.configs["action"]["gmail"]["from"]["user"], self.configs["action"]["gmail"]["from"]["pass"])
            gmail.sendmail(self.configs["action"]["gmail"]["from"]["user"], self.configs["action"]["gmail"]["to"]["user"], msg)
            gmail.quit()
        self.add_action(send_gmail_action)

    def send_to_logs_action(self):
        def to_logs_action(response):
            self.logger.info(self.configs["action"]["logs"]["format"].format(response=response))
        self.add_action(to_logs_action)

    def watching(self):
        """Query logs in eslaticsearch and compare condition then implement action"""
        self.logger.info("Searching in eslaticsearch...")
        response = self.searcher.search(index=self.configs["index"], body=self.configs["search"])
        self.logger.info("Totol hits: "+ str(response['hits']['total']))
        self.logger.debug(response)
        result = True
        self.logger.info("Checking conditions...")
        for condition in self.conditions:
            result = result and condition(response)

        self.logger.info("Result = "+str(result))
        if(result == True):
            for action in self.actions:
                try:
                    self.logger.info("Implement action "+action.__name__)
                    action_thread = threading.Thread(target=action,args=(response,), daemon = True)
                    action_thread.start()
                except Exception:
                    pass

    def run(self):
        """Run watcher"""
        self.logger.info("Running watcher ...")
        schedule.every(self.configs["interval"]).seconds.do(self.watching)
        while True:
            schedule.run_pending()








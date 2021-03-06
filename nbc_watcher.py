import json
import logging
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import schedule
from elasticsearch import Elasticsearch
from apscheduler.schedulers.background import BlockingScheduler


class Watcher:
    """Class watching the log

    Class will base conditions to implement actions
    """
    actions = []
    conditions = []

    def __init__(self, config_file):
        """Init Object base on file config

        @param string config_files, name of file json config
        """
        logging.getLogger("apscheduler.executors.default").setLevel("ERROR")
        logging.getLogger("elasticsearch").setLevel("ERROR")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Loading config file...")
        with open(config_file) as config_file:
            self.config = json.load(config_file)
        self.logger.info("Create searcher...")
        self.searcher = Elasticsearch(self.config["eslaticsearch"])

    def add_action(self, action):
        """Add action for watcher

        @param function action, is a function have only one param (response of Elasticsearch.search)
        """
        self.logger.info("add action " + action.__name__)
        self.actions.append(action)

    def add_condition(self, condition):
        """Add condition for watcher

        @param function condition, is a function have only one param (response of Elasticsearch.search) and return boolean value
        """
        self.logger.info("add condition " + condition.__name__)
        self.conditions.append(condition)

    def add_send_gmail_action(self):
        """Action built-in class Watcher, send gmail action"""

        def send_gmail_action(response):
            msg = MIMEMultipart()
            msg['Subject'] = 'NBC Watcher Notification'
            msg['From'] = self.config["actions"]["gmail"]["from"]["user"]
            msg['To'] = self.config["actions"]["gmail"]["to"]["user"]
            text_msg = MIMEText(self.config["actions"]["gmail"]["msg"].format(response=response), 'plain')
            msg.attach(text_msg)

            gmail = smtplib.SMTP('smtp.gmail.com:587')
            gmail.ehlo()
            gmail.starttls()
            gmail.login(self.config["actions"]["gmail"]["from"]["user"],
                        self.config["actions"]["gmail"]["from"]["pass"])
            gmail.sendmail(self.config["actions"]["gmail"]["from"]["user"],
                           self.config["actions"]["gmail"]["to"]["user"], msg)
            gmail.quit()

        self.add_action(send_gmail_action)

    def add_send_log_action(self):
        def send_log_action(response):
            self.logger.info(self.config["actions"]["log"]["format"].format(response=response))

        self.add_action(send_log_action)

    def watching(self):
        """Query log in eslaticsearch and compare condition then implement action"""
        self.logger.info("Searching in eslaticsearch...")
        response = self.searcher.search(index=self.config["index"], body=self.config["search"])
        self.logger.debug("Total hits: " + str(response['hits']['total']))
        self.logger.debug(response)

        result = True
        self.logger.debug("Checking conditions...")
        for condition in self.conditions:
            result = result and condition(response)

        self.logger.debug("Result = " + str(result))
        if (result == True):
            for action in self.actions:
                try:
                    self.logger.debug("Implement action " + action.__name__)
                    action_thread = threading.Thread(target=action, args=(response,), daemon=True)
                    action_thread.start()
                except Exception as e:
                    self.logger.error(e)

    def run(self):
        """Run watcher"""
        self.logger.info("Running watcher ...")
        scheduler = BlockingScheduler()
        scheduler.add_job(self.watching, 'interval', seconds=self.config["interval"])
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

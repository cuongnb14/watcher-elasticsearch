#!/usr/bin/env python3

import logging
import sys

from nbc_watcher import Watcher


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    def total_condition(response):
        return response['hits']['total'] > 0

    watcher = Watcher("config.json")

    # watcher.add_send_gmail_action()
    watcher.add_send_log_action()
    watcher.add_condition(total_condition)
    watcher.run()


if __name__ == '__main__':
    main()

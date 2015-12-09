from nbc_watcher import Watcher

def main():

    def total_condition(response):
        return response['hits']['total'] > 0

    watcher = Watcher("configs.json")

    watcher.add_send_gmail_action()
    watcher.add_condition(total_condition)
    watcher.run()


if __name__ == '__main__':
    main()
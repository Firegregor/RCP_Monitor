import os
import datetime
import logging
from collections import defaultdict

class RcpMonitor:
    def __init__(self, storage="~/.config/RCP_Monitor"):
        logging.info("RcpMonitor Init")
        self._log_dir = os.path.expanduser(storage)
        self._log_file = os.path.join(self._log_dir, "time.log")
        logging.debug(f"RcpMonitor storage in {self._log_file}")
        self._pattern = "%d-%m-%Y %H:%M:%S"
        self.log = []
        self.worktime = {"day":defaultdict(datetime.timedelta), "week":0}
        self.cw = datetime.date.today().isocalendar()[1]
        self.load_log()
        self.process_log()

    def process_log(self):
        last = None
        self.worktime = {"day":defaultdict(datetime.timedelta), "week":0}
        for entry in self.log:
            if last == None:
                last = entry
                continue
            if last.date is entry.date:
                logging.error("Logs corrupted at {entry.strftime(self._pattern)}")
                break
            passed = entry - last
            self.worktime['day'][last.date()] += passed
            last = None
        for day,time in self.worktime['day'].items():
            if day.isocalendar()[1] == self.cw:
                self.worktime['week'] += time.total_seconds()/60

    def save_time(self):
        logging.info("RcpMonitor save time")
        now = datetime.datetime.now().replace(second=0)
        self.log.append(now)
        self.save_log()
        return self.process_log()

    def load_log(self):
        logging.info("RcpMonitor load logs")
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        if not os.path.exists(self._log_file):
            logging.warning("No logs")
            open(self._log_file, "a+")
        with open(self._log_file, "r") as log:
            for line in log:
                self.log.append(datetime.datetime.strptime(line.strip(), self._pattern))

    def save_log(self):
        logging.info("RcpMonitor save logs")
        with open(self._log_file, 'w') as log:
            for entry in self.log:
                log.write(f"{entry.strftime(self._pattern)}\n")

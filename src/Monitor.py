import os
import datetime as dt
import logging
from collections import defaultdict

class RcpMonitor:

    WORKDAY = dt.timedelta(hours=8).total_seconds()//60
    LOG_SPAN = dt.timedelta(days=62)

    def __init__(self, storage="./res", synch_addr=None):
        logging.info("RcpMonitor Init")
        self._synch = synch_addr
        self._log_dir = os.path.expanduser(storage)
        self._log_file = os.path.join(self._log_dir, "time.log")
        logging.debug(f"RcpMonitor storage in {self._log_file}")
        self._pattern = "%d-%m-%Y %H:%M:%S"
        self.remote_log = []
        self.log = []
        self.worktime = {"day":defaultdict(dt.timedelta), "week":0}
        self.cw = dt.date.today().isocalendar()[1]
        self.month = dt.date.today().month
        self.get_remote()
        self.load_log(self._log_file, self.log)
        self.merge()
        self.process_log()
        try:
            if self.log[-1].date() != dt.date.today():
                self.save_time()
        except IndexError:
            self.save_time()

    def merge(self):
        logging.info(f"RcpMonitor merging logs {len(self.log)} with remote {len(self.remote_log)}")
        final = set(self.log)
        for line in self.remote_log:
            if line in final:
                continue
            entry = dt.datetime.strptime(line.strip(), self._pattern)
            if self.LOG_SPAN > (now - entry.date()):
                logging.info(f"New Entry: {line}")
                final.add(line)
        self.log = list(final)
        self.log.sort()
        self.save_log()

    def send_remote(self):
        if self._synch is None:
            logging.info("No synchronization address defined")
            return
        os.system(f"scp {self._log_file} {self._synch}")

    def get_remote(self):
        if self._synch is None:
            logging.info("No synchronization address defined")
            return
        logging.info(f"RcpMonitor synchronising with {self._synch}")
        remote_file = os.path.join(self._log_dir, "tmp.log")
        os.system(f"scp {self._synch} {remote_file}")
        self.load_log(remote_file,self.remote_log)
        os.remove(remote_file)

    def save_time(self):
        logging.info("RcpMonitor save time")
        now = dt.datetime.now().replace(second=0)
        self.log.append(now)
        self.save_log()
        return self.process_log()

    def load_log(self, _file, entries):
        logging.info(f"RcpMonitor load logs from file {_file}")
        now = dt.date.today()
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        if not os.path.exists(_file):
            logging.warning("No logs")
            open(self._log_file, "a+")
        with open(self._log_file, "r") as log:
            for line in log:
                entry = dt.datetime.strptime(line.strip(), self._pattern)
                if self.LOG_SPAN > (now - entry.date()):
                    entries.append(entry)

    def save_log(self):
        logging.info("RcpMonitor save logs")
        with open(self._log_file, 'w') as log:
            for entry in self.log:
                log.write(f"{entry.strftime(self._pattern)}\n")

    def process_log(self):
        last = None
        self.worktime = {"day":defaultdict(dt.timedelta), "month":0, "week":0, "total":0}
        if self.log is None:
            logging.warning("Trying to process empty log")
            return
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
        if dt.date.today() not in self.worktime['day']:
            self.worktime['day'][dt.date.today()] = dt.timedelta()
        for day,time in self.worktime['day'].items():
            if day.month == self.month:
                self.worktime['month'] += time.total_seconds()/60
            if day.isocalendar()[1] == self.cw:
                self.worktime['week'] += time.total_seconds()/60
                self.worktime['total'] += self.WORKDAY

    def get_ttw(self):
        now = dt.datetime.now()
        working = len(self.log)%2
        current = working * (now - self.log[-1]).total_seconds()//60
        today_worked = self.worktime['day'][dt.date.today()].total_seconds()//60 + current
        ttw = self.worktime["total"] - self.worktime["week"] - current
        if ttw < 0:
            ttw = - ttw
            overtime = True
        else:
            overtime = False
        hours = int(ttw//60)
        minutes = int(ttw - 60*hours)
        out_time = now +dt.timedelta(hours=hours, minutes=minutes)
        teoretical = now + dt.timedelta(minutes=self.WORKDAY - today_worked)
        out = f"\nTeoretical {teoretical.strftime('%H:%M')}, but out at {out_time.strftime('%H:%M')}" if (working and not overtime) else f"\n8 hours at {teoretical.strftime('%H:%M')}"
        today = f"{today_worked//60:02.0f}:{today_worked%60:02.0f} / 8:00"
        week = f"left {hours:02.0f}:{minutes:02.0f} to work" if not overtime else f"{hours:02.0f}:{minutes:02.0f} overtime"
        return_string = f"{today} {week}{out}"
        return (return_string, working)

    def get_total_month(self):
        now = dt.datetime.now()
        working = len(self.log)%2
        current = working * (now - self.log[-1]).total_seconds()//60
        today_worked = self.worktime['day'][dt.date.today()].total_seconds()//60 + current
        ttw = self.worktime["total"] - self.worktime["week"] - current
        if ttw < 0:
            ttw = - ttw
            overtime = True
        else:
            overtime = False
        hours = int(ttw//60)
        minutes = int(ttw - 60*hours)
        today = f"{today_worked//60:02.0f}:{today_worked%60:02.0f} / 8:00"
        week = f"left {hours:02.0f}:{minutes:02.0f} to work" if not overtime else f"{hours:02.0f}:{minutes:02.0f} overtime"
        month = f"{self.worktime['month']//60:0.0f} hours this month"
        return_string = f"{today}\n{week}\n{month}"
        return (return_string, working)

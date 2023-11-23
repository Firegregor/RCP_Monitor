import os
import datetime as dt
import logging
from collections import defaultdict

class RcpMonitor:

    WORKDAY = dt.timedelta(hours=8).total_seconds()//60
    LOG_SPAN = dt.timedelta(days=62)

    def __init__(self, storage="~/.config/RCP_Monitor"):
        logging.info("RcpMonitor Init")
        self._log_dir = os.path.expanduser(storage)
        self._log_file = os.path.join(self._log_dir, "time.log")
        logging.debug(f"RcpMonitor storage in {self._log_file}")
        self._pattern = "%d-%m-%Y %H:%M:%S"
        self.log = []
        self.worktime = {"day":defaultdict(dt.timedelta), "week":0}
        self.cw = dt.date.today().isocalendar()[1]
        self.month = dt.date.today().month
        self.load_log()
        self.process_log()
        if self.log[-1].date() != dt.date.today():
            self.save_time()

    def save_time(self):
        logging.info("RcpMonitor save time")
        now = dt.datetime.now().replace(second=0)
        self.log.append(now)
        self.save_log()
        return self.process_log()

    def load_log(self):
        logging.info("RcpMonitor load logs")
        now = dt.date.today()
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        if not os.path.exists(self._log_file):
            logging.warning("No logs")
            open(self._log_file, "a+")
        with open(self._log_file, "r") as log:
            for line in log:
                entry = dt.datetime.strptime(line.strip(), self._pattern)
                if self.LOG_SPAN > (now - entry.date()):
                    self.log.append(entry)

    def save_log(self):
        logging.info("RcpMonitor save logs")
        with open(self._log_file, 'w') as log:
            for entry in self.log:
                log.write(f"{entry.strftime(self._pattern)}\n")

    def process_log(self):
        last = None
        self.worktime = {"day":defaultdict(dt.timedelta), "month":0, "week":0, "total":0}
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
        out = f"\nTeoretical {teoretical.strftime('%H:%M')}, but out at {out_time.strftime('%H:%M')}" if (working and not overtime) else "\8 hours at {teoretical.strftime('%H:%M')}"
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

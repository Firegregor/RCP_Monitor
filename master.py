from src import RcpMonitor
import datetime

if __name__ == "__main__":
    print("RCP_Monitor started")
    mon = RcpMonitor()
    mon.save_time()
    for key,val in mon.worktime['day'].items():
        print(f"{key}\n{val}")
    print(mon.worktime["week"]/60)

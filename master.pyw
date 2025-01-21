from src import RcpMonitor, RcpGui
import sys
import logging

REMOTE="gkot@91.225.132.94:Rcp/time.log"

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("RCP_Monitor started")
    mon = RcpMonitor(synch_addr=REMOTE)
    if len(sys.argv) == 1:
        RcpGui(
            mon.save_time,
            mon.get_ttw,
            mon.get_total_month,
            (mon.get_remote,
            mon.send_remote)
            )
        return
    if sys.argv[1] == "test":
        RcpGui(
            lambda: print("save time"),
            lambda: ("Time to work", False),
            lambda: ("Total Month", True)
            )
    if sys.argv[1] == "gui":
        for key,val in mon.worktime['day'].items():
            print(f"{key}\n{val}")
        print(mon.worktime["week"]/60)


if __name__ == "__main__":
    main()

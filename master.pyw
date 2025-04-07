from src import RcpMonitor, RcpGui, config
import sys
import logging


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("RCP_Monitor started")
    config["update"]()
    mon = RcpMonitor(config["monitor"])
    if len(sys.argv) == 1:
        RcpGui(
            config["gui"],
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

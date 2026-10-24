import time
from risk.governor import RiskGovernor

def main():
    governor = RiskGovernor()
    print("execution engine online; live execution is gated")
    while True:
        governor.heartbeat()
        time.sleep(5)

if __name__ == "__main__":
    main()

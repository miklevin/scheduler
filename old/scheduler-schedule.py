import shlex
# import schedule
from time import sleep
from os import environ
from sys import stdout
from subprocess import Popen, PIPE
from sqlitedict import SqliteDict as sqldict
from datetime import datetime, date, timedelta
from schedule import every, repeat, run_pending, CancelJob


pulse_count = 0
print("The pulse service has started.")


def run(command, cwd=None):
    process = Popen(
        shlex.split(command),
        stdout=PIPE,
        cwd=cwd,
        bufsize=1,
        universal_newlines=True,
        shell=False,
    )
    for line in process.stdout:
        line = line.rstrip()
        print(line)
        stdout.flush()


def seconds_from_now(secs):
    today = date.today()
    atime = datetime.now().time()
    asoon = datetime.combine(today, atime) + timedelta(seconds=secs)
    return asoon


@repeat(every(60).seconds)
def pulse():
    global pulse_count
    pulse_count += 1
    anow = f"{pulse_count} - {datetime.now()}"
    with open('/tmp/scheduler.txt', 'a') as fh:
        print(f"{anow} logged.")
        fh.write((anow) + '\n')


@repeat(every().day.at(seconds_from_now(5).strftime("%H:%M:%S")))
def sendcats():
    print("Sending email")
    pyx = "/home/ubuntu/py310/bin/python3.10"
    cwd = "/home/ubuntu/github/scheduler/"
    cmd = f"{pyx} {cwd}sendcats.py"
    run(cmd, cwd=cwd)
    anow = f"{datetime.now()}"
    return CancelJob


while True:
    run_pending()
    sleep(1)

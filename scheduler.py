import shlex
from time import sleep
from os import environ
from sys import stdout
from subprocess import Popen, PIPE
from huey import SqliteHuey, crontab
from datetime import datetime, date, timedelta


huey = SqliteHuey(filename='/tmp/scheduler.db')

pulse_count = 0
print("The pulse service has started using Huey.")


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


@huey.periodic_task(crontab(minute='*/1'))
def pulse():
    global pulse_count
    pulse_count += 1
    anow = f"{pulse_count} - {datetime.now()}"
    with open('/tmp/scheduler.txt', 'a') as fh:
        print(f"{anow} EVERY MINUTE FROM HUEY.")
        fh.write((anow) + '\n')

in5secs = seconds_from_now(60)
anhour = in5secs.hour
aminute = in5secs.minute

@huey.periodic_task(crontab(hour=anhour, minute=aminute))
def sendcats():
    print("Sending email")
    pyx = "/home/ubuntu/py310/bin/python3.10"
    cwd = "/home/ubuntu/github/scheduler/"
    cmd = f"{pyx} {cwd}sendcats.py"
    run(cmd, cwd=cwd)



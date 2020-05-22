from threading import Timer
import asyncio
import time

def timeout():
    print("it stopped")

t = Timer(5, timeout)
t.start()
while True:
    print("lol")
    time.sleep(1)
#t.join()
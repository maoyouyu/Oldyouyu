import threading
import time
from queue import Queue

def threadings_add():
	print('This is job /n')
	for i in range(10):
		time.sleep(0.1)
	print('T1 FINISH /n')

def T2_job():
	print('T2 start /n')
	print('T2 FINISH /n')

def main():
	threading_adds = threading.Thread(target=threadings_add)
	threading_adds.start()
	T2 = threading.Thread(target=T2_job)
	T2.start()
	threading_adds.join()
	print('all done')

if __name__=='__main__':
	main()


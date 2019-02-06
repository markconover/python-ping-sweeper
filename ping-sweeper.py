#!/usr/bin/python

# Ping Sweep Example
# Uses multithreading and queue to quickly determine
# which hosts are alive within a specified ip range

import subprocess
import threading
import time

class Pingy(object):
    
    # Contains lists of alive hosts and dead hosts
    status = {'alive': [], 'dead': []}
    
    # List of all ipv4 addresses in the input queue
    hosts = [] 

    # How many ping process at the time.
    thread_count = 4

    # Lock object to keep track the threads in loops, 
    # where race conditions can exist
    lock = threading.Lock()

    def ping(self, ip):
        # Use the system's ping command with a count of 1 and a wait time of 1
        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
            stdout = open('/dev/null', 'w'), stderr = open('/dev/null', 'w'))

        # Return True if the ping command is successful
        return ret == 0 

    def pop_queue(self):
        ip = None

        # Take hold of or wait and take hold of the lock
        self.lock.acquire() 

        if self.hosts:
            ip = self.hosts.pop()

        # Release the lock so another thread 
        # can take hold of it
        self.lock.release()

        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            if self.ping(ip):
                result = 'alive'
            else:
                result = 'dead'

            self.status[result].append(ip)

    def start(self):
        threads = []

        for i in range(self.thread_count):
            # All threads will communicate in order to
            # ping each ip in the hosts list.
            # Each thread will do the job as fast as it can.
            t = threading.Thread(target = self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        for t in threads:
            t.join()

        return self.status

        
def main():

    # Get starting time
    starting_time = time.time()
    
    pingy = Pingy()
    pingy.thread_count = 8
    
    ip_list = []
    nrange = '10.11.1.'
    for ip_suffix in range(1, 255): 
        ipv4_address = nrange + str(ip_suffix)
        ip_list.append(ipv4_address)
    
    pingy.hosts = ip_list

    final_status = pingy.start()
  
    print 'Printing out the hosts that are alive...:'
    for i in final_status['alive']:
        print i
        
    #print 'Printing out the hosts that are dead...:'
    #for i in final_status['dead']:
    #    print i
    
    # Calculate elapsed time it took this program to complete
    elapsed_time = time.time() - starting_time
    print 'Execution of this program took: %s seconds' % elapsed_time

if __name__ == '__main__':
    main()

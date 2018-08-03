#coding=utf-8

import time, sys

class ProgressDisplay(object):
    def __init__(self, todo_length):
        self.start_time = time.time()
        self.todo_length = todo_length
    
    def display_progress(self, finished_n):
        if finished_n > 0:
            delta = time.time() - self.start_time
            remaining_time = int(delta / finished_n * (self.todo_length - finished_n))
            sys.stdout.write('{0:5}/{1:5}  eta:{2:5}s\r'.format(finished_n, self.todo_length, remaining_time))
            sys.stdout.flush()
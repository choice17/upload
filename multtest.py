

import sys
import time
from multiprocessing import Process, Pipe, Queue, Array, Value, RawArray, Lock
import numpy as np

NUM = 20
W,H,C = 1600,1200,3

def worker_arr_raw(arr, arrs, arrstr, qr):
    for task_nbr in range(NUM):
        #conn.send(np.random.rand(W, H, C))
        #array = -np.frombuffer(arr, dtype=np.int32)
        #Arr = np.frombuffer(arr,dtype=np.float32)
        #memoryview(arrs).cast('B').cast('f')[:] = np.array([np.random.rand(),4,5,time.time()],dtype=np.float32)
        arrs[0] = np.random.rand()
        arrs[1] = 3
        arrs[2] = 4
        arrs[3] = time.time()
        #np.copyto(Arr, np.random.rand(W, H, C).reshape(W*H*C), 'same_kind')
        memoryview(arr).cast('B').cast('f')[:] = arrs[0]*np.ones((W*H*C),dtype=np.float32)#= np.random.rand(W, H, C).astype(np.ctypeslib.ctypes.c_float).reshape(W*H*C)
        qr.put(1)
        print(1, arr[0], arrs[3], arrstr.value)#, np.frombuffer(arrs.get_obj(),np.float32))
    sys.exit(1)

def main_arr_raw():
    arr = Array('f', W*H*C, lock=False)#Array(np.ctypeslib.ctypes.c_float, W*H*C, lock=False)
    arrs = Array('f', [W,H,C,time.time()], lock=False)
    arrstr = Array(np.ctypeslib.ctypes.c_char, b"magic")
    qr = Queue()
    Process(target=worker_arr_raw, args=(arr, arrs, arrstr, qr)).start()
    for num in range(NUM):
        while qr.qsize()==0:
            time.sleep(0.01)
            continue
        qr.get()
        #b =  memoryview(arrs).cast('B').cast('f')[:]#
        b = np.frombuffer(arr,dtype=np.float32)
        print('b', b[0])#, np.frombuffer(arrs.get_obj(),np.float32))


def arr_test_raw():
    print("Arr raw start")
    start_time = time.time()
    main_arr_raw()
    end_time = time.time()
    duration = end_time - start_time
    msg_per_sec = NUM / duration
    print("Arr raw")
    print("Duration: " + str(duration))
    print("Messages Per Second: " + str(msg_per_sec))

def worker_arr_v(arr, arrs, v):
    for task_nbr in range(NUM):
        #conn.send(np.random.rand(W, H, C))
        #array = -np.frombuffer(arr, dtype=np.int32)
        Arr = np.frombuffer(arr,dtype=np.float32)
        arrs[0] = np.random.rand()
        arrs[1] = np.random.rand()
        arrs[2] = np.random.rand()
        arrs[3] = time.time()
        np.copyto(Arr, np.random.rand(W, H, C).reshape(W*H*C), 'same_kind')
        v.value=0
        #print(1, Arr[0], np.frombuffer(arrs.get_obj(),np.float32))
    sys.exit(1)

def main_arr_v():
    arr = Array('i', W*H*C, lock=False)
    arrs = Array('f', [W,H,C,time.time()], lock=False)
    v = Value('i', 1)
    Process(target=worker_arr_v, args=(arr, arrs, v)).start()
    for num in range(NUM):
        while v.value:
            time.sleep(0.01)
            continue
        v.value=1
        b = np.frombuffer(arr,dtype=np.float32)
        #print('b', b[0], np.frombuffer(arrs.get_obj(),np.float32))

def arr_test_v():
    print("Arr v start")
    start_time = time.time()
    main_arr_v()
    end_time = time.time()
    duration = end_time - start_time
    msg_per_sec = NUM / duration
    print("Arr v")
    print("Duration: " + str(duration))
    print("Messages Per Second: " + str(msg_per_sec))


def worker_arr_l(arr, arrs, l):
    for task_nbr in range(NUM):
        #conn.send(np.random.rand(W, H, C))
        #array = -np.frombuffer(arr, dtype=np.int32)
        Arr = np.frombuffer(arr.get_obj(),dtype=np.float32)
        l.acquire()
        arrs[0] = np.random.rand()
        arrs[1] = np.random.rand()
        arrs[2] = np.random.rand()
        arrs[3] = time.time()
        np.copyto(Arr, np.random.rand(W, H, C).reshape(W*H*C), 'same_kind')
        l.release()
        print(1, Arr[0])#, np.frombuffer(arrs.get_obj(),np.float32))
    sys.exit(1)

def main_arr_l():
    arr = Array('f', W*H*C)
    arrs = Array('f', [W,H,C,time.time()])
    lock = Lock()
    Process(target=worker_arr_l, args=(arr, arrs, lock,)).start()
    for num in range(NUM):
        time.sleep(0.1)
        ret = lock.acquire()
        b = np.frombuffer(arr.get_obj(),dtype=np.float32)
        print('b', b[0], ret)#, np.frombuffer(arrs.get_obj(),np.float32))
        lock.release()

def arr_test_l():
    print("Arr l start")
    start_time = time.time()
    main_arr_l()
    end_time = time.time()
    duration = 0.01 + end_time - start_time
    msg_per_sec = NUM / duration
    print("Arr l")
    print("Duration: " + str(duration))
    print("Messages Per Second: " + str(msg_per_sec))


def worker_arr(arr, arrs, q):
    for task_nbr in range(NUM):
        #conn.send(np.random.rand(W, H, C))
        #array = -np.frombuffer(arr, dtype=np.int32)
        Arr = np.frombuffer(arr.get_obj(),dtype=np.float32)
        arrs[0] = np.random.rand()
        arrs[1] = np.random.rand()
        arrs[2] = np.random.rand()
        arrs[3] = time.time()
        np.copyto(Arr, np.random.rand(W, H, C).reshape(W*H*C), 'same_kind')
        q.put(1)
        #print(1, Arr[0])#, np.frombuffer(arrs.get_obj(),np.float32))
    sys.exit(1)

def main_arr():
    arr = Array('f', W*H*C)
    arrs = Array('f', [W,H,C,time.time()])
    q = Queue()
    print(W*H*C)
    Process(target=worker_arr, args=(arr, arrs, q)).start()
    for num in range(NUM):
        while q.qsize()==0:
            time.sleep(0.01)
            continue
        q.get()
        b = np.frombuffer(arr.get_obj(),dtype=np.float32)
        #print('b', b[0])#, np.frombuffer(arrs.get_obj(),np.float32))

def arr_test():
    print("Arr starts")
    start_time = time.time()
    main_arr()
    end_time = time.time()
    duration = end_time - start_time
    msg_per_sec = NUM / duration
    print("Arr")
    print("Duration: " + str(duration))
    print("Messages Per Second: " + str(msg_per_sec))

def worker_pipe(conn):
    for task_nbr in range(NUM):
        conn.send(np.random.rand(W, H, C))
    sys.exit(1)


def main_pipe():
    parent_conn, child_conn = Pipe(duplex=False)
    Process(target=worker_pipe, args=(child_conn,)).start()
    for num in range(NUM):
        message = parent_conn.recv()

def pipe_test():
    print("Pipe start")
    start_time = time.time()
    main_pipe()
    end_time = time.time()
    duration = end_time - start_time
    msg_per_sec = NUM / duration
    print("Pipe")
    print("Duration: " + str(duration))
    print("Messages Per Second: " + str(msg_per_sec))

def worker_queue(q):
    for task_nbr in range(NUM):
        q.put(np.random.rand(W, H, C))
    sys.exit(1)

def main_queue():
    recv_q = Queue()
    Process(target=worker_queue, args=(recv_q,)).start()
    for num in range(NUM):
        message = recv_q.get()

def queue_test():
    print("Queue starts")
    start_time = time.time()
    main_queue()
    end_time = time.time()
    duration = end_time - start_time
    msg_per_sec = NUM / duration
    print("Queue")
    print("Duration: " + str(duration))
    print("Messages Per Second: " + str(msg_per_sec))


if __name__ == "__main__":
    for i in range(1):
        arr_test_raw()
        arr_test_v()
        #arr_test_l()
        #arr_test_noq()
        arr_test()
        queue_test()
        pipe_test()
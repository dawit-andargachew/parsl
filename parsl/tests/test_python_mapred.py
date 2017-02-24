''' Testing bash apps
'''
import parsl
from parsl import *

import os
import time
import shutil
import argparse
import random

#parsl.set_stream_logger()

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)

@App('python', dfk)
def fan_out(x, dur):
    import time
    time.sleep(dur)
    return x*2

@App('python', dfk)
def accumulate(inputs=[]):
    return sum(inputs)

@App('python', dfk)
def accumulate_t(*args):
    return sum(args)


def test_mapred_type1(width=5):
    futs = []
    for i in range(1,width+1):
        fu = fan_out(i, random.randint(0,5)/10)
        futs.extend([fu])

    print("Fan out : ", futs)

    red = accumulate(inputs=futs)
    #print([(i, i.done()) for i in futs])
    r = sum([x*2 for x in range(1,width+1)])
    assert r  == red.result(), "[TEST] MapRed type1 expected %s, got %s" % (r, red.result())


def test_mapred_type2(width=5):
    futs = []
    for i in range(1,width+1):
        fu = fan_out(i, i/10)
        futs.extend([fu])

    print("Fan out : ", futs)

    red = accumulate_t(*futs)

    #print([(i, i.done()) for i in futs])
    r = sum([x*2 for x in range(1,width+1)])
    assert r  == red.result(), "[TEST] MapRed type2 expected %s, got %s" % (r, red.result())


if __name__ == '__main__' :

    parser   = argparse.ArgumentParser()
    parser.add_argument("-w", "--width", default="5", help="width of the pipeline")
    parser.add_argument("-d", "--debug", action='store_true', help="Count of apps to launch")
    args   = parser.parse_args()

    if args.debug:
        parsl.set_stream_logger()


    tests = [test_mapred_type1, test_mapred_type2]
    for test in tests :
        print("*" * 50)
        try:

            test(width=int(args.width))
        except AssertionError as e:
            print("[TEST]  %s [FAILED]" % test.__name__)
            print(e)
        else:
            print("[TEST]  %s type [SUCCESS]" % test.__name__)

        print("*" * 50)

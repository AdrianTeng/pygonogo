"""
Code to run go/no-go task. Ported from Matlab.
"""

import sys
import task

if __name__ == '__main__':
    mytask = task.Task()
    mytask.run(shorten=len(sys.argv) > 1)
    mytask.teardown()

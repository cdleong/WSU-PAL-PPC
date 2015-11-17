'''
Created on Nov 16, 2015

@author: cdleong
'''
#based on http://www.graphviz.org/doc/info/output.html#ID
#also, https://www.logilab.org/blogentry/6883

#To make this work, try 

import pylint
import os
from pylint import run_pyreverse
import subprocess
import shlex

if __name__ == '__main__':
    for fn in os.listdir('.'):
        if os.path.isfile(fn):
            if(fn.endswith('.py')):
                print (fn)
                command = 'pyreverse -o png -ASmy {0} -p {0}'.format(fn)
                subprocess.call(shlex.split(command)) 
                                               
#                 run_pyreverse()
        
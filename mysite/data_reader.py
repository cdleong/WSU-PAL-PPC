'''
Created on Mar 5, 2015

@author: cdleong
'''
import xlrd

class DataReader(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
'''
let us test things
'''
def main(): 
    print "hello world"
    book = xlrd.open_workbook("pprinputs_Colin.xlsx")
    print "The number of worksheets is", book.nsheets
    print "Worksheet name(s):", book.sheet_names()
    
    
    
if __name__ == "__main__":
    main()
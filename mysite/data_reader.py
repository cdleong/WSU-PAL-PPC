'''
Created on Mar 5, 2015

@author: cdleong
'''
import xlrd


#Useful notes: http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/

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
    
    
    workSheet = book.sheet_by_index(0)
    
    num_rows = workSheet.nrows-1
    
    print "the number of rows is", num_rows
    
    curr_row =1
    
    row = workSheet.row(curr_row)
    
    print row
    
    #I successfully printed a row. I have discovered how to read data from excel spreadsheets.
    #successs
    
    
    
    
if __name__ == "__main__":
    main()
'''
Created on Mar 5, 2015

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively. 


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
    
    
    #workSheet = book.sheet_by_index(0)
    workSheet = book.sheet_by_name('pprinputs')

    
    num_rows = workSheet.nrows-1
    
    print "the number of rows is", num_rows
    
    curr_row =0
    
    columnnames = workSheet.row(curr_row)
    
    print columnnames
    
    #
    
    
    
    
    #I successfully printed a row. I have discovered how to read data from excel spreadsheets.
    #success
    
    
    #now to keep only the rows for, say, one lake. 
    #how
    curr_row=1
    rowData = workSheet.row(curr_row)
    print rowData
    #OK, so Lake ID is index 2
    lakeIDIndex = 2
    print rowData[lakeIDIndex] #test that 
    
    #testing xlrd.colname
    #print xlrd.colname(2) #gives "C"
    
    #test. 
    rowsThatHaveUS_Spark = []
    curr_row = -1
    while curr_row<num_rows:
        curr_row+=1
        row = workSheet.row(curr_row)
        #print "the value at row index ", lakeIDIndex, " is ", row[lakeIDIndex] 
        if ('US_SPARK'==row[lakeIDIndex].value):
            rowsThatHaveUS_Spark.append(row)
            
    print len(rowsThatHaveUS_Spark)   # 1120 rows, or, about a third of them. Not unreasonable 
    print rowsThatHaveUS_Spark[0] #hey it worked.
    
    #find kd
    curr_column = 14 #I think it is this one
    print columnnames[curr_column] #yup
    
  
    
    
    
     
    
    
    
    
if __name__ == "__main__":
    main()
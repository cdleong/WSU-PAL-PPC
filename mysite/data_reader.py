'''
Created on Mar 5, 2015

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively. 
from mysite import PondLayer


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
    
    #############################################
    #Keep only one lake
    #############################################
    
     
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
    rowsForOneLake = []
    curr_row = 0
    while curr_row<num_rows:
        curr_row+=1
        row = workSheet.row(curr_row)
        #print "the value at row index ", lakeIDIndex, " is ", row[lakeIDIndex] 
        if ('US_SPARK'==row[lakeIDIndex].value):
            rowsForOneLake.append(row)
            
    print len(rowsForOneLake)   # 1120 rows, or, about a third of them. Not unreasonable 
    print rowsForOneLake[0] #hey it worked.
    
    
    #################################################
    #Keep only one DOY
    #################################################
    dayOfYearIndex = 1
    curr_column = dayOfYearIndex
    curr_row = 0
    doy = rowsForOneLake[curr_row][curr_column].value
    print "DAY OF YEAR: ", doy
    
    
    rowsForOneLakeAndOneDay = []
    while curr_row<len(rowsForOneLake)-1:
        curr_row+=1
        row = rowsForOneLake[curr_row]
        
        if (doy==row[curr_column].value):
            print "the value at row index ", curr_column, " is ", row[curr_column] 
            rowsForOneLakeAndOneDay.append(row)
    

    

    
    ##########################
    #Keep only littoral area
    ##########################
    #find kd
    kd_index = 14 #I think it is this one
    #print columnnames[kd_index] #yup
    
    #find depth
    depth_index = 3
#     print columnnames[depth_index] #yup
    
    
    #depth of 1% light is 4.6/kd
    
    #kd is the same for the whole lake for one day.
    curr_row = 0
    curr_column = kd_index
    kd = rowsForOneLakeAndOneDay[curr_row][curr_column].value
    print "THE KD VALUE IS", kd
    
    d1percent = 4.6/kd #depth of 1%light, meters.
    print "depth of 1%light is ", d1percent
    
    
    curr_row = 0
    curr_column = depth_index
    rowsForLittoralArea = []
    while curr_row<len(rowsForOneLakeAndOneDay)-1:
        curr_row+=1
        row = rowsForOneLakeAndOneDay[curr_row]
         
        if (d1percent>row[curr_column].value):
            print "the value at row index ", curr_column, " is ", row[curr_column] 
            rowsForLittoralArea.append(row)    
            
    ###############################
    #Calculate total littoral area
    ###############################
    area_index = 16
    curr_column = area_index
    print columnnames[curr_column] #yup
    
    
    
    
    curr_row = 0
    curr_column = area_index
    total_area = 0 #I expect 518220
    while curr_row<len(rowsForLittoralArea)-1:
        curr_row+=1
        row = rowsForLittoralArea[curr_row]
        area_at_z = row[curr_column].value
        total_area += area_at_z
        print "area at ", row[depth_index].value, " is ", row[area_index].value
        
    
    print "TOTAL AREA: ", total_area
    
    ################################
    #Fractional area
    ################################
    
        
    
    
    
    
    
  
    
    
    
     
    
    
    
    
if __name__ == "__main__":
    main()
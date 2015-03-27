'''
Created on Mar 5, 2015

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively. 
from pond_layer import Pond_Layer
from pond import Pond
import numpy as np
from django.contrib.gis.geos.base import numpy


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
        
        row = workSheet.row(curr_row)
        #print "the value at row index ", lakeIDIndex, " is ", row[lakeIDIndex] 
        if ('US_SPARK'==row[lakeIDIndex].value):
            rowsForOneLake.append(row)
        curr_row+=1    
        
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
    while curr_row<len(rowsForOneLake):        
        
        row = rowsForOneLake[curr_row]
        
        if (doy==row[curr_column].value):
            print "the value at row index ", curr_column, " is ", row[curr_column] 
            rowsForOneLakeAndOneDay.append(row)
        curr_row+=1

    


    

    
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
    while curr_row<len(rowsForOneLakeAndOneDay):        
        row = rowsForOneLakeAndOneDay[curr_row]
         
        if (d1percent>row[curr_column].value):
#             print "the value at row index ", curr_column, " is ", row[curr_column] 
            rowsForLittoralArea.append(row)    
        curr_row+=1    
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
    pond_littoral_area = 0 #I expect 518220
    while curr_row<len(rowsForLittoralArea):        
        row = rowsForLittoralArea[curr_row]
        area_at_z = row[curr_column].value
        pond_littoral_area += area_at_z
        curr_row+=1

        
    
    print "TOTAL AREA: ", pond_littoral_area
    
    ################################
    #Fractional area and make objects
    ################################
    print "number of rows in littoral area is", len(rowsForLittoralArea)
    
    
    curr_row = 0
    curr_column = 0
    lengthOfDayIndex = 27
    print columnnames[lengthOfDayIndex]#yup
    noonLightIndex = 18
    print columnnames[noonLightIndex]
    pmax_index = 13
    print columnnames[pmax_index]
    ikIndex = 21
    print columnnames[ikIndex]
    
    
    #MAKE A POND
    row = rowsForLittoralArea[curr_row]
    pond_doy_value = row[dayOfYearIndex].value #Day of year, same for every row
    pond_kd_value = row[kd_index].value #kd value (light attenuation coefficient
    pond_lod_value = row[lengthOfDayIndex].value
    pond_noonLight_value = row[noonLightIndex].value
    
    pond = Pond() #includes a list of pond_layers
    pond.setDayOfYear(pond_doy_value)
    pond.setBackgroundLightAttenuation(pond_kd_value)
    pond.setDayLength(pond_lod_value)
    pond.setLittoralArea(pond_littoral_area)
    pond.setNoonSurfaceLight(pond_noonLight_value)
    
    
    
    
    
    #make layers
    while curr_row<len(rowsForLittoralArea):        
        row = rowsForLittoralArea[curr_row]
        row_depth_value = row[depth_index].value        
        row_area_value = row[area_index].value
        row_fractional_area = row_area_value/pond_littoral_area
        row_pmax_value = row[pmax_index].value
        row_ik_value = row[ikIndex].value
        layer = Pond_Layer(row_depth_value, row_area_value, row_fractional_area, row_pmax_value, row_ik_value)
        print "adding layer with values", layer.get_depth(), " , ", layer.get_fractional_area(), " , ", layer.get_ik(), " , ", layer.get_pmax(), " "
        pond.appendPondLayer(layer)
        curr_row+=1
        
    
    #testing
#     layer = listOfPondLayers[0]
#     print "length of pond layer list", len(listOfPondLayers)
    
    #test. fractional areas should equal 1
    test_area_total=0 #should be 1 at the end
    for layer in pond.pondLayerList:
        f_area = layer.get_fractional_area()
#         print "f_area is ",f_area 
        test_area_total+=layer.fractional_area
        
    print "sum of fractional areas is ", test_area_total
    
    
    timeInterval =0.25
    
    time =0.0
    noonLight = pond.getNoonSurfaceLight()
    lengthOfDay = pond.getDayLength()
    kd = pond.getBackgroundLightAttenuation()
    BPPR =0.0 #
    while (time < pond.getDayLength()): #for each time interval
        
        
        
        light = noonLight * np.sin(np.pi*(time/lengthOfDay)) #SAS code was light = noon*sin(constant('pi')*Time/LOD1);
        print "light at time ", time, " is ", light
        #for each layer
        for layer in pond.pondLayerList:
            z = layer.get_depth()
            f_a = layer.get_fractional_area
            pmax = layer.get_pmax()
            ik = layer.get_ik()
            BPPRZT = (pmax*np.tanh(light*np.exp(-kd*z)/ik))
            BPPR += BPPRZT
            
            
        time+=timeInterval  
        
    BPPR = BPPR/(1/timeInterval) #e.g. 1/0.25 = 4. Accounting for 15 minute time. Calculations give us production/hour, but we calculated 4 times per hour, so adding them all up gives 4 times as much
    print "Whole lake Benthic Primary Production per meter squared per day is ", BPPR
    
    
    for layer in pond.pondLayerList:
        f_area = layer.get_fractional_area()
        bpprz = BPPR*f_area
        print bpprz
        layer.set_bpprz(bpprz)
        
            
            
        
        
        
        
        
        
        
        
        
    
    
    
    
        
        
        
        

        
    
    
    
    
    
  
    
    
    
     
    
    
    
    
if __name__ == "__main__":
    main()
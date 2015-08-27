'''
Created on Mar 5, 2015

This class reads in data from an excel file, packages it up, and sends it to the model for processing.

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively.
from pond import Pond
from numpy.distutils.npy_pkg_config import FormatError

from mysite.benthic_photosynthesis_measurement import BenthicPhotosynthesisMeasurement
from mysite.bathymetric_pond_shape import BathymetricPondShape


from mysite.phytoplankton_photosynthesis_measurement import PhytoPlanktonPhotosynthesisMeasurement
import sys




#Useful notes: http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/

class DataReader(object):
    
    '''
    classdocs
    '''

    ##################################
    # Class variables
    ##################################
#     filename = "template.xlsx" #name of file. Default is "template.xlsx"
#     filename = "template_example.xlsx" #name of file. Has photo measurements at 0.1 meter intervals
#     filename = "June_26_light_penetration_testing_data_fixed_surface_area.xlsx" #Attempted to fix water surface area. Only photo data at certain intervals.
#     filename = "June_26_10cm_testing_data_fixed_surface_area.xlsx"#Attempted to fix water surface area. photo data at 10cm intervals
#     filename = "relative_depth_template_example.xlsx" #name of file. Only has photo data at light penetration levels [1.0, 0.8,0.5,0.25,0.1,0.01]
#     filename = "Jul_03_data_template_example.xlsx" #"reasonable" values for everything, including phytoplankton photosynthesis. Benthic measurements use light penetration proportions.
#     filename = "Jul_08_data_template_example_interim.xlsx" #"reasonable" values for everything, except the benthic data is back to the old pprinputs 10cm intervals by actual depth instead of proportions.
#     filename = "Jul_08_data_template_example_with_benthic_light_proportions.xlsx" #"reasonable" values for everything, benthic data uses light penetration proportions calculated from the 10 cm individuals
#     filename = "Aug_03_test_data.xls" #"Same as Jul_08_data_template_example_with_benthic_light_proportions, but added in BIGMU lake.
#     filename = "Aug_03_test_data_bppr10percent_intervals.xls" #"Same as Aug_03_test_data, but reducing data points to 10-percent intervals.
#     filename = "Aug_03_test_data_bppr5measurements.xls" #"Same as Aug_03_test_data_bppr10percent_intervals.xls, but with bppr data points at the following light proportions: [1.00,0.5,0.25,0.1,0.01]
#     filename = "Aug_03_test_data_pppr1995_day152_cryst.xls" #"Same as Aug_03_test_data_bppr5measurements.xls, but altered PPR data to test PPR calculations. test data taken from Phyte_90s.csv. Year=1995, DOY=152. Depth is max depth. Just assuming 1 layer.
    filename = "Aug_26_test_data.xls" #"Same as Aug_03_test_data_bppr5measurements.xls, but altered PPR data to test PPR calculations. test data taken from Phyte_90s.csv. Year=1995, DOY=152. Depth is max depth. Just assuming 1 layer.  
 
    

    
    
    
    

    #data starts at row 1. Row 0 is column headings
    DEFAULT_COLUMN_HEADINGS_ROW = 0
    DEFAULT_FIRST_DATA_ROW = 1
    DEFAULT_NUMBER_OF_SHEETS = 4 #Pond, benthic, planktonic. Guide optional.
    
    
    
    
    
    ########################
    #Worksheet Names/Indices
    ########################
    
    #TODO: maybe some arrays? Or some more flexible solution anyway
    
    #default indices. 
    POND_DATA_SHEET_INDEX =0
    BENTHIC_PHOTO_DATA_SHEET_INDEX = 1
    PHYTOPLANKTON_PHOTO_DATA_SHEET_INDEX = 2
    SHAPE_DATA_SHEET_INDEX = 3     
    
    #default names       
    POND_DATA_SHEET_NAME = "pond_data"
    BENTHIC_PHOTO_DATA_SHEET_NAME = "benthic_photo_data"
    PHYTOPLANKTON_PHOTO_DATA_SHEET_NAME = "phytoplankton_photo_data"
    SHAPE_DATA_SHEET_NAME = "shape_data"    
    
    
        
    
    
    #############
    #Data Indices
    #############
    #TODO: a dict? 
    #TODO: some way for the user to specify all this on sheet 0, perhaps?
    #indices common to all sheets
    dayOfYearIndex = 0 #"DOY"
    lakeIDIndex = 1 #"Lake_ID"
    
    
    
    
    #indices for Pond vars in pond_data worksheet
    kd_index = 2 #index of light attenuation coefficient kd
    noon_surface_light_index = 3 #"midday.mean.par"
    length_of_day_index = 4 #"LOD" in hours             
    latitude_index = 5 #latitude in decimal degrees.    
    
    #indices for vars in benthic_photo_data worksheet
    benthic_light_penetration_proportion_index = 2 #        
    benthic_pmax_index = 3 #"pmax.z"
    benthic_ik_index = 4 #"ik_z" light intensity at onset of saturation
    
    #indices for vars in phytoplankton_photo_data worksheet
    phyto_thermal_layer_index =2
    phyto_depth_index = 3
    phyto_pmax_index = 4
    phyto_alpha_index = 5
    phyto_beta_index = 6
    
    #indices for vars in shape_data worksheet        
    shape_ID_index = 0
    shape_depth_index = 1 #"z" in meters #depth is in several sheets #TODO: different variable?            
    shape_area_index = 2 #"kat_div" in meters squared. 
    

    ###############
    #CONSTANTS
    ###############
    DEFAULT_DEPTH_INTERVAL_PERCENTAGE=1 
    DEFAULT_TIME_INTERVAL = 0.25


    def __init__(self, filename, testFlag=0):
        '''
        Constructor
        '''        
        self.filename = filename

                       
            

            
                        


    #TODO: this should return nothing. Bad style. Or rename it.  
    def read(self):
        try:
            book = xlrd.open_workbook(self.filename)
        except:
            raise

        return self.readPondListFromFile(book)




    def readFile(self,inputfile):
        '''
        READ FILE
        Given an inputFile object, opens the workbook and calls the function to read the pondList. 
        '''
        #http://stackoverflow.com/questions/10458388/how-do-you-read-excel-files-with-xlrd-on-appengine
        try:
            book =  xlrd.open_workbook(file_contents=inputfile)
        except IOError:
            raise
         
             
        return self.readPondListFromFile(book)


    #reads all the pond data from the excel file.

    
    def get_wanted_depths(self, pond):
        '''
        GET WANTED DEPTHS
        Used for testing purposes. The original pprinputs file had benthic photosynthesis measurements organized by depth rather than light penetration. 
        @param param: a pond object. 
        @return: 
        @rtype: 
        '''
        pond.calculate_depth_of_specific_light_percentage()
        wanted_depths = pond.calculate_depths_of_specific_light_percentages(self.light_penetration_levels)
        wanted_depths_rounded = []
        for depth in wanted_depths:
            rounded_depth = int((depth*10**1))/10.0**1 #truncate to 1 decimal place
            wanted_depths_rounded.append(rounded_depth)
        return wanted_depths_rounded
        
    
    
    
    
    
    
    def readPondListFromFile(self,book):
        '''
        READ POND LIST FROM FILE
        If you change the name of this, you have to update the name in all the HTML templates, etc.
        Opens the xlrd workbook and returns a list of Pond objects. 
        @param book: an xlrd Workbook
        @return: 
        @rtype: 
        '''
        
        
        
        ##############
        #Worksheets
        ##############
        nsheets = book.nsheets
#         print "The number of worksheets is", book.nsheets
        
        
        sheet_names = book.sheet_names()
#         print "Worksheet name(s):" 
#         print sheet_names
        
        pond_data_workSheet = xlrd.book
        benthic_photo_data_workSheet= xlrd.book        
        phytoplankton_photo_data_sheet= xlrd.book
        shape_data_sheet =xlrd.book 
        
        
        if(nsheets<self.DEFAULT_NUMBER_OF_SHEETS): #Pond, benthic, planktonic. Guide optional.
            raise IOError("file format incorrect. Number of sheets less than expected")
        
        if(self.POND_DATA_SHEET_NAME in sheet_names and 
           self.BENTHIC_PHOTO_DATA_SHEET_NAME in sheet_names and 
           self.PHYTOPLANKTON_PHOTO_DATA_SHEET_NAME in sheet_names and
           self.SHAPE_DATA_SHEET_NAME in sheet_names):
            pond_data_workSheet = book.sheet_by_name(self.POND_DATA_SHEET_NAME)
            benthic_photo_data_workSheet = book.sheet_by_name(self.BENTHIC_PHOTO_DATA_SHEET_NAME)
            phytoplankton_photo_data_sheet = book.sheet_by_name(self.PHYTOPLANKTON_PHOTO_DATA_SHEET_NAME)
            shape_data_sheet = book.sheet_by_name(self.SHAPE_DATA_SHEET_NAME)
        else:
            #Standard sheet names not detected. Attempting to read using sheet indices.
            pond_data_workSheet = book.sheet_by_index(self.POND_DATA_SHEET_INDEX)
            benthic_photo_data_workSheet = book.sheet_by_index(self.BENTHIC_PHOTO_DATA_SHEET_INDEX)
            phytoplankton_photo_data_sheet = book.sheet_by_name(self.PHYTOPLANKTON_PHOTO_DATA_SHEET_INDEX)
            shape_data_sheet = book.sheet_by_name(self.SHAPE_DATA_SHEET_INDEX)
        
        ##############
        #Rows, Columns
        ##############
            
        pond_data_workSheet_num_rows = pond_data_workSheet.nrows 
        benthic_data_workSheet_num_rows = benthic_photo_data_workSheet.nrows
        phytoplankton_photo_data_sheet_num_rows = phytoplankton_photo_data_sheet.nrows
        shape_data_sheet_num_rows = shape_data_sheet.nrows
        
        
        
        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = pond_data_workSheet.row(curr_row)
#         print "the column names in sheet \"" + pond_data_workSheet.name +  "\" are "
#         print columnnames

        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = benthic_photo_data_workSheet.row(curr_row)
#         print "the column names in sheet \"" + benthic_photo_data_workSheet.name +  "\" are "
#         print columnnames        
        
        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = phytoplankton_photo_data_sheet.row(curr_row)
#         print "the column names in sheet \"" + phytoplankton_photo_data_sheet.name +  "\" are "
#         print columnnames                     
        
        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = shape_data_sheet.row(curr_row)
#         print "the column names in sheet \"" + shape_data_sheet.name +  "\" are "
#         print columnnames             
        
        
        #################################################
        #make all the objects!
        #################################################
        pondList = [] #list of pond objects. The same water body on a different day counts as a separate "Pond"



        

        ################################################
        #Make Pond objects from pond_data sheet
        ################################################
        sheet = pond_data_workSheet
        num_rows  = pond_data_workSheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:                  
            row = sheet.row(curr_row)        
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value              
            row_kd_value = float(row[self.kd_index].value)          
            row_noonlight_value = float(row[self.noon_surface_light_index].value) 
            row_latitude_value = float(row[self.latitude_index].value)         
            row_lod_value = float(row[self.length_of_day_index].value)
                    
    
            
            
            #Do we need to make a pond object?
            pond = None
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #not in list. Must create Pond object
#                 print "creating pond with lake ID = ", row_lakeID_value, " , and DOY = ", row_doy_value
                emptyShape = BathymetricPondShape({}) #initialize with empty dict 
                pond = Pond(row_lakeID_value, row_doy_value, row_lod_value, row_noonlight_value, row_kd_value, emptyShape, [], [], row_latitude_value, self.DEFAULT_TIME_INTERVAL)
                pondList.append(pond)         
            curr_row+=1       
            
#         print "out of while loop. size of pond list is: ", len(pondList)
            
        #######################################################
        #we made all the ponds. Time to add all the members
        #######################################################
        
        
        
        
        ############
        #Shape data
        ############
        
        
        sheet = shape_data_sheet
        num_rows = shape_data_sheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
            row = sheet.row(curr_row) 
            
            
            #values
            row_lakeID_value = row[self.shape_ID_index].value
            row_depth_value = float(row[self.shape_depth_index].value)                                                                    
            row_area_value = float(row[self.shape_area_index].value)     

            
            row_dict = {row_depth_value:row_area_value}
            row_shape = BathymetricPondShape(row_dict)
            
            #find the correct pond
            pond = None
#             pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value )),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            #http://stackoverflow.com/questions/14366511/return-the-first-item-in-a-list-matching-a-condition            
#             matchingPonds = filter(next((i for i in pondList if (i.get_lake_id()== row_lakeID_value )),None), pondList)
            for pond in pondList:
                if(pond.get_lake_id()==row_lakeID_value):            
                    pond.update_shape(row_shape)                #add to Pond

            #increment while loop to next row
            curr_row+=1            
        
#         print "added shape data"
        
        
        
        
        
        ###############
        #Benthic data
        ###############
        
        sheet = benthic_photo_data_workSheet
        num_rows = benthic_data_workSheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
            row = sheet.row(curr_row) 
            
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value
            print "light penetration proportion is", row[self.benthic_light_penetration_proportion_index].value
            row_light_penetration_proportion_value = float(row[self.benthic_light_penetration_proportion_index].value)                                        
            row_pmax_value = float(row[self.benthic_pmax_index].value)                            
            row_ik_value = float(row[self.benthic_ik_index].value)                                        
            
            #find the correct pond
            pond = None
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row
                row_depth_value = pond.calculate_depth_of_specific_light_percentage(row_light_penetration_proportion_value) #convert from light proportions to depth in meters.
#                 row_depth_value = row_light_penetration_proportion_value #Read the depths directly. TODO: delete this. Used for testing only.
                 

#                 print "proportion is ", row_light_penetration_proportion_value, " depth is ", row_depth_value
                benthic_measurement = BenthicPhotosynthesisMeasurement(row_depth_value, row_pmax_value, row_ik_value)
                pond.add_benthic_measurement_if_photic(benthic_measurement)                          
                #add to Pond

            curr_row+=1    
        #end of while loop
        ###############
        #Phyto data
        ###############
        
        sheet = phytoplankton_photo_data_sheet
        num_rows = phytoplankton_photo_data_sheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
            row = sheet.row(curr_row) 
            
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value
            row_thermal_layer_value = row[self.phyto_thermal_layer_index].value
            row_depth_value = row[self.phyto_depth_index].value
            row_phyto_pmax_value = row[self.phyto_pmax_index].value
            row_alpha_value = row[self.phyto_alpha_index].value
            row_beta_value = row[self.phyto_beta_index].value                                       
            
#             print "row pmax value ", row_phyto_pmax_value
#             print "row alpha ", row_alpha_value
#             print "row beta ", row_beta_value
            #find the correct pond
            pond = None
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row

                phyto_measurement = PhytoPlanktonPhotosynthesisMeasurement(row_thermal_layer_value, row_depth_value, row_phyto_pmax_value, row_alpha_value, row_beta_value)
                pond.add_phytoplankton_measurement(phyto_measurement)                          
                #add to Pond

            curr_row+=1            
#         print "out of while loop. size of pond list is: ", len(pondList)
         
        


 
        return pondList
    
    #END OF readPondListFromFile METHOD
    
    
    
    
    
    
    

    def write(self, filename="output.xls"):
        '''
        Write to file
        '''

        #Create a new workbook object
        workbook = xlwt.Workbook()

        #Add a sheet
        worksheet = workbook.add_sheet('Statistics')

        #Add some values
        for x in range(0, 10):
            for y in range(0,10):
                worksheet.write(x,y,x*y)

        workbook.save(filename)

'''
let us test things
'''
def main():
    print "hello world"
#     filename = "static/template.xlsx"
    filename = "static/"+DataReader.filename

    reader = DataReader(filename)
    pondList = reader.read()

    p = Pond()
    for p in pondList:
        shape = p.get_pond_shape()
        bppmeasurements_sorted = p.get_benthic_measurements_sorted_by_depth()
        bppmeasurements = p.get_benthic_photosynthesis_measurements()
        

        
        pid = p.get_lake_id()
        doy = p.get_day_of_year()
        lod = p.get_length_of_day()
        kd = p.get_light_attenuation_coefficient()
        noon_light = p.get_noon_surface_light()
        relative_depths = [1.0, 0.8,0.5,0.25,0.1,0.01]
        relative_depth_meters = []
        
        #testing phyto stuff
        #US sparkling lake
#         us_spark_p_m1 = PhytoPlanktonPhotosynthesisMeasurement(1, 5, 4.113867544, 0.05, 0.01) #US sparkling lake
#         us_spark_p_m2 = PhytoPlanktonPhotosynthesisMeasurement(2, 10, 2.636765965,0.0412667109,0)
#         us_spark_p_m3 = PhytoPlanktonPhotosynthesisMeasurement(3, 15, 4.959339837, 0.1646230769,0)        
#         
#         us_cryst_p_m1 = PhytoPlanktonPhotosynthesisMeasurement(1, 5.25, 4.113867544, 0.05, 0.01) #US sparkling lake
#         us_cryst_p_m2 = PhytoPlanktonPhotosynthesisMeasurement(2, 11, 4.113867544, 0.05, 0.01) #US sparkling lake
#         us_cryst_p_m3 = PhytoPlanktonPhotosynthesisMeasurement(3, 18.4, 4.113867544, 0.05, 0.01) #US sparkling lake
#         
        
        
               
        print ""
        print ""
        print ""      
            
        print "**************************************************************************************" 
        bppr = p.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(0.1)
        bppr_surface_area = p.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(0.1, False)
        pppr = p.calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared(0.1)
        
        print "lake ID: ", pid, " DOY: ", doy
        print "bppr is ", str(bppr), " mg C per square meter of littoral area"
        print "bppr is ", str(bppr_surface_area),  " mg C per square meter of lake surface area"
        print "pppr is ", str(pppr)
        littoral_area = p.calculate_total_littoral_area()+0.0
        surface_area = p.get_pond_shape().get_water_surface_area_at_depth(0)
        print "the percentage of 1% light is ", p.calculate_depth_of_specific_light_percentage(0.01)
        print "the total littoral zone is: ", littoral_area
        print "the surface area is: ",  surface_area
        print "max depth is: ", shape.get_max_depth()
        print "number of bpp measurements is:", len(bppmeasurements) 
        
        
        

#         tbpp = p.calculate_total_seasonal_benthic_primary_production()
#         print "total seasonal benthic primary production (mgC) would be ",tbpp
#         print "in kilograms of carbon, that would be ",tbpp/1000 
#         print "in tons of carbon, that would be", tbpp/(1000*1000)
#         print "in terms of milligrams of carbon per meter squared of littoral area that would be", tbpp/p.calculate_total_littoral_area()
#         
#         
#         tppp = p.calculate_total_seasonal_phytoplankton_primary_production() 
#         print "total seasonal benthic primary production (mgC) would be ",tppp
#         print "in kilograms of carbon, that would be ",tppp/1000 
#         print "in tons of carbon, that would be", tppp/(1000*1000)
#         print "in terms of milligrams of carbon per meter squared of littoral area that would be", tppp/p.calculate_total_littoral_area()        

                

            





        print ""
        print ""
        print ""           
        print "**************************************************************************************"
    
    print "done with all the ponds"
    sys.exit()

if __name__ == "__main__":
    main()
'''
Created on Mar 5, 2015

This class reads in data from an excel file, packages it up, and sends it to the model for processing.

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively.
from pond import Pond
from numpy.distutils.npy_pkg_config import FormatError
from mysite.photosynthesis_measurement import PhotosynthesisMeasurement
from mysite.benthic_photosynthesis_measurement import BenthicPhotoSynthesisMeasurement
from mysite.bathymetric_pond_shape import BathymetricPondShape
import numpy as np




#Useful notes: http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/

class DataReader(object):
    
    '''
    classdocs
    '''

    ##################################
    # Class variables
    ##################################
#     filename = "template.xlsx" #name of file. Default is "template.xlsx"
    filename = "template_example.xlsx" #name of file. Has photo measurements at 0.1 meter intervals
#     filename = "relative_depth_template_example.xlsx" #name of file. Only has photo data at light penetration levels [1.0, 0.8,0.5,0.25,0.1,0.01]
    
#     light_penetration_levels = [1.0,0.8,0.5,0.25,0.1,0.01]
#     light_penetration_levels = [1.0,0.95,0.9,0.85,0.8,0.75,0.7,0.9,0.65,0.6,0.55,0.5,0.45,0.4,0.35,0.3,0.25,0.2,0.15,0.1,0.01]
    light_penetration_levels = np.arange(0, 1, 0.01)
    
    
    
    

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
#     WORKSHEET_INDICES ={"POND_DATA_SHEET_INDEX":0, "BENTHIC_PHOTO_DATA_SHEET_INDEX":1, "PHYTOPLANKTON_PHOTO_DATA_SHEET_INDEX":2,"SHAPE_DATA_SHEET_INDEX":3}#TODO: finish converting to dicts. 
    
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
    
    #indices for vars in benthic_photo_data worksheet
    benthic_depth_index = 2 #"z" in meters #depth is in several sheets        
    benthic_pmax_index = 3 #"pmax.z"
    benthic_ik_index = 4 #"ik_z" light intensity at onset of saturation
    
    #indices for vars in phytoplankton_photo_data worksheet
    
    #indices for vars in shape_data worksheet        
    shape_depth_index = 2 #"z" in meters #depth is in several sheets #TODO: different variable?            
    shape_area_index = 3 #"kat_div" in meters squared. 
    

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
        self.light_penetration_levels = np.arange(0,1, 0.01)
        print "wanted: ", self.light_penetration_levels
                       
            

            
                        


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
        Opens the xlrd workbook and generates a list of Pond objects.
        @param book: an xlrd Workbook
        '''
        
        
        
        ##############
        #Worksheets
        ##############
        nsheets = book.nsheets
        print "The number of worksheets is", book.nsheets
        
        
        sheet_names = book.sheet_names()
        print "Worksheet name(s):" 
        print sheet_names
        
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
#             print "pond_data sheet detected"
            pond_data_workSheet = book.sheet_by_name(self.POND_DATA_SHEET_NAME)
#             print "benthic photosynthesis data sheet detected"
            benthic_photo_data_workSheet = book.sheet_by_name(self.BENTHIC_PHOTO_DATA_SHEET_NAME)
#             print "phytoplankton photosynthesis data sheet detected"
            phytoplankton_photo_data_sheet = book.sheet_by_name(self.PHYTOPLANKTON_PHOTO_DATA_SHEET_NAME)
#             print "lake shape data sheet detected"
            shape_data_sheet = book.sheet_by_name(self.SHAPE_DATA_SHEET_NAME)
        else:
#             print "Standard sheet names not detected. Attempting to read using sheet indices."
            pond_data_workSheet = book.sheet_by_index(self.POND_DATA_SHEET_INDEX)
            benthic_photo_data_workSheet = book.sheet_by_index(self.BENTHIC_PHOTO_DATA_SHEET_INDEX)
            phytoplankton_photo_data_sheet = book.sheet_by_name(self.PHYTOPLANKTON_PHOTO_DATA_SHEET_INDEX)
            shape_data_sheet = book.sheet_by_name(self.SHAPE_DATA_SHEET_INDEX)
        
        ##############
        #Rows, Columns
        ##############
            
        pond_data_workSheet_num_rows = pond_data_workSheet.nrows
#         print "the number of rows in sheet " + pond_data_workSheet.name +  " is " + str(pond_data_workSheet_num_rows)        
        benthic_data_workSheet_num_rows = benthic_photo_data_workSheet.nrows
        print "the number of rows in sheet " + benthic_photo_data_workSheet.name + " is " + str(benthic_data_workSheet_num_rows)
        phytoplankton_photo_data_sheet_num_rows = phytoplankton_photo_data_sheet.nrows #TODO: implement ppp
#         print "the number of rows in sheet " + phytoplankton_photo_data_sheet.name + " is " + str(phytoplankton_photo_data_sheet_num_rows)
        shape_data_sheet_num_rows = shape_data_sheet.nrows
#         print "the number of rows in sheet " + shape_data_sheet.name + " is " + str(shape_data_sheet_num_rows)
        
        
        
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
#             print "adding Ponds. curr_row = " + str(curr_row) + ", which is still less than num_rows = " + str(num_rows)
            #for quick reference, these are the Pond row indices            
            #     dayOfYearIndex = 0 #"DOY"
            #     lakeIDIndex = 1 #"Lake_ID"
            #     surface_area_index = 2 #"LA.m2"
            #     gam_index = 3
            #     kd_index = 4 #index of light attenuation coefficient kd
            #     noon_surface_light_index = 5 #"midday.mean.par"
            #     length_of_day_index = 10 #"LOD" in hours                     
            row = sheet.row(curr_row)        
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value              
            row_kd_value = row[self.kd_index].value          
            row_noonlight_value = row[self.noon_surface_light_index].value 
            row_lod_value = row[self.length_of_day_index].value            
    
            
            
            #Do we need to make a pond object?
            pond = None
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #not in list. Must create Pond object
#                 print "creating pond with lake ID = ", row_lakeID_value, " , and DOY = ", row_doy_value
                emptyShape = BathymetricPondShape({}) #initialize with empty dict 
                pond = Pond(row_lakeID_value, row_doy_value, row_lod_value, row_noonlight_value, row_kd_value, emptyShape, [], [], self.DEFAULT_TIME_INTERVAL)
                pondList.append(pond)         
            curr_row+=1       
            
        print "out of while loop. size of pond list is: ", len(pondList)
            
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
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value
            row_depth_value = row[self.shape_depth_index].value                                                                    
            row_area_value = row[self.shape_area_index].value     

            
            row_dict = {row_depth_value:row_area_value}
            row_shape = BathymetricPondShape(row_dict)
            
            #find the correct pond
            pond = None
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                print "oh no"#TODO: better error
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row
                pond.update_shape(row_shape)                #add to Pond

            curr_row+=1            
        
        
        
        
        
        
        
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
            row_depth_value = row[self.benthic_depth_index].value                                        
            row_pmax_value = row[self.benthic_pmax_index].value                            
            row_ik_value = row[self.benthic_ik_index].value                                        
            
            #find the correct pond
            pond = None
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row
                row_depth_value_rounded = int(row_depth_value*10)/10.0 #truncate to 1 decimal place.
                print "truncated depth value", row_depth_value
                
                wanted_depths = []
                wanted_depths.extend(self.get_wanted_depths(pond))
                
                
                if( row_depth_value_rounded in wanted_depths):
                    print "original number: ", row_depth_value, " rounded to ", row_depth_value_rounded
                    print "wanted depths are: ", wanted_depths
                    print "row value contains wanted depth. Adding Benthic Photosynthesis Measurement to Pond."
                
                    benthic_measurement = BenthicPhotoSynthesisMeasurement(row_depth_value, row_pmax_value, row_ik_value)
                    pond.add_benthic_measurement_if_photic(benthic_measurement)                

                
                #add to Pond
                
            curr_row+=1    
        
                       

        #end of while loop
#         print "out of while loop. size of pond list is: ", len(pondList)
         
        


 
        return pondList

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
        

        
        pid = p.get_lake_id()
        doy = p.get_day_of_year()
        lod = p.get_length_of_day()
        kd = p.get_light_attenuation_coefficient()
        noon_light = p.get_noon_surface_light()
        relative_depths = [1.0, 0.8,0.5,0.25,0.1,0.01]
        relative_depth_meters = []
        
        
               
        print ""
        print ""
        print ""      
            
        print "**************************************************************************************" 
        bppr = p.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
        print "lake ID: ", pid, " DOY: ", doy
        print  "bppr is ", str(bppr) 
        littoral_area = p.calculate_total_littoral_area()+0.0
        print "the total littoral zone calculated using the bottom area - top area method is: ", littoral_area 
        print "the depth of 1% light is ", p.calculate_depth_of_specific_light_percentage(0.01)
        

        
        for rel_depth in  relative_depths:
                    rel_dep_m=p.calculate_depth_of_specific_light_percentage(rel_depth)
                    relative_depth_meters.append(rel_dep_m)
#                     print "relative depth = ", rel_depth, " meters: ", rel_dep_m
        #             print "the corresponding depth in meters is ", p.calculate_depth_of_specific_light_percentage(rel_depth)
        
        
        
        
        
        current_depth = 0
        depth_interval = 0.1
        max_depth = p.get_max_depth()
        depths = []
        areas = []
        pmaxes = []
        iks = []
        bp_measurements = p.get_benthic_photosynthesis_measurements()
        for measurement in bp_measurements:
            bpmax = measurement.get_pmax()
            ik = measurement.get_ik()
            current_depth = measurement.get_depth()
            area = p.pond_shape_object.get_water_surface_area_at_depth(current_depth)
            
            depths.append(current_depth)
            pmaxes.append(bpmax+0.0)
            iks.append(ik+0.0)
            areas.append(area)
            current_depth+=depth_interval            
            
            
#         while current_depth<=max_depth:
#             bpmax = p.get_benthic_pmax_at_depth(current_depth)
#             ik = p.get_benthic_ik_at_depth(current_depth)
#             area = p.pond_shape_object.get_water_surface_area_at_depth(current_depth)
#             
# #             print "__________________________________________________________________________________________________________________"
# #             print "at depth: ", current_depth, " the interpolated value of benthic pmax is: ", bpmax, " and ik is: ", ik
# #             print "interpolation also used for area at depth. The calculated value of area at this depth is: ", p.get_pond_shape().get_water_surface_area_at_depth(current_depth)
#             depths.append(current_depth)
#             pmaxes.append(bpmax+0.0)
#             iks.append(ik+0.0)
#             areas.append(area)
#             current_depth+=depth_interval
        
        print "depths: ", depths
        print "areas: ", areas
        print "pmaxes", pmaxes
        print "iks", iks
  
        




        print ""
        print ""
        print ""           
        print "**************************************************************************************"

        

if __name__ == "__main__":
    main()
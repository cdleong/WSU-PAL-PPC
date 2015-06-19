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




#Useful notes: http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/

class DataReader(object):
    
    '''
    classdocs
    '''

    ##################################
    # Class variables
    ##################################
#     filename = "template.xlsx" #name of file. Default is "template.xlsx"
#     filename = "template_example.xlsx" #name of file. Default is "template.xlsx"
    filename = "optical_depth_template_example.xlsx" #name of file. Default is "template.xlsx"    
    
    

    #data starts at row 1. Row 0 is column headings
    DEFAULT_COLUMN_HEADINGS_ROW = 0
    DEFAULT_FIRST_DATA_ROW = 1
    DEFAULT_NUMBER_OF_SHEETS = 4
    
    
    
    
    
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
                       
            

            
                        


    #TODO: this should return nothing. Bad style. Or rename it.  
    def read(self):
        try:
            book = xlrd.open_workbook(self.filename)
        except:
            raise

        return self.readPondListFromFile(book)



##########################################################################################################################
#    READ FILE 
#    Given an inputFile object, opens the workbook and calls the function to read the pondList. 
##########################################################################################################################
    def readFile(self,inputfile):
        #http://stackoverflow.com/questions/10458388/how-do-you-read-excel-files-with-xlrd-on-appengine
        try:
            book =  xlrd.open_workbook(file_contents=inputfile)
        except IOError:
            raise
         
             
        return self.readPondListFromFile(book)


##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
#    READ POND LIST FROM FILE
#    The primary meat of data_reader. 
#
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
    #reads all the pond data from the excel file.
    def readPondListFromFile(self,book):
        '''
        TODO: doc
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
        
        
        if(nsheets<self.DEFAULT_NUMBER_OF_SHEETS):
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
#         print "the number of rows in sheet " + benthic_photo_data_workSheet.name + " is " + str(benthic_data_workSheet_num_rows)
        phytoplankton_photo_data_sheet_num_rows = phytoplankton_photo_data_sheet.nrows
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
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #not in list. Must create Pond object
#                 print "creating pond with lake ID = ", row_lakeID_value, " , and DOY = ", row_doy_value
                emptyShape = BathymetricPondShape({}, self.DEFAULT_DEPTH_INTERVAL_PERCENTAGE)
                pond = Pond(row_lakeID_value, row_doy_value, row_lod_value, row_noonlight_value, row_kd_value, emptyShape, [], [], self.DEFAULT_TIME_INTERVAL, self.DEFAULT_DEPTH_INTERVAL_PERCENTAGE)
#                 pond.set_day_of_year(row_doy_value)
#                 pond.set_lake_id(row_lakeID_value)               
#                 pond.set_light_attenuation_coefficient(row_kd_value)
#                 pond.set_noon_surface_light(row_noonlight_value)
#                 pond.set_length_of_day(row_lod_value) 
#                 pond.set_benthic_photosynthesis_measurements([]) #initialize empty list. #TODO: try testing without this line now that I added in the proper line to the init() in Pond
#                 
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
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                print "oh no"#TODO: better error
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row
#                 print "pond shape thing. ", " row depth is ", row_depth_value," row area is ", row_area_value, " row doy is ", row_doy_value, " row lake ID is ", row_lakeID_value
#                 print "still in pond shape thing, pond lake ID is ", pond.get_lake_id(), " and pond doy is ", pond.get_day_of_year() 
#                 water_surface_area_dict = {row_depth_value:row_area_value}
#                 print "created dict: ", water_surface_area_dict
#                 depth_interval_percentage = pond.get_depth_interval_percentage()
#                 pond_shape_object = BathymetricPondShape(water_surface_area_dict, depth_interval_percentage)  
#                 print "about to update shape. max depth is currently ", pond.get_max_depth()
                pond.update_shape(row_shape)
#                 print "max depth is now ", pond.get_max_depth()
                #add to Pond

            curr_row+=1            
        
        
        
        
        
        
        
        ###############
        #Benthic data
        ###############
        
        sheet = benthic_photo_data_workSheet
        num_rows = benthic_data_workSheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
#             print "adding layers to Ponds. curr_row = " + str(curr_row)
            row = sheet.row(curr_row) 
            
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value
            row_depth_value = row[self.benthic_depth_index].value                                        
            row_pmax_value = row[self.benthic_pmax_index].value                            
            row_ik_value = row[self.benthic_ik_index].value                                        
            
            #find the correct pond
            pond = next((i for i in pondList if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                print "oh no"#TODO: better error
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row
                benthic_measurement = BenthicPhotoSynthesisMeasurement(row_depth_value, row_pmax_value, row_ik_value)                
#                 benthic_measurement.set_depth(row_depth_value)
#                 benthic_measurement.set_pmax(row_pmax_value)  
#                 benthic_measurement.set_ik(row_ik_value)
                
                
                #add to Pond
                pond.add_benthic_measurement_if_photic(benthic_measurement)
            curr_row+=1    
                       

        #end of while loop
#         print "out of while loop. size of pond list is: ", len(pondList)
         
        
        


 
        return pondList

    def write(self, filename="output.xls"):

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

        bppr = p.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
        pid = p.get_lake_id()
        doy = p.get_day_of_year()
        lod = p.get_length_of_day()
        kd = p.get_light_attenuation_coefficient()
        noon_light = p.get_noon_surface_light()
        
        
        
        print ""
        print ""
        print ""           
        print "**************************************************************************************"
        print "lake ID: ", pid, " DOY: ", doy, "bppr is ", str(bppr) 
        
        
        print "testing interpolation"
        current_depth = 0
        depth_interval = 0.1
        max_depth = p.get_max_depth()
        depths = []
        pmaxes = []
        iks = []
        while current_depth<=max_depth:
            bpmax = p.get_benthic_pmax_at_depth(current_depth)
            ik = p.get_benthic_ik_at_depth(current_depth)
#             print "__________________________________________________________________________________________________________________"
#             print "at depth: ", current_depth, " the interpolated value of benthic pmax is: ", bpmax, " and ik is: ", ik
#             print "interpolation also used for area at depth. The calculated value of area at this depth is: ", p.get_pond_shape().get_water_surface_area_at_depth(current_depth)
            depths.append(current_depth)
            pmaxes.append(bpmax+0.0)
            iks.append(ik+0.0)
            current_depth+=depth_interval
        
        print "depths: ", depths
        print "pmaxes", pmaxes
        print "iks", iks
        
        print ""
        print ""
        print ""        
        








if __name__ == "__main__":
    main()
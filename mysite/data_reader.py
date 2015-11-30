'''
Created on Mar 5, 2015

This class reads in data from an excel file, packages it up, and sends it to the model for processing.

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively.
from pond import Pond
from numpy.distutils.npy_pkg_config import FormatError

from benthic_photosynthesis_measurement import BenthicPhotosynthesisMeasurement
from bathymetric_pond_shape import BathymetricPondShape


from phytoplankton_photosynthesis_measurement import PhytoPlanktonPhotosynthesisMeasurement
import sys




#Useful notes: http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/

class DataReader(object):

    '''
    classdocs
    '''

    ##################################
    # Class variables
    ##################################

    # Data    Method    Source
    # pmax,    copied directly    https://drive.google.com/open?id=1jxqTExiqx5Y3rqf8Q3UBus5Rjr5ETVLCUy08Stey4w4
    # alpha,    copied directly    https://drive.google.com/open?id=1jxqTExiqx5Y3rqf8Q3UBus5Rjr5ETVLCUy08Stey4w4
    # beta    copied directly    https://drive.google.com/open?id=1jxqTExiqx5Y3rqf8Q3UBus5Rjr5ETVLCUy08Stey4w4
    # stratum number    copied directly    https://drive.google.com/open?id=1jxqTExiqx5Y3rqf8Q3UBus5Rjr5ETVLCUy08Stey4w4
    # stratum depth    calculated from the daily average of pp_epi_nhw_m2/pp_epi_nhw_m3,pp_met_nhw_m2/pp_met_nhw_m3, and pp_hyp_nhw_m2/pp_hyp_nhw_m3 for the epilimnion, metalimnion, and hypolimnion respectively    https://lter.limnology.wisc.edu/dataset/north-temperate-lakes-lter-primary-production-trout-lake-area-1986-2007
    # light extinction coefficient    copied directly    https://lter.limnology.wisc.edu/dataset/north-temperate-lakes-lter-light-extinction-trout-lake-area-1981-current
    # pppr        https://lter.limnology.wisc.edu/dataset/north-temperate-lakes-lter-primary-production-trout-lake-area-1986-2007
#     filename = "example_data.xls" #Removed everything but one lake from Oct 16_test_data.
    filename = "Sep_17_test_data.xls" #used for testing







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
    yearIndex = 0
    dayOfYearIndex = yearIndex+1 #"DOY"
    lakeIDIndex = dayOfYearIndex+1 #"Lake_ID"

    #indices for Pond vars in pond_data worksheet
    kd_index = lakeIDIndex+1 #index of light attenuation coefficient kd
    noon_surface_light_index = kd_index+1 #"midday.mean.par"
    length_of_day_index = noon_surface_light_index+1 #"LOD" in hours
    

    #indices for vars in benthic_photo_data worksheet
    benthic_light_penetration_proportion_index = lakeIDIndex+1
    benthic_pmax_index = benthic_light_penetration_proportion_index+1 #"pmax.z"
    benthic_ik_index = benthic_pmax_index+1 #"ik_z" light intensity at onset of saturation

    #indices for vars in phytoplankton_photo_data worksheet
    phyto_thermal_layer_index =lakeIDIndex+1
    phyto_depth_index = phyto_thermal_layer_index+1
    phyto_pmax_index = phyto_depth_index+1
    phyto_alpha_index = phyto_pmax_index+1
    phyto_beta_index = phyto_alpha_index+1

    #indices for vars in shape_data worksheet
    shape_ID_index = 0
    shape_depth_index = shape_ID_index+1 #"z" in meters #depth is in several sheets #TODO: different variable?
    shape_area_index = shape_depth_index+1 #"kat_div" in meters squared.


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
            raise Exception("error in read method. xlrd.open_workbook gave an Exception with filename: ", self.filename)

        return self.read_pond_list_from_workbook(book)

    

    #TODO: redundant with read()
    def readFile(self,inputfile):
        '''
        READ FILE
        Given an inputFile object, opens the workbook and calls the function to read the pond_list.
        '''
        #http://stackoverflow.com/questions/10458388/how-do-you-read-excel-files-with-xlrd-on-appengine
        try:
            book =  xlrd.open_workbook(file_contents=inputfile)
        except IOError:
            raise Exception ("Error in readFile. xlrd.open_workbook(file_contents=inputfile) gave exception with inputfile", inputfile)


        return self.read_pond_list_from_workbook(book)


    #reads all the pond data from the excel file.









    def read_pond_list_from_workbook(self,book):
        '''
        READ POND LIST FROM WORKBOOK
        
        Opens the xlrd workbook and returns a list of Pond objects.
        @param book: an xlrd Workbook
        @return: list of Pond objects, storing the information in the workbook.
        @rtype: list
        '''
        ##############
        #Worksheets
        ##############
        nsheets = book.nsheets


        sheet_names = book.sheet_names()

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




        #################################################
        #make all the objects!
        #################################################
        pond_list = [] #list of pond objects. The same water body on a different day counts as a separate "Pond"





        ################################################
        #Make Pond objects from pond_data sheet
        ################################################
        sheet = pond_data_workSheet
        num_rows  = pond_data_workSheet_num_rows #TODO: read until blank space encountered might be better. 
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
            row = sheet.row(curr_row)

            #values
            try:
                row_year_value = row[self.yearIndex].value
                row_doy_value = row[self.dayOfYearIndex].value
                row_lakeID_value = row[self.lakeIDIndex].value
                row_kd_value = float(row[self.kd_index].value)
                row_noonlight_value = float(row[self.noon_surface_light_index].value)
                row_lod_value = float(row[self.length_of_day_index].value)
            except Exception as e:
                print str(e)
                print "Error: couldn't read values properly."
            



            #Do we need to make a pond object?
            pond = None
            pond = next((i for i in pond_list if (i.get_lake_id()== row_lakeID_value and 
                                                 i.get_day_of_year()==row_doy_value and
                                                 i.get_year() == row_year_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #not in list. Must create Pond object
                emptyShape = BathymetricPondShape({}) #initialize with empty dict
                pond = Pond(row_year_value, row_lakeID_value, row_doy_value, row_lod_value, row_noonlight_value, row_kd_value, emptyShape, [], [], self.DEFAULT_TIME_INTERVAL)
                pond_list.append(pond)
            curr_row+=1



        #######################################################
        #we made all the ponds. Time to add all the members
        #######################################################




        #################################
        #Shape data from shape_data sheet
        #################################


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
#             pond = next((i for i in pond_list if (i.get_lake_id()== row_lakeID_value )),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            #http://stackoverflow.com/questions/14366511/return-the-first-item-in-a-list-matching-a-condition
#             matchingPonds = filter(next((i for i in pond_list if (i.get_lake_id()== row_lakeID_value )),None), pond_list)
            for pond in pond_list:
                if(pond.get_lake_id()==row_lakeID_value):
                    pond.update_shape(row_shape)                #add to Pond
            
            #increment while loop to next row
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
            row_year_value = row[self.yearIndex].value
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value
            row_light_penetration_proportion_value = float(row[self.benthic_light_penetration_proportion_index].value)
            row_pmax_value = float(row[self.benthic_pmax_index].value)
            row_ik_value = float(row[self.benthic_ik_index].value)

            #find the correct pond
            pond = None
            pond = next((i for i in pond_list if (i.get_lake_id()== row_lakeID_value and
                                                 i.get_day_of_year()==row_doy_value and
                                                 i.get_year() == row_year_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")
                #TODO: handle this better.
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row
                row_depth_value = pond.calculate_depth_of_specific_light_percentage(row_light_penetration_proportion_value) #convert from light proportions to depth in meters.


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
            row_year_value = row[self.yearIndex].value
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value
            row_thermal_layer_value = row[self.phyto_thermal_layer_index].value
            row_depth_value = row[self.phyto_depth_index].value
            row_phyto_pmax_value = row[self.phyto_pmax_index].value
            row_alpha_value = row[self.phyto_alpha_index].value
            row_beta_value = row[self.phyto_beta_index].value


            #find the correct pond
            pond = None
            pond = next((i for i in pond_list if (i.get_lake_id()== row_lakeID_value and
                                                 i.get_day_of_year()==row_doy_value and
                                                 i.get_year() == row_year_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                raise FormatError("Something went wrong. Benthic Measurement with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")
            else:
                #create PhotoSynthesisMeasurement object using values specific to that benthic_measurement/row

                phyto_measurement = PhytoPlanktonPhotosynthesisMeasurement(row_thermal_layer_value, row_depth_value, row_phyto_pmax_value, row_alpha_value, row_beta_value)
                pond.add_phytoplankton_measurement(phyto_measurement)
                #add to Pond

            curr_row+=1






        return pond_list

    #END OF read_pond_list_from_workbook METHOD








    def write(self, filename="output.xls"):
        '''
        Write to file
        @param filename: the name of the output file. 
        '''
        
        #TODO:return whether it was successful.
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
    sys.exit()
    
    
            

if __name__ == "__main__":
    main()
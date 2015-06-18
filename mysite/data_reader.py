'''
Created on Mar 5, 2015

This class reads in data from an excel file, packages it up, and sends it to the model for processing.

@author: cdleong
'''
import xlrd, xlwt #reading and writing, respectively.
from pond_layer import PhotoSynthesisMeasurement
from pond import Pond
from numpy.distutils.npy_pkg_config import FormatError




#Useful notes: http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/

class DataReader(object):
    
    '''
    classdocs
    '''

    ##################################
    # Class variables
    ##################################
#     filename = "template.xlsx" #name of file. Default is "template.xlsx"
    filename = "template_example.xlsx" #name of file. Default is "template.xlsx"
    


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
    
    #indices common to all sheets
    dayOfYearIndex = 0 #"DOY"
    lakeIDIndex = 1 #"Lake_ID"
    
    
    
    
    #indices for Pond vars in pond_data worksheet
    kd_index = 2 #index of light attenuation coefficient kd
    noon_surface_light_index = 3 #"midday.mean.par"
    length_of_day_index = 4 #"LOD" in hours                
    
    #indices for vars in benthic_photo_data worksheet
    depth_index = 2 #"z" in meters #depth is in several sheets        
    pmax_index = 3 #"pmax.z"
    ikIndex = 4 #"ik_z" light intensity at onset of saturation
    
    #indices for vars in phytoplankton_photo_data worksheet
    
    #indices for vars in shape_data worksheet        
#     depth_index = 2 #"z" in meters #depth is in several sheets #TODO: different variable?            
    area_index = 4 #"kat_div" in meters squared. 
    

    
    


    def __init__(self, filename, testFlag=0):
        '''
        Constructor
        '''        
        if(2==testFlag): #based off pprinputs_colin.xlsx
            self.filename = "pprinputs_Colin.xlsx"
            self.dayOfYearIndex = 1 #"DOY"
            self.lakeIDIndex = 2 #"Lake_ID"
            self.depth_index = 3 #"z" in meters
            self.surface_area_index = 9 #"LA.m2"
            self.gam_index = 10
            self.pmax_index = 13 #"pmax.z"
            self.kd_index = 14 #index of light attenuation coefficient kd
            self.area_index = 16 #"kat_div" in meters squared. 
            self.noon_surface_light_index = 18 #"midday.mean.par"
            self.ikIndex = 21 #"ik_z" light intensity at onset of saturation
            self.length_of_day_index = 27 #"LOD" in hours

        elif(1==testFlag):#based off inputs_pruned.xlsx
            self.filename = "example.xlsx"
            self.dayOfYearIndex = 0 #"DOY"
            self.lakeIDIndex = 1 #"Lake_ID"
            self.depth_index = 2 #"z" in meters
            self.surface_area_index = 3 #"LA.m2"
            self.gam_index = 4
            self.pmax_index = 5 #"pmax.z"
            self.kd_index = 6 #index of light attenuation coefficient kd
            self.area_index = 7 #"kat_div" in meters squared. 
            self.noon_surface_light_index = 8 #"midday.mean.par"
            self.ikIndex = 9 #"ik_z" light intensity at onset of saturation
            self.length_of_day_index = 10 #"LOD" in hours

        else:
            #use default indices
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
            raise IOError("file format incorrect. Number of sheets less than two.")
        
        if(self.POND_DATA_SHEET_NAME in sheet_names and 
           self.BENTHIC_PHOTO_DATA_SHEET_NAME in sheet_names and 
           self.PHYTOPLANKTON_PHOTO_DATA_SHEET_NAME in sheet_names and
           self.SHAPE_DATA_SHEET_NAME in sheet_names):
            print "pond_data sheet detected"
            pond_data_workSheet = book.sheet_by_name(self.POND_DATA_SHEET_NAME)
            print "benthic photosynthesis data sheet detected"
            benthic_photo_data_workSheet = book.sheet_by_name(self.BENTHIC_PHOTO_DATA_SHEET_NAME)
            print "phytoplankton photosynthesis data sheet detected"
            phytoplankton_photo_data_sheet = book.sheet_by_name(self.PHYTOPLANKTON_PHOTO_DATA_SHEET_NAME)
            print "lake shape data sheet detected"
            shape_data_sheet = book.sheet_by_name(self.SHAPE_DATA_SHEET_NAME)
        else:
            print "Standard sheet names not detected. Attempting to read using sheet indices."
            pond_data_workSheet = book.sheet_by_index(self.POND_DATA_SHEET_INDEX)
            benthic_photo_data_workSheet = book.sheet_by_index(self.BENTHIC_PHOTO_DATA_SHEET_INDEX)
            phytoplankton_photo_data_sheet = book.sheet_by_name(self.PHYTOPLANKTON_PHOTO_DATA_SHEET_INDEX)
            shape_data_sheet = book.sheet_by_name(self.SHAPE_DATA_SHEET_INDEX)
        
        ##############
        #Rows, Columns
        ##############
            
        pond_data_workSheet_num_rows = pond_data_workSheet.nrows
        print "the number of rows in sheet " + pond_data_workSheet.name +  " is " + str(pond_data_workSheet_num_rows)        
        benthic_data_workSheet_num_rows = benthic_photo_data_workSheet.nrows
        print "the number of rows in sheet " + benthic_photo_data_workSheet.name + " is " + str(benthic_data_workSheet_num_rows)
        phytoplankton_photo_data_sheet_num_rows = phytoplankton_photo_data_sheet.nrows
        print "the number of rows in sheet " + phytoplankton_photo_data_sheet.name + " is " + str(phytoplankton_photo_data_sheet_num_rows)
        shape_data_sheet_num_rows = shape_data_sheet.nrows
        print "the number of rows in sheet " + shape_data_sheet.name + " is " + str(shape_data_sheet_num_rows)
        
        
        
        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = pond_data_workSheet.row(curr_row)
        print "the column names in sheet \"" + pond_data_workSheet.name +  "\" are "
        print columnnames

        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = benthic_photo_data_workSheet.row(curr_row)
        print "the column names in sheet \"" + benthic_photo_data_workSheet.name +  "\" are "
        print columnnames        
        
        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = phytoplankton_photo_data_sheet.row(curr_row)
        print "the column names in sheet \"" + phytoplankton_photo_data_sheet.name +  "\" are "
        print columnnames                     
        
        curr_row = self.DEFAULT_COLUMN_HEADINGS_ROW
        columnnames = shape_data_sheet.row(curr_row)
        print "the column names in sheet \"" + shape_data_sheet.name +  "\" are "
        print columnnames             
        
        
        #################################################
        #make all the objects!
        #################################################
        pondList = [] #list of pond objects. The same water body on a different day counts as a separate "Pond"



        

        ################################################
        #Make Pond objects from pond_data sheet
        ################################################
        
        num_rows  = pond_data_workSheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
            print "adding Ponds. curr_row = " + str(curr_row) + ", which is still less than num_rows = " + str(num_rows)
            #for quick reference, these are the Pond row indices            
            #     dayOfYearIndex = 0 #"DOY"
            #     lakeIDIndex = 1 #"Lake_ID"
            #     surface_area_index = 2 #"LA.m2"
            #     gam_index = 3
            #     kd_index = 4 #index of light attenuation coefficient kd
            #     noon_surface_light_index = 5 #"midday.mean.par"
            #     length_of_day_index = 10 #"LOD" in hours                     
            row = pond_data_workSheet.row(curr_row)        
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value              
            row_kd_value = row[self.kd_index].value          
            row_noonlight_value = row[self.noon_surface_light_index].value 
            row_lod_value = row[self.length_of_day_index].value            
    
            
            
            #Do we need to make a pond object?
            pond = next((i for i in pondList if (i.getLakeID()== row_lakeID_value and i.getDayOfYear()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #not in list. Must create Pond object
                print "creating pond with lake ID = ", row_lakeID_value, " , and DOY = ", row_doy_value
                pond = Pond()
                pond.setDayOfYear(row_doy_value)
                pond.setLakeID(row_lakeID_value)               
                pond.setLightAttenuationCoefficient(row_kd_value)
                pond.setNoonSurfaceLight(row_noonlight_value)
                pond.setLengthOfDay(row_lod_value) 
                pond.setPondLayerList([]) #initialize empty list. #TODO: try testing without this line now that I added in the proper line to the init() in Pond
                
                pondList.append(pond)         
            curr_row+=1       
            
        print "out of while loop. size of pond list is: ", len(pondList)
            
        #######################################################
        #we made all the ponds. Time to add all the layers. 
        #######################################################
        
        #
        #shape data
        #
        
        #
        #Benthic data
        #
        
        
        num_rows = benthic_data_workSheet_num_rows
        curr_row = self.DEFAULT_FIRST_DATA_ROW #start at 1. row 0 is column headings
        while curr_row<num_rows:
            print "adding layers to Ponds. curr_row = " + str(curr_row)
            row = benthic_photo_data_workSheet.row(curr_row) 
            
            
            #values
            row_doy_value = row[self.dayOfYearIndex].value
            row_lakeID_value = row[self.lakeIDIndex].value                                        
            row_pmax_value = row[self.pmax_index].value                            
            row_ik_value = row[self.ikIndex].value
            
            row_depth_value = row[self.depth_index].value
            row_area_value = row[self.area_index].value        
            
            #find the correct pond
            pond = next((i for i in pondList if (i.getLakeID()== row_lakeID_value and 
                                                 i.getDayOfYear()==row_doy_value)),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
            if pond is None: #something is terribly wrong
                print "oh no"#TODO: better error
                raise FormatError("Something went wrong. Layer with DOY "+str(row_doy_value) + " and Lake ID " + row_lakeID_value + " does not match to any Pond.")                    
            else:
                #create PhotoSynthesisMeasurement object using values specific to that layer/row
                layer = PhotoSynthesisMeasurement()
                layer.set_depth(row_depth_value)
                layer.set_ik(row_ik_value)
                layer.set_pmax(row_pmax_value)
                layer.set_area(row_area_value)         
                
                #add to Pond
                pond.appendPondLayerIfPhotic(layer)    
            curr_row+=1    
                       

        #end of while loop
        print "out of while loop. size of pond list is: ", len(pondList)
         
        
        


 
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


    for p in pondList:
        bppr = p.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
        pid = p.getLakeID()
        print "Daily Whole Lake Primary Production Per Meter Squared For lake ID " + pid + " is " + str(bppr)
        
        backgroundLightAttenuation = p.getLightAttenuationCoefficient()
        zOnePercent = p.calculateDepthOfSpecificLightPercentage(0.01)
        zFiftyPercent = p.calculateDepthOfSpecificLightPercentage(0.5)
        
        print "given a background light coefficient of " + str(backgroundLightAttenuation) + ", the depth of 1% light is about " + str(zOnePercent)
        print "given a background light coefficient of " + str(backgroundLightAttenuation) + ", the depth of 50% light is about " + str(zFiftyPercent)
        
        
        









if __name__ == "__main__":
    main()
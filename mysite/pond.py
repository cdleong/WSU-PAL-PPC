# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 09:38:17 2014

@author: cdleong
"""

import math as mat
import numpy as np
from mysite.pond_shape import PondShape
from mysite.benthic_photosynthesis_measurement import BenthicPhotosynthesisMeasurement
from mysite.bathymetric_pond_shape import BathymetricPondShape
from scipy.interpolate import interp1d
from scipy import interpolate
from mysite.phytoplankton_photosynthesis_measurement import PhytoPlanktonPhotosynthesisMeasurement
from mysite.season_light import SeasonalLightEstimator
import copy










class Pond(object):

    ###################################
    # CONSTANTS
    ###################################
    MINIMUM_VALID_DAY = 0 #New Year's Day
    MAXIMUM_VALID_DAY = 366 #New Year's Eve in a leap year.
    
    MINIMUM_LENGTH_OF_DAY = 0.0  # north of the arctic circle and south of the antarctic one, this is possible during winter.
    MAXIMUM_LENGTH_OF_DAY = 24.0003  # north of the arctic circle and south of the antarctic one, this is possible during summer, if there's a leap second
    
    MINIMUM_NOON_SURFACE_LIGHT = 0.0 #Total darkness. TODO: will this cause divide-by-zero errors?
    MAXIMUM_NOON_SURFACE_LIGHT = 1000000.0  # normally it's in the range of ~1000-2000. A 1000x increase, I'm pretty sure, would sterilize the lake. And probably the Earth. According to http://autogrow.com/general-info/light-measurement, the highest it generally gets on Earth is 2000. Don't wanna exclude nuclear weapons going off over lakes, though, you know?
    
    
    MINIMUM_LIGHT_ATTENUATION_COEFFICIENT = 0.0 #totally, perfectly clear. Units in inverse meters. M^-1 #TODO: will this cause divide-by-zero errors?
    MAXIMUM_LIGHT_ATTENUATION_COEFFICIENT = 100  #Close enough to totally opaque to make no practical difference. At this level, light goes from 100% at depth 0 to 0.005% at 10 centimeters. No meaningful photosynthesis is likely to be going on in this lake.
    
    PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND = 0.01 #1% light penetration is the definition of the photic zone from various sources, including Vadeboncoeur 2008, and http://limnology.wisc.edu/courses/zoo316/REVIEW%20OF%20A%20FEW%20MAJOR%20CONCEPTS.html 
    
    MAXIMUM_LAKE_ID_LENGTH = 140 #value picked arbitrarily during specification process. I chose it because I had Twitter on the mind. Possibly too long. 50 characters would give us enough characters for "Lake Chargoggagoggmanchaoggagoggchaubunaguhgamaugg", the longest lake name in the world...
    
    MAXIMUM_NUMBER_OF_THERMAL_LAYERS = 3
    
    DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS = 0.1 #ten centimeters, 0.1 meters. Arbitrary.  
    
    DEFAULT_FREEZE_DAY = 349#December 15 #arbitrary default value, based on median from http://www.epa.gov/climatechange/pdfs/CI-snow-and-ice-2014.pdf
    DEFAULT_THAW_DAY = 135 #May 15 #arbitrary default value, based on median from http://www.epa.gov/climatechange/pdfs/CI-snow-and-ice-2014.pdf    
    
    
    ###################################
    # VARIABLES
    ###################################    
    
    # identifying variables, aka Primary Key
    lake_ID = ""  # invalid lake ID I'm assuming. #TODO: check.    
    day_of_year = 0  # day of year 0-366    
 
 
    # General pond information. Light/photosynthesis
    length_of_day = 15  # hours of sunlight
    noon_surface_light = 1500  # micromol*m^(-2)*s^(-1 ) (aka microEinsteins?)
    light_attenuation_coefficient = 0.05  # aka "kd"
    
    # shape object. Holds information regarding the shape of the lake. Methods include area at depth, volume at depth, etc.
    pond_shape_object = PondShape()
    
    # benthic photosynthesis data list
    benthic_photosynthesis_measurements = []
    
    # phytoplankton photosynthesis data list #TODO: everything to do with this
    phytoplankton_photosynthesis_measurements = []
    
    #latitude, for seasonal calculations. #TODO: Calculate based on Sudhakhar et al http://www.journal-ijeee.com/content/4/1/21
    latitude = 0.0 
    
    # default intervals for calculations is quarter-hours
    time_interval = 0.25


    
    
    ############################
    # CONSTRUCTOR
    ###########################
    def __init__(self,
                 lake_ID="",
                 day_of_year=0,
                 length_of_day=0.0,
                 noon_surface_light=0.0,
                 light_attenuation_coefficient=0.0,
                 pond_shape_object=PondShape(),
                 benthic_photosynthesis_measurements=[],
                 phytoplankton_photosynthesis_measurements=[],
                 lattitude = 0.0,
                 time_interval=0.25):
        '''
        CONSTRUCTOR
        @param lake_ID:
        @param day_of_year:
        @param length_of_day:
        @param noon_surface_light:
        @param light_attenuation_coefficient:
        @param pond_shape_object: a PondShape object      
        @param benthic_photosynthesis_measurements: a list of BenthicPhotoSynthesisMeasurements
        @param phytoplankton_photosynthesis_measurements:  a list of PhyttoplanktonPhotoSynthesisMeasurements
        '''
        self.set_lake_id(lake_ID)
        self.set_day_of_year(day_of_year)
        self.length_of_day = length_of_day
        self.noon_surface_light = noon_surface_light
        self.light_attenuation_coefficient = light_attenuation_coefficient
        self.set_pond_shape(pond_shape_object)
        self.set_benthic_photosynthesis_measurements(benthic_photosynthesis_measurements)
        self.set_phytoplankton_photosynthesis_measurements(phytoplankton_photosynthesis_measurements)
        self.set_latitude(lattitude)
        self.set_time_interval(time_interval)






    ###################
    # VALIDATORS
    ###################
    
    def validate_numerical_value(self, value, max_value, min_value):
        '''
        Generic numerical validator. 
        Checks if value is >max_value or <min_value.
        If it's outside the valid range it'll be set to the closest valid value.
        @param value: numerical value of some sort to be checked.
        @param max_value: numerical value. Max valid value.
        @param min_value: numerical value. Min valid value.
        @return: a valid value in the range (min_value,max_value), inclusive 
        @rtype: numerical value  
        '''
        validated_value = 0
        if(value < min_value):
            validated_value = min_value
        elif(value > max_value):
            validated_value = max_value
        else: 
            validated_value = value
        return validated_value        
    
    def validate_day_of_year(self, day_of_year=0):
        '''
        
        @param day_of_year: the day of year the measurement was made.
        @return: a valid value in the range (Pond.MINIMUM_VALID_DAY,Pond.MAXIMUM_VALID_DAY), inclusive 
        @rtype: int
        '''        
        return self.validate_numerical_value(day_of_year, Pond.MAXIMUM_VALID_DAY, Pond.MINIMUM_VALID_DAY)
            
    def validate_length_of_day(self, length_of_day=0.0):
        '''
        
        @param length_of_day:
        @return: a valid value in the range (Pond.MINIMUM_LENGTH_OF_DAY,Pond.MAXIMUM_LENGTH_OF_DAY), inclusive 
        @rtype:  float
        '''
        return self.validate_numerical_value(length_of_day, Pond.MAXIMUM_LENGTH_OF_DAY, Pond.MINIMUM_LENGTH_OF_DAY)     
    
    def validate_proportional_value(self, proportional_value):
        '''
        @param proportional_value:
        @return: a value in the range (0.0, 1.0) inclusive
        @rtype: float 
        '''
        validated_proportional_value = self.validate_numerical_value(proportional_value, 1.0, 0.0)
        return validated_proportional_value
    
    def validate_depth(self, depth=0.0):
        '''
        @param depth:
        @return: 
        @rtype: float
        '''
        pond_shape_object = self.get_pond_shape()
        validated_depth = pond_shape_object.validate_depth(depth)
        return validated_depth
    
    def validate_noon_surface_light(self, noon_surface_light=0.0):
        '''
        @param noon_surface_light:
        @return: 
        @rtype: float 
        '''
        validated_noon_surface_light = self.validate_numerical_value(noon_surface_light, Pond.MAXIMUM_NOON_SURFACE_LIGHT, Pond.MINIMUM_NOON_SURFACE_LIGHT)
        return validated_noon_surface_light
    
    def validate_light_attenuation_coefficient(self, light_attenuation_coefficient):
        validated_light_attenuation_coefficient = self.validate_numerical_value(light_attenuation_coefficient, Pond.MAXIMUM_LIGHT_ATTENUATION_COEFFICIENT, Pond.MINIMUM_LIGHT_ATTENUATION_COEFFICIENT)
        return validated_light_attenuation_coefficient
    
    def validate_types_of_all_items_in_list(self, items=[], desired_type=object):
        '''
        @param items:
        @param desired_type:

        '''
        all_valid = False
        if(all(isinstance(item, desired_type) for item in items)):            
            all_valid = True
        else: 
            all_valid = False
        return all_valid


    def validate_time(self, time):
        validated_time =time
        length_of_day = self.get_length_of_day()
        if(time>length_of_day):
            validated_time =length_of_day
        elif(time<0.0):
            validated_time = 0.0
         
            
        return validated_time






    #######################
    # GETTERS
    #######################
    def get_lake_id(self):
        '''
        Get Lake ID
        Getter method.
        @return: the ID of the lake.
        @rtype: string
        '''
        return self.__lake_ID


    def get_day_of_year(self):
        '''
        Get Day of Year
        Getter method.
        @return: the day of on which measurements occurred.
        @rtype: int
        '''
        return self.__day_of_year


    def get_length_of_day(self):
        '''
        Get Length Of Day
        Getter method
        @return: the length of day, in hours, on the day of measurements.
        @rtype: float
        '''
        return self.__length_of_day


    def get_noon_surface_light(self):
        '''
        Get Noon Surface Light
        @return: The surface light intensite at solar noon, in micromoles per square meter per second(umol*m^-2*s^-1)
        @rtype: float
        '''
        return self.__noon_surface_light


    def get_light_attenuation_coefficient(self):
        '''
        Get Light Attenuation Coefficient. 
        AKA background light attenuation, kd.
        @return:light attenuation coefficient.  
        @rtype: float
        '''
        return self.__light_attenuation_coefficient

    def get_pond_shape(self):
        '''
        Get Pond Shape
        @return: a PondShape object, holding all the information describing the shape of the lake.
        @rtype: PondShape
        '''
        return self.pond_shape_object


    def get_benthic_photosynthesis_measurements(self):
        '''
        Get Benthic Photosynthesis Measurements
        @return: the list containing all the Benthic Photosynthesis Measurement objects, that hold the information regarding benthic photosynthesis.
        @rtype: list containing BenthicPhotosynthesisMeasurement objects
        '''
        return self.__benthic_photosynthesis_measurements


    def get_phytoplankton_photosynthesis_measurements(self):
        '''
        Get Phytoplankton Photosynthesis Measurements
        @return: the list containing all the Phytoplankton Photosynthesis Measurement objects, that hold the information regarding benthic photosynthesis.
        @rtype: list containing PhytoplanktonPhotoSynthesisMeasurement objects        
        '''
        return self.__phytoplankton_photosynthesis_measurements
    



    

    
    def get_max_depth(self):
        '''
        Get Max Depth
        '''
        return self.get_pond_shape().get_max_depth()
    
    
    
    def get_latitude(self):
        '''
        Get Latitude
        '''
        return self.__latitude

    def get_time_interval(self):
        '''
        Get Time Interval
        '''
        return self.__time_interval
    
    
    #######################
    # SETTERS
    #######################

    def set_lake_id(self, lake_id):
        '''
        Set Lake ID
        @param lake_id: 
        '''
        self.__lake_ID = lake_id


    def set_day_of_year(self, day_of_year):
        '''
        Set Day Of Year
        Validates the value
        @param day_of_year:         
        '''        
        validated_day_of_year = self.validate_day_of_year(day_of_year)
        self.__day_of_year = validated_day_of_year


    def set_length_of_day(self, length_of_day):
        '''
        Set Length Of Day
        Validates the value
        @param length_of_day:         
        '''     
        validated_length_of_day = self.validate_length_of_day(length_of_day)
        self.__length_of_day = validated_length_of_day


    def set_noon_surface_light(self, noon_surface_light):
        '''
        Set Noon Surface Light
        Validates the value 
        @param noon_surface_light:        
        '''   
        validated_light = self.validate_noon_surface_light(noon_surface_light)
        self.__noon_surface_light = validated_light


    def set_light_attenuation_coefficient(self, light_attenuation_coefficient):
        '''
        Set Light Attenuation Coefficient
        Validates the value      
        @param light_attenuation_coefficient: Also known as light extinction coefficient, or just kd. Units in inverse meters.   
        '''           
        validated_light_attenuation_coefficient = self.validate_light_attenuation_coefficient(light_attenuation_coefficient)
        self.__light_attenuation_coefficient = validated_light_attenuation_coefficient

    def set_latitude(self, latitude):
        '''
        Set Latitude
        @param latitude: 
        '''
        self.__latitude = latitude
        
    def set_time_interval(self, value):
        '''
        Set Time Interval
        '''
        self.__time_interval = value\
        
    def set_pond_shape(self, pond_shape_object):
        '''
        Set Time Interval
        Validates the value        
        '''           
        if(isinstance(pond_shape_object, PondShape)):
            print "setting pond shape."
            self.pond_shape_object = pond_shape_object
        else:
            raise Exception("cannot set pond shape. Invalid type")
        


    def set_benthic_photosynthesis_measurements(self, values=[]):
        '''
        Set Benthic Photosynthesis Measurements
        Validates the value        
        '''           
        all_valid = self.validate_types_of_all_items_in_list(values, BenthicPhotosynthesisMeasurement)
        if(all_valid):
            self.__benthic_photosynthesis_measurements = values
        else:
            raise Exception("ERROR: all values in benthic_photosynthesis_measurements must be of type BenthicPhotosynthesisMeasurement")


    def set_phytoplankton_photosynthesis_measurements(self, values=[]):
        '''
        Set Phytoplankton Photosynthesis Measurements
        '''
        # TODO: use a dict to ensure 3 unique layers.
        all_valid = self.validate_types_of_all_items_in_list(values, PhytoPlanktonPhotosynthesisMeasurement)
        length_valid = len(values)<=self.MAXIMUM_NUMBER_OF_THERMAL_LAYERS
        
        if(not all_valid):
            raise Exception("ERROR: all values in phytoplankton_photosynthesis_measurements must be of type PhytoPlanktonPhotosynthesisMeasurement")
        elif(not length_valid):
            raise Exception("ERROR: there must be 0 to 3 thermal layers")
        else:
            self.__phytoplankton_photosynthesis_measurements = values





    #############################
    # WEIRD AUTOGENERATED THINGS
    #############################        

    def del_lake_id(self):
        del self.__lake_ID


    def del_day_of_year(self):
        del self.__day_of_year


    def del_length_of_day(self):
        del self.__length_of_day


    def del_noon_surface_light(self):
        del self.__noon_surface_light


    def del_light_attenuation_coefficient(self):
        del self.__light_attenuation_coefficient


    def del_benthic_photosynthesis_measurements(self):
        del self.__benthic_photosynthesis_measurements


    def del_phytoplankton_photosynthesis_measurements(self):
        del self.__phytoplankton_photosynthesis_measurements

    def del_latitude(self):
        del self.__latitude

    def del_time_interval(self):
        del self.__time_interval



    lake_ID = property(get_lake_id, set_lake_id, del_lake_id, "lake_ID's docstring")
    day_of_year = property(get_day_of_year, set_day_of_year, del_day_of_year, "day_of_year's docstring")
    length_of_day = property(get_length_of_day, set_length_of_day, del_length_of_day, "length_of_day's docstring")
    noon_surface_light = property(get_noon_surface_light, set_noon_surface_light, del_noon_surface_light, "noon_surface_light's docstring")
    light_attenuation_coefficient = property(get_light_attenuation_coefficient, set_light_attenuation_coefficient, del_light_attenuation_coefficient, "light_attenuation_coefficient's docstring")
    benthic_photosynthesis_measurements = property(get_benthic_photosynthesis_measurements, set_benthic_photosynthesis_measurements, del_benthic_photosynthesis_measurements, "benthic_photosynthesis_measurements's docstring")
    phytoplankton_photosynthesis_measurements = property(get_phytoplankton_photosynthesis_measurements, set_phytoplankton_photosynthesis_measurements, del_phytoplankton_photosynthesis_measurements, "phytoplankton_photosynthesis_measurements's docstring")
    latitude = property(get_latitude, set_latitude, del_latitude, "latitude's docstring")
    time_interval = property(get_time_interval, set_time_interval, del_time_interval, "time_interval's docstring")                     
       



    ########################################
    # Appenders/mutators
    ########################################
    def add_benthic_measurement(self, measurement=BenthicPhotosynthesisMeasurement):
        if(isinstance(measurement, BenthicPhotosynthesisMeasurement)):
            self.benthic_photosynthesis_measurements.append(measurement)
        else:
            raise Exception("ERROR: cannot add measurement to benthic measurements list - measurement must be of type BenthicPhotosynthesisMeasurement")

    def add_benthic_measurement_if_photic(self, measurement):
        z1Percent = self.calculate_depth_of_specific_light_percentage(self.PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND)
        if(measurement.get_depth()<=z1Percent):
            self.add_benthic_measurement(measurement)
        else: 
            print "measurement not within photic zone"
            
    
    def add_phytoplankton_measurement(self, measurement=PhytoPlanktonPhotosynthesisMeasurement):
        if(isinstance(measurement, PhytoPlanktonPhotosynthesisMeasurement)):
            if(len(self.phytoplankton_photosynthesis_measurements)>0):
                existing_measurement = next((i for i in self.phytoplankton_photosynthesis_measurements if (i.get_thermal_layer()==measurement.get_thermal_layer())),None) #source: http://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
                if(existing_measurement is not None):
                    index = measurement.get_thermal_layer()-1
                    self.phytoplankton_photosynthesis_measurements.remove(existing_measurement)
                    self.phytoplankton_photosynthesis_measurements.insert(index, measurement)
                
                
            self.phytoplankton_photosynthesis_measurements.append(measurement)
        else:
            raise Exception("ERROR: cannot add measurement to benthic measurements list - measurement must be of type PhytoPlanktonPhotosynthesisMeasurement")
        
        
    def remove_benthic_measurement(self, measurement=BenthicPhotosynthesisMeasurement):
        self.benthic_photosynthesis_measurements.remove(measurement)
        
    def update_shape(self, other_pond_shape):
        our_shape = self.get_pond_shape()
        if(isinstance(other_pond_shape, BathymetricPondShape)):
            our_shape.update_shape(other_pond_shape)
            self.pond_shape_object = our_shape

    ############################################
    ############################################
    ## SCIENCE FUNCTIONS
    ## This section is where the science occurs.    
    ############################################
    ############################################
    
   
    ###########################################################
    #BENTHIC PHOTO METHODS
    ###########################################################    
    
    ##############################
    # BENTHIC PRIMARY PRODUCTIVITY
    ##############################    
    def calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(self, depth_interval = DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS, use_littoral_area=True):        
        '''
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        Almost everything else in this entire project works to make this method work.
        #TODO: allow specification of littoral or surface area
        #TODO: user-specified depth interval.
        @return: Benthic Primary Production, mg C per meter squared, per day.
        @rtype: float 
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        '''
        time_interval = self.get_time_interval()
        length_of_day = self.get_length_of_day() #TODO: Fee normalized this around zero. Doesn't seem necessary, but might affect the periodic function. 
 
 

        benthic_primary_production_answer = 0.0  # mg C per day
        current_depth_interval = 0.0
        previous_depth = 0.0
        current_depth = 0.0
        total_littoral_area=self.calculate_total_littoral_area()
        total_surface_area = self.get_pond_shape().get_water_surface_area_at_depth(0.0)
 
        #for each depth interval #TODO: integration over whole lake?
        while current_depth<self.calculate_photic_zone_lower_bound():
            bpprz = 0.0  # mg C* m^-2 *day    
            
            #depth interval calculation
            previous_depth = current_depth
            current_depth +=depth_interval
            current_depth_interval = current_depth-previous_depth
            


            
            area = self.get_pond_shape().get_sediment_surface_area_at_depth(current_depth, current_depth_interval)
                        
            ik_z = self.get_benthic_ik_at_depth(current_depth)
            benthic_pmax_z = self.get_benthic_pmax_at_depth(current_depth)
            
            if(True==use_littoral_area):
                f_area = area/total_littoral_area #TODO: these add up to 1.0, right?
            else: 
                f_area = area/total_surface_area

            
            # for every time interval                 
            t = 0.0  # start of day
            while t < length_of_day:
                bpprzt = 0.0 
                izt = self.calculate_light_at_depth_and_time(current_depth, t)
                bpprzt = self.calculate_benthic_primary_productivity(izt, benthic_pmax_z, ik_z)
                                
                bpprz += bpprzt
  
                t += time_interval
            bpprz = bpprz / (1 / time_interval)  # account for the fractional time interval. e.g. dividing by 1/0.25 is equiv to dividing by 4
            weighted_bpprz = bpprz * f_area  # normalizing
            

                    
                
            benthic_primary_production_answer += weighted_bpprz             
        

        return benthic_primary_production_answer    
    
        
                
                        
    def calculate_total_seasonal_benthic_primary_production(self, depth_interval = DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS, use_littoral_area=True):
        '''
        Incomplete implementation
        Future work: calculate this accurately TODO: that.
        '''
        print ""
        seasonal_light_estimator = SeasonalLightEstimator(self.latitude)
        season_start_day = self.DEFAULT_THAW_DAY
        season_end_day = self.DEFAULT_FREEZE_DAY
        pond_day = copy.deepcopy(self)
        littoral_area = self.calculate_total_littoral_area()
        surface_area = self.get_pond_shape().get_water_surface_area_at_depth(0) #TODO: more elegant.
        day = season_start_day
        tppp = 0.0 #total benthic primary production
        while day<season_end_day:
            noon_surface_light = seasonal_light_estimator.calculate_noon_light(day)
            length_of_day = seasonal_light_estimator.calculate_day_length(day)            
            pond_day.set_noon_surface_light(noon_surface_light)
            pond_day.set_length_of_day(length_of_day)
            bppr= pond_day.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(depth_interval, use_littoral_area)
#             print "bppr on day ", day, " is ", bppr
            tbpp_day = 0.0
            if(True==use_littoral_area):
                tbpp_day=bppr*littoral_area
            else:
                tbpp_day=bppr*surface_area
            tppp+=tbpp_day
            day = day+ 1
        
        return tppp
        
        
        
        
        
        
    
    def get_benthic_pmax_at_depth(self, depth=0.0):
        '''
        Get Benthic Pmax At Depth
        @return:
        @rtype:  
        '''    
        #if depth is lower than the depth of 1% light, pmax approaches zero.
        if(self.check_if_depth_in_photic_zone(depth)==False):
            return 0
        
        
        validated_depth = self.validate_depth(depth)            
        pmax_values_list = []
        depths_list = []
        for measurement_value in self.get_benthic_photosynthesis_measurements():
            pmax_value = measurement_value.get_pmax()
            depth_value = measurement_value.get_depth()
            pmax_values_list.append(pmax_value)
            depths_list.append(depth_value)
        bpmax_at_depth = self.interpolate_values_at_depth(validated_depth, depths_list, pmax_values_list)
        return bpmax_at_depth
    
    def get_benthic_ik_at_depth(self, depth=0.0):
        '''
        @return: 
        @rtype: 
        '''
        validated_depth = self.validate_depth(depth)
        

        values_list = []
        depths_list = []
        for measurement_value in self.get_benthic_photosynthesis_measurements():
            ik_value = measurement_value.get_ik()
            depth_value = measurement_value.get_depth()
            values_list.append(ik_value)
            depths_list.append(depth_value)
        
        
        ik_at_depth = self.interpolate_values_at_depth(validated_depth, depths_list, values_list)
        
        return ik_at_depth         
    
    def calculate_benthic_primary_productivity(self, light_at_time_and_depth, benthic_pmax_z, benthic_ik_z):
        '''
        Equation for productivity that doesn't include photoinhibition, etc. 
        TODO: Source of this equation? Doesn't match the one from Wikipedia. 
        @return: 
        '''
        bpprzt = benthic_pmax_z * np.tanh(light_at_time_and_depth / benthic_ik_z)
        return bpprzt
    
    def get_benthic_measurements_sorted_by_depth(self):
        '''
        Sort
        @return: sorted benthic measurements
        @rtype: list of BenthicPhotosynthesisMeasurement objects.
        '''
        #http://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
        unsorted_measurements = self.get_benthic_photosynthesis_measurements()
        sorted_measurements = sorted(unsorted_measurements, key=lambda x: x.get_depth(), reverse=False)
        return sorted_measurements       
        
    ###########################################################
    #PHYTO PHOTO METHODS
    ###########################################################
    
    
    def calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared(self, depth_interval = DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS):
        '''
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        Calculate Daily Whole-lake Phytoplankton Primary Production
        Almost everything else in this entire project works to make this method work.
        #TODO: allow specification of littoral or surface area
        #TODO: user-specified depth interval.        
        @return: Benthic Primary Production, mg C per meter squared, per day.
        @rtype: float 
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        '''
        
        #TODO: validate interval        
        time_interval = self.get_time_interval() #hours 
        length_of_day = self.get_length_of_day()  
 
 

        pppr_total = 0.0  # mg C per day
        current_depth = 0.0 #lake surface
        photic_zone_lower_bound = self.calculate_photic_zone_lower_bound()
        photic_volume = self.get_pond_shape().get_volume_above_depth(photic_zone_lower_bound, depth_interval)
        max_depth = self.get_pond_shape().get_max_depth()
        mean_depth = self.get_pond_shape().get_mean_depth()
        total_volume = self.get_pond_shape().get_volume_above_depth(max_depth, depth_interval)
        surface_area = self.get_pond_shape().get_water_surface_area_at_depth(0)
        depth_ratio = mean_depth/max_depth
        


        #for each depth interval #TODO: integration over whole lake?
        while current_depth<self.calculate_photic_zone_lower_bound():
            current_depth+=depth_interval
            ppprz = 0.0  # mg C* m^-3 *day    

            
            #fractional volume
            
            volume = self.get_pond_shape().get_volume_at_depth(current_depth, depth_interval) #m^3
            
            f_volume = volume/photic_volume #unitless ratio
 



            
            # for every time interval                 
            t = 0.0  # start of day
            while t < length_of_day:
                ppprzt = 0.0  
                izt = self.calculate_light_at_depth_and_time(current_depth, t) #umol*m^-2*s^-1
                ppprzt = self.calculate_phytoplankton_primary_productivity(izt, current_depth) #(mg/m^3/hr)
                                
                ppprz += ppprzt
  
                t += time_interval
            ppprz = ppprz / (1 / time_interval)  # (mgC/m^3/hr)*hr = mgC/m^3. Account for the fractional time interval. e.g. dividing by 1/0.25 is equiv to dividing by 4
            ppprz = ppprz*volume #(mgC/m^3) *m^3 = total in this volume, mgC. 
            #OK, now we have ppprz in this volume. Let's weight using the fractional volume
#             weighted_pppr_z = ppprz * f_volume #mg/m^3  #production rate multiplied by the fraction of production rate across all volumes.           
                
#             pppr_total += weighted_pppr_z #mg/m^3
            pppr_total += ppprz #mgC            
        
        
        pppr_m2 =pppr_total/surface_area  #mgC/m^2/day 
        return pppr_m2 #mgC/m^2/day          
    

        
                
                        
    def calculate_total_seasonal_phytoplankton_primary_production(self, depth_interval = DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS):
        '''
        Incomplete implementation
        Future work: calculate this accurately TODO: that.
        '''
        print ""
        seasonal_light_estimator = SeasonalLightEstimator(self.latitude)
        season_start_day = self.DEFAULT_THAW_DAY
        season_end_day = self.DEFAULT_FREEZE_DAY
        pond_day = copy.deepcopy(self)
        surface_area = self.get_pond_shape().get_water_surface_area_at_depth(0) #TODO: more elegant.
        day = season_start_day
        tbpp = 0.0 #total benthic primary production
        while day<season_end_day:
            noon_surface_light = seasonal_light_estimator.calculate_noon_light(day)
            length_of_day = seasonal_light_estimator.calculate_day_length(day)            
            pond_day.set_noon_surface_light(noon_surface_light)
            pond_day.set_length_of_day(length_of_day)
            pppr= pond_day.calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared()
#             print "pppr on day ", day, " is ", pppr
            tbpp_day = 0.0

            tbpp_day=pppr*surface_area
            tbpp+=tbpp_day
            day = day+ 1
        
        return tbpp    
    
    def get_phyto_pmax_at_depth(self, depth):
        '''
        @param depth:
        @return: 
        @rtype:  
        '''
        validated_depth = self.validate_depth(depth)
        pmax = 0.0
        measurement = self.get_phytoplankton_photosynthesis_measurement_at_depth(validated_depth)  
        if(measurement is not None):
            pmax = measurement.get_pmax()
        return pmax
    
    def get_phyto_alpha_at_depth(self, depth):
        '''
        @param depth:
        @return: 
        @rtype:  
        '''
        validated_depth = self.validate_depth(depth)
        phyto_alpha = 0.0 #TODO: safer value?
        measurement = self.get_phytoplankton_photosynthesis_measurement_at_depth(validated_depth)
        if(measurement is not None):
            phyto_alpha = measurement.get_phyto_alpha()
        return phyto_alpha
    
    def get_phyto_beta_at_depth(self, depth):
        '''
        @param depth:
        @return: 
        @rtype:  
        '''      
        validated_depth = self.validate_depth(depth)
        phyto_beta = 0.0 #TODO: safer value?
        measurement = self.get_phytoplankton_photosynthesis_measurement_at_depth(validated_depth)  
        if(measurement is not None):
            measurement.get_phyto_beta()
        return phyto_beta
    
    
    def calculate_phytoplankton_primary_productivity(self, izt, depth):
        '''
        Calculate Phytoplankton Primary Productivity
        @param izt: light at depth z, time t (umol*m^-2*s^-1) 
        @param depth: depth (m)
        @return 
        '''
        ppr = 0.0

        phyto_photo_measurement_z = self.get_phytoplankton_photosynthesis_measurement_at_depth(depth)
        if(phyto_photo_measurement_z is not None):
            
            
            phyto_pmax = phyto_photo_measurement_z.get_pmax() #mg C per m^3 per hour (mgC/m^3/hr)
            phyto_alpha = phyto_photo_measurement_z.get_phyto_alpha() #(mgC/m^3/hr)/(umol/m^2/s^1) 
            phyto_beta = phyto_photo_measurement_z.get_phyto_beta() #(mg/m^3/hr)/(umol/m^2/s^1) 
            
            #P-I curve equation derived from Jassby/Platt, and specifically from http://web.pdx.edu/~rueterj/courses/esr473/notes/pvsi.htm
            #that website, of course, got it from "Photoinhibition of photosynthesis in natural assemblages of marine phytoplankton" By Platt, T., C.L. Gallegos and W.G. Harrison 1979.
            interim_value = 1-mat.exp(-phyto_alpha*izt/phyto_pmax)#[(mg/m^3/hr)/(umol/m^2/s^1) * (umol/m^2/s^1) = (mg/m^3/hr)
            other_interim_value = mat.exp(-phyto_beta*izt/phyto_pmax) #(mg/m^3/hr), same as above
            ppr=phyto_pmax = phyto_pmax*interim_value*other_interim_value #(mg/m^3/hr)
           
            
        return ppr
            
        
    
    def get_phytoplankton_photosynthesis_measurement_at_depth(self, depth):
        '''
        @param depth:
        @return: shallowest layer measurement deeper than specified depth, or None if not found.
        @rtype:  
        '''        
        #find the shallowest layer_measurement that's deeper than this depth.
        #example: layers are at 5, 10, 15. Depth given is                 
        measurement =None
        reverse_sorted_measurements = self.get_phyto_measurements_sorted_by_depth(True) #sort reversed by depth. 
        for layer_measurement in reverse_sorted_measurements:
            if (layer_measurement.get_depth()>depth):
                #the bottom of said thermal layer is deeper than the depth we want.
                measurement = layer_measurement
        return measurement
                
    def get_phyto_measurements_sorted_by_depth(self, reverse= False):
        '''
        Sort
        @return: sorted benthic measurements
        @rtype: list of BenthicPhotosynthesisMeasurement objects.
        '''
        #http://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
        thing = reverse
        unsorted_measurements = self.get_phytoplankton_photosynthesis_measurements()
        sorted_measurements = sorted(unsorted_measurements, key=lambda x: x.get_depth(), reverse=thing)
        return sorted_measurements           
    
    
    ###########################################################
    #OTHER SCIENCE METHODS
    ###########################################################    
    def check_if_depth_in_photic_zone(self, depth):
        '''
        Check If Depth In Photic Zone
        Used when adding photosynthesis measurements, calculating things, etc. 
        @param depth: depth to check, in meters. 
        @return: True if in photic zone, False if not. 
        '''
        in_zone = True
        photic_zone_lower_bound = self.calculate_photic_zone_lower_bound() 
        if(depth<0 or depth>photic_zone_lower_bound):
            in_zone = False
        else: 
            in_zone = True
        return in_zone

        
    def calculate_photic_zone_lower_bound(self):
        '''
        Calculate Photic Zone Lower Bound
        This is actually redundant. It can be accomplished just by calling calculate_depth_of_specific_light_percentage with PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND.
        That said, I might one day wish to decouple photic zone lower bound from calculate_depth_of_specific_light_percentage, so I'm leaving this.
        NOTE: returns max depth if lower bound is deeper than max depth.
        @return: lower bound of the photic zone, in meters.
        @rtype: float
        '''
        lower_bound = self.calculate_depth_of_specific_light_percentage(self.PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND)
        max_depth = self.get_max_depth()
        if(lower_bound>max_depth):
            lower_bound = max_depth
        return lower_bound
        
            
        
    def calculate_depth_of_specific_light_percentage(self, desired_light_proportion=1.0):
        '''
        Calculate Depth Of Specific Light Proportion
        
        Calculates the depth of, say, 1% light.
        Uses: light attenuation coefficient kd. 
        This is how "optical depth" works.         
        
        Given a proportion, say 0.01 for 1%, 
        calculates the depth of the pond at which that much light will reach.
        
        Equation on which this is based: Iz/I0=e^-kd*z
        Given a desired proportion for Iz/I0, and solved for z, this simplifies to 
        z= kd/ln(desired proportion)
        
         
         
        @param desired_light_proportion:a float value from 0 to 1.0 
        @return: the depth, in meters, where that proportion of light penetrates.
        @rtype: float         
        '''         
        validated_desired_light_proportion = self.validate_proportional_value(desired_light_proportion)
        depthOfSpecifiedLightProportion = 0.0  # the surface of the pond makes a good, safe default depth
        backgroundLightAttenuation = self.get_light_attenuation_coefficient()
        
         

 
        if(validated_desired_light_proportion < 1.0 and validated_desired_light_proportion > 0.0):         
            naturalLogOfProportion = mat.log(validated_desired_light_proportion)
             
            depthOfSpecifiedLightProportion = naturalLogOfProportion / -backgroundLightAttenuation  # TODO: check if zero.             
             
        return depthOfSpecifiedLightProportion 
    
    def calculate_light_proportion_at_depth(self, depth=0.0):
        '''
        Calculate Light Proportion at Depth
                
        The inverse operation of "Calculate Depth Of Specific Light Proportion". Given the depth, calculates what proportion of light
        will be visible at that depth.
        
        Given a depth, say "10" for 10 meters, calculates the proportion of light (Iz/I0) that will reach that depth 
        
        Equation on which this is based: Iz/I0=e^-kd*z        
        
        If you want Iz, just do Iz*I0 again. #TODO: just light at depth z
        
        @param depth: depth in meters. 
        @return: proportion of light at depth z as a number in the range (0.0, 1.0), inclusive. 
        @rtype:  float
        '''       
        validated_depth = self.validate_depth(depth)
        light_attenuation_coefficient = self.get_light_attenuation_coefficient()
        multiplied = light_attenuation_coefficient * validated_depth
        light_proportion_at_depth = mat.exp(-multiplied)
        return light_proportion_at_depth
    
    
    


    def calculate_light_at_depth_and_time(self, depth, time):
        '''
        Calculate Light At Depth And Time
        @param depth:
        @param time:
        @return: the light at that depth and time, in micromoles/m^2/sec
        @rtype: float 
        '''
        
        validated_depth = self.validate_depth(depth)
        validated_time = self.validate_time(time)
        noonlight = self.get_noon_surface_light()
        length_of_day = self.get_length_of_day()
        surface_light_at_t = noonlight * np.sin(np.pi * validated_time / length_of_day)
        light_attenuation_coefficient = self.get_light_attenuation_coefficient()
        light_at_z_and_t = surface_light_at_t* np.exp(-light_attenuation_coefficient * validated_depth)
        return light_at_z_and_t
        

    
    def calculate_total_littoral_area(self):
        '''
        Calculate Total Littoral Area
        Uses kd to calculate the depth of 1% light, then uses the pond_shape to find sediment area above that.
        @return:
        @rtype:  
        '''
        z1percent = self.calculate_photic_zone_lower_bound()        
        shape_of_pond = self.get_pond_shape()
        
        littoral_area = shape_of_pond.get_sediment_area_above_depth(z1percent, Pond.DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS)
        return littoral_area    
    
    def calculate_total_photic_volume(self):
        z1percent = self.calculate_photic_zone_lower_bound()        
        shape_of_pond = self.get_pond_shape()
        
        photic_volume = shape_of_pond.get_volume_above_depth(z1percent, Pond.DEFAULT_DEPTH_INTERVAL_FOR_CALCULATIONS)
        return photic_volume
        

    def interpolate_values_at_depth(self, depth, depths_list=[], values_list=[]):
        '''
        INTERPOLATE VALUES AT DEPTH
        Essentially, given an array of "x" (validated_depths) and "y" values, interpolates "y" value at specified validated_depth.
        
        Based on SciPy interpolation:http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        
        Used for things like, "I have pmax values at 0 and 1, but I need one at 0.5)
        
        @param depth: depth to interpolate _at_. In the above example, this would be 0.5 
        @param depths_list: list of depths where we have data.
        @param values_list: corresponding data that goes with the depths. So value[0] is the value at depth[0] for example.
        @return: a single value, the value calculated for the specified depth.        
        @rtype: a number. #TODO: what _kind_ of number?
        '''

        
        # Uses http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html   
        validated_depth = self.validate_depth(depth)
        
        max_depth_given = max(depths_list)
        min_depth_given = min(depths_list)
        
        if(validated_depth>max_depth_given):            
#             print "depth is",validated_depth, "cannot interpolate outside the range of measurements given. setting to max depth = ", max_depth_given
            validated_depth= max_depth_given
        elif(min_depth_given<min_depth_given):
#             print "depth is",validated_depth, "cannot interpolate outside the range of measurements given. setting to min depth = ", min_depth_given
            validated_depth= min_depth_given            
            
        
        # get interpolation function
        x = depths_list
        y = values_list 
        f = interp1d(x, y)
        
        #magic from http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        #SPLINES....!!!
#         tck = interpolate.splrep(x, y, s=0)
#         xnew = [validated_depth]
#         spline_interpolated = interpolate.splev(xnew, tck, der=0) #0th derivative
        linear_interpolated = f(validated_depth)         
        
        
        

#         value_at_depth = spline_interpolated[0] #TODO: inefficient to get the whole array and return just one.
        value_at_depth = linear_interpolated
        return value_at_depth        
    
    
    


    
    def calculate_depths_of_specific_light_percentages(self, light_penetration_depths):
        '''
        CALCULATE DEPTHS OF SPECIFIC LIGHT PERCENTAGES
        Given a list of light penetration depths returns the depth in meters needed for each of those light penetration levels.
        I only used this once, for making some testing data. 
        @rtype: list 
        '''
        depths = []
        for light_penetration_depth in light_penetration_depths:
            depth_m_of_light_penetration = self.calculate_depth_of_specific_light_percentage(light_penetration_depth)
            depths.append(depth_m_of_light_penetration)
        return depths

    
    
     



############################################################################
#TESTING SECTION
###########################################################################


def main():
    '''
    TESTING TIME!!!
    
    '''
    print "hello world"
    m0 = BenthicPhotosynthesisMeasurement(0.0, 14.75637037, 404.943)
    m1 = BenthicPhotosynthesisMeasurement(1.0, 25.96292587, 307.6793317)
    m2 = BenthicPhotosynthesisMeasurement(2.0, 57.98165587, 238.6559726)
    m3 = BenthicPhotosynthesisMeasurement(3.0, 47.35232783, 189.673406)
    m4 = BenthicPhotosynthesisMeasurement(4.0, 36.7229998, 154.9128285)
    m5 = BenthicPhotosynthesisMeasurement(5.0, 33.63753108, 130.2449143)
    m6 = BenthicPhotosynthesisMeasurement(6.0, 26.8494999, 112.7392791)
    m7 = BenthicPhotosynthesisMeasurement(7.0, 20.06146872, 100.3163696)
    m8 = BenthicPhotosynthesisMeasurement(8.0, 16.976, 91.50042668)
    m9 = BenthicPhotosynthesisMeasurement(9.0, 15.45920354, 85.24417497)
    m10 = BenthicPhotosynthesisMeasurement(10.0, 11.7585159, 80.80441327)
    m11 = BenthicPhotosynthesisMeasurement(11.0, 7.148489714, 77.6537274)
    m12 = BenthicPhotosynthesisMeasurement(12.0, 2.903677594, 75.41783679)
    m13 = BenthicPhotosynthesisMeasurement(13.0, 0.2986321643, 73.83113249)
    
    
    measurement_list = [m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13]
    areas = {0:100, 5:100, 10:100, 13.3:100, 13.4:0.1}
    
    p_m1 = PhytoPlanktonPhotosynthesisMeasurement(1, 5, 4.113867544, 0.05, 0.01) #US sparkling lake
    p_m2 = PhytoPlanktonPhotosynthesisMeasurement(2, 10, 2.636765965,0.0412667109,0)
    p_m3 = PhytoPlanktonPhotosynthesisMeasurement(3, 15, 4.959339837, 0.1646230769,0)
    p_measurement_list= {p_m1, p_m2, p_m3}
    
    pond_shape_instance = BathymetricPondShape(areas)
       
    
    p = Pond("lake_ID", 360, 12.0, 1440.0, 0.3429805354, pond_shape_instance, measurement_list, p_measurement_list)
    
    depth_of_one_percent_light = p.calculate_depth_of_specific_light_percentage(.01)
    
    print "depth of 1% light is ", depth_of_one_percent_light
    proportional_light = p.calculate_light_proportion_at_depth(depth_of_one_percent_light)
    print "%light of depth ", depth_of_one_percent_light, " is ", proportional_light
    

    
    max_depth = p.get_max_depth()
    print "max depth is ", max_depth
    
    current_depth = 0
    depth_interval_meters = 0.5
    while(current_depth < max_depth):
        print "current depth is ", current_depth
        print "benthic pmax at this depth is: ", p.get_benthic_pmax_at_depth(current_depth)     
        print "benthic ik at this depth is: ", p.get_benthic_ik_at_depth(current_depth)   
        current_depth += depth_interval_meters
    
    littoral_area = p.calculate_total_littoral_area()
    print "littoral area is (should be ~40): ", littoral_area
    
    depth=5
    depth_interval = depth
    sediment_area = p.pond_shape_object.get_sediment_surface_area_at_depth(depth, depth_interval)
    
    
    print "sediment area at depth ", depth, " with interval = ", depth_interval, " is ", sediment_area
    
    f_area1 = p.pond_shape_object.get_fractional_sediment_area_at_depth(depth, littoral_area, depth_interval)
    
    print "f_area, same parameters. Should be 25/40 = 0.625: ", f_area1
    
    
    depth=13.4
    depth_interval = 13.4-5
    sediment_area = p.pond_shape_object.get_sediment_surface_area_at_depth(depth, depth_interval)
    
    
    print "sediment area at depth ", depth, " with interval = ", depth_interval, " is ", sediment_area
    f_area2 = p.pond_shape_object.get_fractional_sediment_area_at_depth(depth, littoral_area, depth_interval)
    
    print "f_area, same parameters. Should be 15/40 = 0.375: ", f_area2
    
    print "f_area1+f_area2: ", f_area1+f_area2
    
    
    
    
    
    print "whatever man. I just wanna know what phyto productivity I get when I=100, Pmax = 4, alpha = 0.01, and beta = 0.001. I'm expecting 0.8629511552"
    print "phyto productivity  is ", p.calculate_phytoplankton_primary_productivity(100, 5)
    
    print "phyto pmax at 0 is ", p.get_phyto_pmax_at_depth(0)
    print "phyto pmax at 10 is ", p.get_phyto_pmax_at_depth(10)
    print "phyto pmax at 15 is ", p.get_phyto_pmax_at_depth(15)
    
    print "phyto productivity at 0 is ", p.calculate_phytoplankton_primary_productivity(100, 0)
    print "phyto productivity at 10 is ", p.calculate_phytoplankton_primary_productivity(100, 5)
    print "phyto productivity at 15 is ", p.calculate_phytoplankton_primary_productivity(100, 15)
        
    print "z1% is ", p.calculate_photic_zone_lower_bound()
    print "volume of photic zone is ", p.calculate_total_photic_volume()
    
    print "pppr is", p.calculateDailyWholeLakePhytoplanktonPrimaryProductionPerMeterSquared(0.1)
    
    total_seasonal_benthic_production = p.calculate_total_seasonal_benthic_primary_production()
    print "total seasonal BPP is ", total_seasonal_benthic_production




if __name__ == "__main__":
    main()

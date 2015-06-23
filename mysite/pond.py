# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 09:38:17 2014

@author: cdleong
"""

import math as mat
import numpy as np
from mysite.pond_shape import PondShape
from mysite.benthic_photosynthesis_measurement import BenthicPhotoSynthesisMeasurement
from mysite.bathymetric_pond_shape import BathymetricPondShape
from scipy.interpolate import interp1d
from scipy import interpolate








class Pond(object):

    ###################################
    # CONSTANTS
    ###################################
    MINIMUM_VALID_DAY = 0
    MAXIMUM_VALID_DAY = 366
    
    MINIMUM_LENGTH_OF_DAY = 0.0  # north of the arctic circle and south of the antarctic one, this is possible during winter.
    MAXIMUM_LENGTH_OF_DAY = 24.0003  # north of the arctic circle and south of the antarctic one, this is possible during summer, if there's a leap second
    
    MINIMUM_NOON_SURFACE_LIGHT = 0.0
    MAXIMUM_NOON_SURFACE_LIGHT = 1000000.0  # normally it's in the range of ~1000-2000. A 1000x increase, I'm pretty sure, would sterilize the lake
    
    
    MINIMUM_LIGHT_ATTENUATION_COEFFICIENT = 0.0
    MAXIMUM_LIGHT_ATTENUATION_COEFFICIENT = float("inf")  # no upper limit
    
    PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND = 0.01 #1% 
    


    
    ###################################
    # VARIABLES
    ###################################    
    
    # identifying variables, aka Primary Key
    lake_ID = -1  # invalid lake ID I'm assuming    
    day_of_year = 0  # day of year 0-366    
 
 
    # General pond information. Light/photosynthesis
    length_of_day = 15  # hours of sunlight
    noon_surface_light = 1500  # micromol*m^(-2)*s^(-1 ) (aka microEinsteins?)
    light_attenuation_coefficient = 0.05  # aka "kd"
    
    # shape
    pond_shape_object = PondShape()
    
    # benthic photosynthesis data list
    benthic_photosynthesis_measurements = []
    
    # phytoplankton photosynthesis data list #TODO: everything to do with this
    phytoplankton_photosynthesis_measurements = []
    
    # default intervals for calculatations 
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
        self.set_time_interval(time_interval)

    def get_time_interval(self):
        return self.__time_interval


    def set_time_interval(self, value):
        self.__time_interval = value


    def del_time_interval(self):
        del self.__time_interval








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
        @return: The surface light intensite at solar noon, in micromoles per square meter per second(μmol*m^-2*s^-1)
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
        @rtype: list containing BenthicPhotoSynthesisMeasurement objects
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
        return self.get_pond_shape().get_max_depth()
    
    #######################
    # SETTERS
    #######################

    def set_lake_id(self, lake_id):
        '''
        Setter method
        '''
        self.__lake_ID = lake_id


    def set_day_of_year(self, day_of_year):
        '''
        Setter method
        Validates the value        
        '''        
        validated_day_of_year = self.validate_day_of_year(day_of_year)
        self.__day_of_year = validated_day_of_year


    def set_length_of_day(self, length_of_day):
        '''
        Setter method
        Validates the length_of_day        
        '''     
        validated_length_of_day = self.validate_length_of_day(length_of_day)
        self.__length_of_day = validated_length_of_day


    def set_noon_surface_light(self, noon_surface_light):
        '''
        Setter method
        Validates the value        
        '''   
        validated_light = self.validate_noon_surface_light(noon_surface_light)
        self.__noon_surface_light = validated_light


    def set_light_attenuation_coefficient(self, light_attenuation_coefficient):
        '''
        Setter method
        Validates the value        
        '''           
        validated_light_attenuation_coefficient = self.validate_light_attenuation_coefficient(light_attenuation_coefficient)
        self.__light_attenuation_coefficient = validated_light_attenuation_coefficient

        
    def set_pond_shape(self, pond_shape_object):
        '''
        Setter method
        Validates the value        
        '''           
        if(isinstance(pond_shape_object, PondShape)):
            print "setting pond shape."
            self.pond_shape_object = pond_shape_object
        else:
            raise Exception("cannot set pond shape. Invalid type")
        

    def set_benthic_photosynthesis_measurements(self, values=[]):
        '''
        Setter method
        Validates the value        
        '''           
        all_valid = self.validate_types_of_all_items_in_list(values, BenthicPhotoSynthesisMeasurement)
        if(all_valid):
            self.__benthic_photosynthesis_measurements = values
        else:
            raise Exception("ERROR: all values in benthic_photosynthesis_measurements must be of type BenthicPhotoSynthesisMeasurement")


    def set_phytoplankton_photosynthesis_measurements(self, value):
        # TODO: Type-checking
        self.__phytoplankton_photosynthesis_measurements = value
        






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







    lake_ID = property(get_lake_id, set_lake_id, del_lake_id, "lake_ID's docstring")
    day_of_year = property(get_day_of_year, set_day_of_year, del_day_of_year, "day_of_year's docstring")
    length_of_day = property(get_length_of_day, set_length_of_day, del_length_of_day, "length_of_day's docstring")
    noon_surface_light = property(get_noon_surface_light, set_noon_surface_light, del_noon_surface_light, "noon_surface_light's docstring")
    light_attenuation_coefficient = property(get_light_attenuation_coefficient, set_light_attenuation_coefficient, del_light_attenuation_coefficient, "light_attenuation_coefficient's docstring")
    benthic_photosynthesis_measurements = property(get_benthic_photosynthesis_measurements, set_benthic_photosynthesis_measurements, del_benthic_photosynthesis_measurements, "benthic_photosynthesis_measurements's docstring")
    phytoplankton_photosynthesis_measurements = property(get_phytoplankton_photosynthesis_measurements, set_phytoplankton_photosynthesis_measurements, del_phytoplankton_photosynthesis_measurements, "phytoplankton_photosynthesis_measurements's docstring")

                     
       



    ########################################
    # Appenders/mutators
    ########################################
    def add_benthic_measurement(self, measurement=BenthicPhotoSynthesisMeasurement):
        if(isinstance(measurement, BenthicPhotoSynthesisMeasurement)):
            self.benthic_photosynthesis_measurements.append(measurement)
        else:
            raise Exception("ERROR: cannot add measurement to benthic measurements list - measurement must be of type BenthicPhotoSynthesisMeasurement")

    def add_benthic_measurement_if_photic(self, measurement):
        z1Percent = self.calculate_depth_of_specific_light_percentage(self.PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND)
        if(measurement.get_depth()<z1Percent):
            self.add_benthic_measurement(measurement)
        else: 
            print "measurement not within photic zone"

        
        
    def remove_benthic_measurement(self, measurement=BenthicPhotoSynthesisMeasurement):
        self.benthic_photosynthesis_measurements.remove(measurement)
        
    def update_shape(self, other_pond_shape):
        our_shape = self.get_pond_shape()
        if(isinstance(other_pond_shape, BathymetricPondShape)):
            our_shape.update_shape(other_pond_shape)
            self.pond_shape_object = our_shape


    ########################################
    # SCIENCE FUNCTIONS
    ########################################
    def check_if_depth_in_photic_zone(self, depth):
        in_zone = True
        photic_zone_lower_bound = self.calculate_photic_zone_lower_bound() 
        if(depth<0 or depth>photic_zone_lower_bound):
            in_zone = False
        else: 
            in_zone = True
        return in_zone
        
    def calculate_photic_zone_lower_bound(self):
        lower_bound = self.calculate_depth_of_specific_light_percentage(self.PHOTIC_ZONE_LIGHT_PENETRATION_LEVEL_LOWER_BOUND)
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
        depthOfSpecifiedLightProportion = 0.0  # the surface of the pond makes a good default
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
    
    def calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(self):        
        '''
        Everything else in this entire project works to make this method work.
        @return: Benthic Primary Production, mg C per meter squared, per day.
        @rtype: float 
        '''
        time_interval = self.get_time_interval()
        noonlight = self.get_noon_surface_light()
        lod = self.get_length_of_day()
        kd = self.get_light_attenuation_coefficient()
        total_littoral_area = self.calculate_total_littoral_area()
 
 
        
        depth_interval =0.1 #TODO: undo this
        benthic_primary_production_answer = 0.0  # mg C per day
        current_depth = 0.0
        max_depth = self.get_max_depth()
        shape_object = self.get_pond_shape()        
        # for each current_depth interval
        for depth, area in shape_object.water_surface_areas.items():
            current_depth = depth
            bpprz = 0.0  # mg C* m^-2 *day
 
            # for every time interval
            
            ik_z = self.get_benthic_ik_at_depth(current_depth)
            benthic_pmax_z = self.get_benthic_pmax_at_depth(current_depth)  # units?
            area_z = area
            f_area = area_z/total_littoral_area
                
            t = 0.0  # start of day
            while t < lod:
 
                light_zt = noonlight * np.sin(np.pi * t / lod)  # light at current_depth current_depth, time t
                izt = light_zt * np.exp(-kd * current_depth)
                bpprzt = benthic_pmax_z * np.tanh(izt / ik_z)
                bpprz += bpprzt
 
                t += time_interval
            bpprz = bpprz / (1 / time_interval)  # account for the fractional time interval. e.g. dividing by 1/0.25 is equiv to dividing by 4
            interval_bppr_fraction = bpprz * f_area  # normalizing


 
            benthic_primary_production_answer += interval_bppr_fraction
            current_depth += depth_interval 
 
 
        return benthic_primary_production_answer
    


#     #####################################################################
#     #calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared
#     #April 1 2015
#     #Function
#     #basically equation 12, TBP
#     #but works with pprinputs and datareader
#     #and sets layer bppr_z values
#     ######################################################################
#     #TODO: delete this
#     def oldcalculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(self,
#                                                    time_interval=0.25   #15 minutes, or a quarter-hour
#                                                    ):
#  
#  
#         noonlight = self.getNoonSurfaceLight()
#         lod = self.getLengthOfDay()
#         kd =self.getLightAttenuationCoefficient() #unitless coefficient
#         total_littoral_area = self.calculate_total_littoral_area()
#  
#  
#         #for each layer
#         benthic_primary_production_answer =0.0 #mg C per day
#         for layer in self.pondLayerList:
#             bpprz = 0.0 #mg C* m^-2 *day
#  
#             #for every time interval
#             current_depth = layer.get_depth() #meters
#             ik_z = layer.get_ik()
#             benthic_pmax_z = layer.get_pmax() #units?
#             f_area = layer.get_area()/total_littoral_area #fractional area of normalized 1m lake
#             t = 0.0 #start of day
#             while t < lod:
#  
#                 light_zt = noonlight*np.sin(np.pi*t/lod) #light at current_depth current_depth, time t
#                 izt = light_zt* np.exp(-kd*current_depth)
#                 bpprzt = benthic_pmax_z* np.tanh(izt/ik_z)
#                 bpprz +=bpprzt
#  
#                 t += time_interval
#             bpprz = bpprz / (1/time_interval) #account for the fractional time interval. e.g. dividing by 1/0.25 is equiv to dividing by 4
#             interval_bppr_fraction = bpprz*f_area
#             layer.set_bpprz(interval_bppr_fraction)
#  
#             benthic_primary_production_answer+=interval_bppr_fraction
#  
#  
#  
#         return benthic_primary_production_answer
    
    def calculate_total_littoral_area(self):
        '''
        @return:
        @rtype:  
        '''
        z1percent = self.calculate_depth_of_specific_light_percentage(0.01)
        shape_of_pond = self.get_pond_shape()
        areas_dict = shape_of_pond.water_surface_areas
        littoral_area=0.0
        for key, elem in areas_dict.items():
            if (key <z1percent):
                littoral_area+=elem
            
#         littoral_area = self.get_pond_shape().get_sediment_area_above_depth(z1percent) #TODO: check? 
        return littoral_area    
    
    def get_benthic_pmax_at_depth(self, depth=0.0):
        '''
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
    
        
        
        

    def interpolate_values_at_depth(self, depth, depths_list=[], values_list=[]):
        '''
        INTERPOLATE VALUES AT DEPTH
        Essentially, given an array of "x" (validated_depth) and "y" values, interpolates "y" value at specified validated_depth.
        
        
        
        '''
        # Uses http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html   
        validated_depth = self.validate_depth(depth)
        
        max_depth_given = max(depths_list)
        min_depth_given = min(depths_list)
        
        if(validated_depth>max_depth_given):            
            print "depth is",validated_depth, "cannot interpolate outside the range of measurements given. setting to max."
            validated_depth= max_depth_given
        elif(min_depth_given<min_depth_given):
            print "depth is",validated_depth, "cannot interpolate outside the range of measurements given. setting to min.."
            validated_depth= min_depth_given            
            
        
        # get interpolation function
        x = depths_list
        y = values_list 
        f = interp1d(x, y)
        
        #magic from # Uses http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        #SPLINES....!!!
        tck = interpolate.splrep(x, y, s=0)
        xnew = [validated_depth]
        spline_interpolated = interpolate.splev(xnew, tck, der=0) #0th derivative
        linear_interpolated = f(validated_depth)         
        
        
        

#         value_at_depth = spline_interpolated[0] #TODO: inefficient to get the whole array and return just one.
        value_at_depth = linear_interpolated
        
        return value_at_depth        
    
    
    
    time_interval = property(get_time_interval, set_time_interval, del_time_interval, "time_interval's docstring")
     

# 
# 
# 
# 
# 
#     ###############
#     #DOES
#     ###############
#     def stringTest(self):
#         return "pond test"
# 
# 
#     #default values all negative in the hope it'll break when not set properly
#     def __init__(self,
#                  lakeID =-1,
#                  dayOfYear = -1,
#                  meanDepth=-2.0,
#                  maxDepth=-6.666,
#                  shapeFactor = -1,
#                  dayLength = -12.0,
#                  light_attenuation_coefficient = -0.2, #aka kd
#                  noonLight=-1500.0,
#                  benthic_pmax=-5.0,
#                  pondLayerList = []):
#         self.setLakeID(lakeID)
#         self.setDayOfYear(dayOfYear)
#         self.length_of_day = dayLength
#         self.light_attenuation_coefficient = light_attenuation_coefficient
#         self.benthic_pmax = benthic_pmax #max benthic production
#         self.pondLayerList = pondLayerList
# 
# 
# 
# 
# 
# 
# 
#     ######################
#     #getters/setters, etc.
#     ######################
#     def getLakeID(self):
#         return self.lake_ID
# 
# 
#     def setLakeID(self, value):
#         self.lake_ID = value
# 
#     def getDayOfYear(self):
#         return self.day_of_year
# 
#     def setDayOfYear(self, dayOfYear):
#         if (dayOfYear<366 and dayOfYear>=0):#simple check
#             self.day_of_year=dayOfYear
# 
#     def calculate_total_littoral_area(self):
#         z1percent = self.getDepthOf1PercentLight()
#         littoral_area = 0
#         for layer in self.pondLayerList:
#             if layer.get_depth()<z1percent: #less than equals shallower than
#                 littoral_area+=layer.get_area()
#         return littoral_area
# 
# 
# 
# 
# 
# 
#     def getLengthOfDay(self):
#         return self.length_of_day
# 
#     def setLengthOfDay(self, length_of_day=12.0):
#         self.length_of_day = length_of_day
# 
#     def getLightAttenuationCoefficient(self):
#         '''AKA kd'''
#         return self.light_attenuation_coefficient
# 
#     def setLightAttenuationCoefficient(self, light_attenuation_coefficient):
#         self.light_attenuation_coefficient=light_attenuation_coefficient
# 
# 
# 
#     def getNoonSurfaceLight(self):
#         return self.noon_surface_light
# 
#     def setNoonSurfaceLight(self, noonSurfaceLight):
#         self.noon_surface_light = noonSurfaceLight
# 
# 
# 
#     def getBPMax(self):
#         return self.benthic_pmax
# 
#     def setBPMax(self, bpMax):
#         self.benthic_pmax = bpMax
# 
#     def getPondLayer(self, index):
#         return self.pondLayerList[index]
# 
#     def popPondLayer(self, index):
#         return self.pondLayerList.pop(index)
# 
#     def appendPondLayer(self, layer):
#         self.pondLayerList.append(layer)
# 
#     def appendPondLayerIfPhotic(self, layer):
#         z1percent = self.calculate_depth_of_specific_light_percentage(0.01) #1%
#         if (layer.get_depth()<z1percent): #0 is surface, larger is deeper, smaller is shallower. We want depths shallower than z1percent
# 
#             self.pondLayerList.append(layer)
# 
# 
# 
#     def getPondLayerList(self):
#         return self.pondLayerList
# 
#     def setPondLayerList(self, pondLayerlist):
#         self.pondLayerList = pondLayerlist
# 
#     def getDepthOf1PercentLight(self):
#         #depth of 1% light is 4.6/kd
#         return 4.6/self.light_attenuation_coefficient
# 
# 
# 
# 
#     #####################################################################
#     #calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared
#     #April 1 2015
#     #Function
#     #basically equation 12, TBP
#     #but works with pprinputs and datareader
#     #and sets layer bppr_z values
#     ######################################################################
#     def calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(self,
#                                                    time_interval=0.25   #15 minutes, or a quarter-hour
#                                                    ):
# 
# 
#         noonlight = self.getNoonSurfaceLight()
#         lod = self.getLengthOfDay()
#         kd =self.getLightAttenuationCoefficient() #unitless coefficient
#         total_littoral_area = self.calculate_total_littoral_area()
# 
# 
#         #for each layer
#         bppr =0.0 #mg C per day
#         for layer in self.pondLayerList:
#             bpprz = 0.0 #mg C* m^-2 *day
# 
#             #for every time interval
#             z = layer.get_depth() #meters
#             ik_z = layer.get_ik()
#             benthic_pmax_z = layer.get_pmax() #units?
#             f_area = layer.get_area()/total_littoral_area #fractional area of normalized 1m lake
#             t = 0.0 #start of day
#             while t < lod:
# 
#                 light_zt = noonlight*np.sin(np.pi*t/lod) #light at depth z, time t
#                 izt = light_zt* np.exp(-kd*z)
#                 bpprzt = benthic_pmax_z* np.tanh(izt/ik_z)
#                 bpprz +=bpprzt
# 
#                 t += time_interval
#             bpprz = bpprz / (1/time_interval) #account for the fractional time interval. e.g. dividing by 1/0.25 is equiv to dividing by 4
#             layer_bpprz = bpprz*f_area
#             layer.set_bpprz(layer_bpprz)
# 
#             bppr+=layer_bpprz
# 
# 
# 
#         return bppr
# 
# 
#     ########################################
#     #calculateDailyWholeLakePelagicPrimaryProduction
#     #April 9 2015
#     #basically equation 10, but not
#     #and works with pprinputs and datareader
#     #and sets layer pppr_z values
#     ########################################
#     def calculateDailyWholeLakePelagicPrimaryProduction(self,
#                                                         time_interval =0.25#15 minutes, or a quarter-hour
#                                                         ):
# 
# 
#         z1percent = self.calculate_depth_of_specific_light_percentage(0.01)#1%
#         noonlight = self.getNoonSurfaceLight()
#         lod = self.getLengthOfDay()
#         kd =self.getLightAttenuationCoefficient() #unitless coefficient
# 
#         layer = PhotoSynthesisMeasurement
# 
#         #make sure the pond layer list is sorted
#         #http://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
#         sortedLayerList = sorted(self.pondLayerList, key = lambda x: x.depth, reverse = False)
# 
# 
#         pppr =0
#         total_volume = self.calculateLakeVolumeAboveDepthZ(sortedLayerList[-1].get_depth())
#         previous_layer_volume_above_z = 0.0
#         for layer in sortedLayerList:
#             #no need to filter for layers above z1percent, ideally.
#             #we only add layers to the pond if they're above z1percent
#             #still, might as well be careful
#             if layer.get_depth()>z1percent:
#                 print "ERROR: layers are below depth of 1 percent light"
#                 return -2
# 
# 
# 
# 
#             #equation 9 basically
#             t = 0.0 #start of day
#             z = layer.get_depth()
#             ik_z = layer.get_ik()
#             pelagic_pmax = self.calculatePelagicProductivityMax() #mg C per m^3 per hour
# 
#             #TODO: have this pre-calculated for each layer?
#             volumeAboveLayer = self.calculateLakeVolumeAboveDepthZ(z)
#             volumeOfLayer = volumeAboveLayer-previous_layer_volume_above_z
#             previous_layer_volume_above_z=volumeAboveLayer #update
#             f_volume = volumeOfLayer/total_volume #unitless fraction
# 
#             pppr_z = 0.0
# 
#             while t < lod:
# 
#                 light_zt = noonlight*np.sin(np.pi*t/lod) #light at depth z, time t
#                 izt = light_zt* np.exp(-kd*z)
# 
#                 pppr_zt = pelagic_pmax* np.tanh(izt/ik_z)*volumeOfLayer #(mg C *m^-3*h^-1) *m^-3, so m^3 cancels
#                 pppr_z+=pppr_zt #mg C *h^-1 at z
#                 t += time_interval
#             pppr_z = pppr_z/ (1/time_interval) #account for time interval
#             layer_ppr_z = pppr_z
# #             f_layer_ppr_z = pppr_z*f_volume #this would be mg C *h^-1, but as a fractional part of something
#             layer.set_ppprz(layer_ppr_z) #mg C *h^-1
# 
#             pppr+=layer_ppr_z
# 
# 
# 
# 
#         return pppr #whole lake, all day, all depths, pelagic primary productivity. So mgC*day
# 
# 
#     #######################################################################################
#     #calculateDailyWholeLakePelagicPrimaryProductionPerSquareMeter
#     #Stub. TODO: IMPLEMENT THIS
#     #basically uses volume instead of area. 
#     #######################################################################################
#     def calculateDailyWholeLakePelagicPrimaryProductionPerSquareMeter(self,
#                                                                time_interval=0.25
#                                                                ):
#         A0 = self.getSufaceAreaAtDepthZero()
#         z1percent = self.calculate_depth_of_specific_light_percentage(0.01)#1%
# 
#         if (A0<0 or z1percent<0):
#             #crash somehow I guess
#             print "ERROR: values improperly set"
#             return -1
#         total_pppr= self.calculateDailyWholeLakePelagicPrimaryProduction(time_interval)
#         ppprPerMeter = total_pppr/A0
#         return ppprPerMeter
# 
# 
#     ##########################################################################################
#     # CalculateDepthOfSpecificLightProportion
#     #
#     # Calculates the depth of, say, 1% light.
#     # Uses: light attenuation coefficient kd. 
#     # 
#     ##########################################################################################
#     def calculate_depth_of_specific_light_percentage(self, 
#                                                 validated_desired_light_proportion=1.0):
#         '''
#         Given a proportion, say 0.01 for 1%, 
#         calculates the depth of the pond at which that much light will reach.
#         Equation on which this is based: Iz/I0=e^-kd*z
#         Given a desired proportion for Iz/I0, and solved for z, 
#         this simplifies to z= kd/ln(desired proportion) 
#         
#         @param validated_desired_light_proportion:a float value from 0 to 1.0 
#         @return: the depth, in meters, where that proportion of light penetrates.
#         
#         '''
#         
#         depthOfSpecifiedLightProportion = 0.0 # the surface of the pond
#         backgroundLightAttenuation = self.getLightAttenuationCoefficient()
#         
#         if(validated_desired_light_proportion>1.0): #greater than 100%? Just set to 100%. Not strictly necessary, since the default value would be the correct answer.
#             validated_desired_light_proportion = 1.0
#         if(validated_desired_light_proportion<0.0): #less than 0%? Just set to 0%
#             validated_desired_light_proportion = 0.0
# 
#         if(validated_desired_light_proportion<1.0 and validated_desired_light_proportion>0.0):         
#             naturalLogOfProportion = mat.log(validated_desired_light_proportion)
# #             print "natural log = " + str(naturalLogOfProportion)
#             
#             depthOfSpecifiedLightProportion = naturalLogOfProportion / -backgroundLightAttenuation #TODO: check if zero.
#         
#         
#             
#             
#         return depthOfSpecifiedLightProportion
# 
# 
# 
# 
# 
# 
# 
#     ####################################
#     # Science functions.
#     # Source: Vadeboncoeur et al, 2008
#     ####################################
# 
# 
#     def surfaceAreaAtDepthZ(self, z=0.0):
#         """
#         #1 Lake area at depth z. Calculated from area at depth zero (the surface)
#         """
#         if(z>self.getMaxDepth()): #deeper than max
#             z=self.getMaxDepth() #set to max
#         return self.surfaceAreaAtDepthZero*pow((1-(float(z)/self.maxDepth)),self.calculateShapeFactorFromDepthRatio())
# 
# 
#     def calculateLakeVolumeAboveDepthZ(self, z):
#         """
#         #2 Lake volume above depth z.
#         # uses shape factor (gamma)
#         """
#         volume=-1.0 #if it returns this something is wrong
#         gamma = self.getShapeFactor()
#         if(self.shapeFactor<0): #not set
#             gamma = self.calculateShapeFactorFromDepthRatio()
#             print "gamma not set."
#         else:
#             volume = (gamma*z)/(gamma+1)
# 
#         return volume
# 
#     #TODO: remove, not needed. User gives kd directly. 
#     def phytoplanktonChl(self):
#         """
#         # Equation 3:  phytoplankton chlorophyll Chl
#         # Calculated using magic numbers from total phosphorus
#         # source of magic: Prairie et al. (1989)\
#         """
#         return self.calculatePhytoplanktoChlorophyllFromTotalPhosphorus()
# 
#     ####################
#     #AKA PPmax
#     #TODO: Remove. User will give this directly.
#     ###################
#     def calculatePelagicProductivityMax(self):
#         """
#         # Equation 4: phytoplankton productivity, PP (mg C*m^-3*h^-1)
#         # source of magic: Guildford, et al (1994)
#         # AKA ppMax
#         """
#         return 2.2*self.calculatePhytoplanktoChlorophyllFromTotalPhosphorus() #magic
# 
# 
# 
# 
# 
#     def calculateLightAttenuationCoefficient(self):
#         """
#         # Equation 6 light-attenuation coefficient (m^-1) "kd"
#         #calculated from #3,
#         #or, in real life, just measured.
#         #source: Light attenuation and photosynthesis of aquatic plant communities
#         # Krause-Jensen and Sand-Jensen, 1998
#         """
#         return self.getLightAttenuationCoefficient()+0.015*self.calculatePhytoplanktoChlorophyllFromTotalPhosphorus()
# 
#     def lightAtDepthZAndTimeT(self, depths=None, t=6.0): #if day length 12, 6 is noon.
#         """
#         #7 light at depth z, time t (umoles*m^-2*s^-1)
#         #calculated from light attenuation factor, surface light at time 0, depth.
#         """
#         if depths is None:
#             depths = []
#             depths.append(0.0)
#         if isinstance(depths, (int,long,float)):
#             #print depths
#             depths = [depths]
#             #print depths
# 
#         lightValues = []
#         lightAttenuationCoefficient = self.calculateLightAttenuationCoefficient()
#         surfaceLight = self.surfaceLightAtTimeT(t)
#         for depth in depths:
# #            z = abs(z)
#             lightAttentuationFactor = np.exp(-lightAttenuationCoefficient*depth)
#             light = surfaceLight*lightAttentuationFactor
#             lightValues.append(light)
# 
#         if (len(lightValues)==1):
#             return lightValues[0]
#         else:
#             return lightValues
# 
#     def surfaceLightAtTimeT(self, t=6.0): #if day length 12, 6 is noon.
#         """
#         #8 surface light at time t (umoles*m^-2*s^-1)
#         #source of equation: McBride (1992)
#         """
#         return self.noonLight*np.sin((np.pi*(t/self.length_of_day)))
# 
# 
#     def dailyPPatDepthZ(self,deltaT=0.25,deltaZ=0.1, saturationLight=180, depths=None):
#         """
#         #9 daily phytoplankton PP at depth Z (mg C)
#         #summed from sunrise to sunset.
#         """
#         if depths is None:
#             depths = []
#             depths.append(0.0)
#         if isinstance(depths, (int,long,float)): #what is this?
#             #print depths
#             depths = [depths]
#             #print depths
# 
#         ppValues = []
# 
#         #todo: more efficient code? double-nested loops are bad.
#         for depth in depths:
#             summation = 0.0
#             ppMax = self.calculatePelagicProductivityMax()
#             volumeAboveZ = self.calculateLakeVolumeAboveDepthZ(depth)
#             deltaVolume = volumeAboveZ-self.calculateLakeVolumeAboveDepthZ(depth-deltaZ)
#             t=0 #sunrise
#             while t<self.getLengthOfDay():
#                 t+=deltaT
#                 lightZT = self.lightAtDepthZAndTimeT(depth,t)
#                 hyperbolicThing = mat.tanh(lightZT/saturationLight)
#                 summation += ppMax*hyperbolicThing*deltaVolume
#             ppValues.append(summation)
# 
#         #I put this in so you could do single values or arrays with one function.
#         if(len(ppValues)==1):
#             return ppValues[0]
#         else:
#             return ppValues
# 
# 
# 
#     def dailyTPP(self, deltaT=0.25, deltaZ=0.1, saturationLight=180):
#         """
#         # Equation 10: daily whole-lake phytoplankton production, TPP (mg C/m^2)
#         #basically #9, summed from depth 0 to of 1% surface light.
#         #then that quantity divided by surface area at zero.
#         """
#         summation = 0.0
#         z=0.0 #lake surface
#         z1percent=4.6/self.calculateLightAttenuationCoefficient()#depth of 1%surfaceLight
#         while(z<z1percent):
#             z+=deltaZ
#             summation +=self.dailyPPatDepthZ(deltaT, deltaZ, saturationLight,z)
#         return summation/self.surfaceAreaAtDepthZero
# 
# 
#     def dailyBPatDepthZ(self,deltaT=0.25, deltaZ=0.1, saturationLight = 300, z=0):
#         """
#         #11 daily benthic (aka periphyton) primary production, BP, at depth z (mg C)
#         """
#         summation = 0.0
#         bpMax = self.getBPMax()
#         areaAtZ = self.surfaceAreaAtDepthZ(z)
#         deltaArea = self.surfaceAreaAtDepthZ(z-deltaZ)-areaAtZ
#         t=0 #sunrise
#         while t<self.getLengthOfDay():
#             t+=deltaT
#             lightZT = self.lightAtDepthZAndTimeT(z,t)
#             hyperbolicThing = mat.tanh(lightZT/saturationLight)
#             summation += bpMax*hyperbolicThing*deltaArea
#         return summation
# 
# 
#     def dailyTotalBenthicProduction(self, deltaT=0.25, deltaZ=0.1, saturationLight = 300):
#         """
#         #12 daily whole-lake periphyton (AKA, Benthic) primary production, TBP (mg C/m2 )
#         """
#         summation = 0.0
#         z=0.0 #lake surface
#         while(z<self.getMaxDepth()):
#             z+=deltaZ
#             summation +=self.dailyBPatDepthZ(deltaT, deltaZ, saturationLight,z)
#             #print "summation is %f" %summation
#         return summation/self.getSufaceAreaAtDepthZero()





def main():
    print "hello world"
    m0 = BenthicPhotoSynthesisMeasurement(0.0, 14.75637037, 404.943)
    m1 = BenthicPhotoSynthesisMeasurement(1.0, 25.96292587, 307.6793317)
    m2 = BenthicPhotoSynthesisMeasurement(2.0, 57.98165587, 238.6559726)
    m3 = BenthicPhotoSynthesisMeasurement(3.0, 47.35232783, 189.673406)
    m4 = BenthicPhotoSynthesisMeasurement(4.0, 36.7229998, 154.9128285)
    m5 = BenthicPhotoSynthesisMeasurement(5.0, 33.63753108, 130.2449143)
    m6 = BenthicPhotoSynthesisMeasurement(6.0, 26.8494999, 112.7392791)
    m7 = BenthicPhotoSynthesisMeasurement(7.0, 20.06146872, 100.3163696)
    m8 = BenthicPhotoSynthesisMeasurement(8.0, 16.976, 91.50042668)
    m9 = BenthicPhotoSynthesisMeasurement(9.0, 15.45920354, 85.24417497)
    m10 = BenthicPhotoSynthesisMeasurement(10.0, 11.7585159, 80.80441327)
    m11 = BenthicPhotoSynthesisMeasurement(11.0, 7.148489714, 77.6537274)
    m12 = BenthicPhotoSynthesisMeasurement(12.0, 2.903677594, 75.41783679)
    m13 = BenthicPhotoSynthesisMeasurement(13.0, 0.2986321643, 73.83113249)
    
    
    measurement_list = [m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13]
    areas = {0:3542.822, 1:3268.758, 2:2465.176, 3:2196.684, 4:1712.987, 5:2417.836, 6:2412.061, 7:2116.739, 8:1895.766, 9:2333.014, 10:2777.449, 11:2475.657, 12:2475.657, 13:2475.657}
    
    pond_shape_instance = BathymetricPondShape(areas)
       
    
    p = Pond("lake_ID", 360, 12.0, 1440.0, 0.3429805354, pond_shape_instance, measurement_list, measurement_list)
    
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
    
    bob = p.calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared()
    print "bob is ", bob
    




if __name__ == "__main__":
    main()

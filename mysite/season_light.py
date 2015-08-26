'''
Created on Aug 21, 2015

@author: cdleong
'''

import numpy as np


class SeasonalLightEstimator(object):
    '''
    classdocs
    '''


    ###################################
    # CONSTANTS
    ###################################
    EARTH_TILT = 23.45 #Earth tilts 23.45 degrees.
    DAYS_PER_YEAR = 365 #if it's 366, just use 365. Close enough. 
    HOURS_IN_A_DAY = 24 #a common approximation for the number of hours in day.
    DEGREES_IN_A_CIRCLE = 360
    NOON_HOUR = 12 #at 12 hours, it is noon.
    SOLAR_CONSTANT = 1367 #watts per meter squared
    MAX_LATITUDE = 90.0 #degrees
    MIN_LATITUDE = 0.0 #degrees
    MAX_SOLAR_DECLINATION_ANGLE = 23.45 #degrees
    MIN_SOLAR_DECLINATION_ANGLE = 0.0 #degrees
    ECCENTRICITY_OF_EARTH_ORBIT = 0.0167    

    
    ###################
    # CLASS VARIABLES
    ###################
    latitude = 0.0 #equator

    
    

    def __init__(self, latitude):
        '''
        Constructor
        '''
        validated_latitude = self.validate_numerical_value(latitude, 90.0, -90.0)
        self.latitude = validated_latitude
        
    def calculateSolarDeclinationAngle(self, day_of_year):    
        '''
        Based on Sudhakar et al 2013, eqn 1
        '''
        
        validated_day_of_year = self.validate_numerical_value(day_of_year, self.DAYS_PER_YEAR, 0)
        
        solar_declination_angle = SeasonalLightEstimator.EARTH_TILT*np.sin((360*(284+validated_day_of_year))/365) #Sudhakar et al 2013, eqn 1
        return solar_declination_angle
    
    def calculateSolarHourAngle(self, local_solar_time):
        '''
        
        based on Sudhakar et al 2013 eqn 2
        From Sudhakar et al 2013 "The solar hour angle for a location on Earth is zero when the sun is directly overhead, negative before noon and positive in the afternoon. The solar hour varies from 1 to 24"
        @param local_solar_time:
        @return: 
        @rtype: 
        '''
        
        validated_local_solar_time = self.validate_numerical_value(local_solar_time, SeasonalLightEstimator.HOURS_IN_A_DAY, 1) #according to (Sudhakar et al 2013), solar hour (LST), ranges from "1 to 24"
        degrees_per_hour = SeasonalLightEstimator.DEGREES_IN_A_CIRCLE/SeasonalLightEstimator.HOURS_IN_A_DAY #should equal 15
        noon_hour = SeasonalLightEstimator.NOON_HOUR
        solar_hour_angle = degrees_per_hour*(validated_local_solar_time-12)
        return solar_hour_angle
        
        
        
        
        
        
    def calculateSunriseHourAngle(self, solar_declination_angle):
        '''
        
        based on Sudhakar et al 2013 eqn 3
        From Sudhakar et al 2013: "The sunrise hour angle for a location is a function of solar declination angle and the latitude."        
        '''
        
        validated_solar_declination_angle = self.validate_numerical_value(solar_declination_angle, SeasonalLightEstimator.MAX_SOLAR_DECLINATION_ANGLE, SeasonalLightEstimator.MIN_SOLAR_DECLINATION_ANGLE)
        
        
        
        
        sunrise_hour_angle = np.arccos(-np.tan(validated_solar_declination_angle)*np.tan(self.latitude))
        return sunrise_hour_angle
        
        
    def calculateTotalDailyAverageExtraterrestrialRadiation(self, day_of_year, solar_declination_angle, latitude, solar_hour_angle):
        '''
        
        based on Sudhakar et al 2013 eqn 4
        From Sudhakar et al 2013: "The total daily average extraterrestrial radiation incident on Earth varies seasonally due to the atmospheric transmissivity associated with cloud cover."
        "The value of 0.033412 is determined knowing that the ratio between the perihelion (0.98328989 AU) squared andthe aphelion (1.01671033 AU) squared should be approximately 0.935338."
        Actually, further research shows that 1 AU -  perihelion = 0.0167, and aphelion - 1 AU also equals 0.0167. .
        That is to say, the eccentricity of Earth's orbit is 0.0167       
        In other words, the earth's orbit varies by 0.0167*2 = 0.0334 AU per year. 
        '''        
        validated_day_of_year = self.validate_numerical_value(day_of_year, SeasonalLightEstimator.DAYS_PER_YEAR, 0)
        validated_solar_declination_angle = self.validate_numerical_value(solar_declination_angle, SeasonalLightEstimator.MAX_SOLAR_DECLINATION_ANGLE, SeasonalLightEstimator.MIN_SOLAR_DECLINATION_ANGLE)
        
        earth_orbit_variation_parameter = 2*SeasonalLightEstimator.ECCENTRICITY_OF_EARTH_ORBIT #should equal about 0.033
        
        
        number1 = (SeasonalLightEstimator.HOURS_IN_A_DAY*SeasonalLightEstimator.SOLAR_CONSTANT)/np.pi

        number2 = (1+earth_orbit_variation_parameter*np.cos(SeasonalLightEstimator.DEGREES_IN_A_CIRCLE*validated_day_of_year/SeasonalLightEstimator.DAYS_PER_YEAR))
        
        number3 = np.cos(self.latitude)*np.cos(validated_solar_declination_angle)*np.sin(solar_hour_angle) - solar_hour_angle*np.sin(self.latitude)*np.sin(validated_solar_declination_angle)
        
        radiation = number1*number2*number3
        
        return radiation
        
         
        
    def calculate_day_length(self, day_of_year):
        '''
        Stub method.
        Future work: calculate this accurately
        '''
        day_length = 12 #default.
        return day_length
    
    
    def calculate_noon_light(self, day_of_year):
        '''
        Stub method.
        Future work: calculate this accurately
        '''
        noon_light = 1400 #default value
        return noon_light
    
    def calculate_season_length(self, latitude):
        '''
        Stub method.
        Future work: calculate this accurately
        '''      
        season_length =SeasonalLightEstimator.DEFAULT_THAW_DAY - SeasonalLightEstimator.DEFAULT_FREEZE_DAY
        return season_length  
        
        
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


'''
let us test things
'''
def main():
    print "hello world"
    bob = SeasonalLightEstimator() 
    test_day = 365
    print "declination angle at day of year ", test_day, " is ", bob.calculateSolarDeclinationAngle(test_day)

    
if __name__ == "__main__":
    main()    
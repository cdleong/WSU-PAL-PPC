# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 09:38:17 2014

@author: cdleong
"""

import math as mat
import numpy as np
from mysite import pond_shape
from mysite.photosynthesis_measurement import PhotosynthesisMeasurement
from mysite.pond_shape import PondShape





class Pond(object):





    
    ###################################
    #KNOWS 
    ###################################    
    
    #identifying variables, aka Primary Key
    lake_ID = -1 #invalid lake ID I'm assuming    
    day_of_year = 0 #day of year 0-366    
 
 
    #General pond information. Light/photosynthesis
    length_of_day = 15 #hours of sunlight
    noon_surface_light = 1500 #micromol*m^(-2)*s^(-1 ) (aka microEinsteins?)
    light_attenuation_coefficient = 0.05 #aka "kd"
    
    #shape
    pond_shape=PondShape
    
    #benthic photosynthesis data
    benthic_photosynthesis_measurements =[]
    
    #phytoplankton photosynthesis data
    phytoplankton_photosynthesis_measurements =[]
    
    def __init__(self, 
                 lake_ID, 
                 day_of_year, 
                 length_of_day, 
                 noon_surface_light, 
                 light_attenuation_coefficient, 
                 benthic_photosynthesis_measurements, 
                 phytoplankton_photosynthesis_measurements):
        self.lake_ID = lake_ID
        self.day_of_year = day_of_year
        self.length_of_day = length_of_day
        self.noon_surface_light = noon_surface_light
        self.light_attenuation_coefficient = light_attenuation_coefficient
        self.benthic_photosynthesis_measurements = benthic_photosynthesis_measurements
        self.phytoplankton_photosynthesis_measurements = phytoplankton_photosynthesis_measurements



    #######################
    #GETTERS AND SETTERS
    #######################
    def get_lake_id(self):
        return self.__lake_ID


    def get_day_of_year(self):
        return self.__day_of_year


    def get_length_of_day(self):
        return self.__length_of_day


    def get_noon_surface_light(self):
        return self.__noon_surface_light


    def get_light_attenuation_coefficient(self):
        return self.__light_attenuation_coefficient


    def get_benthic_photosynthesis_measurements(self):
        return self.__benthic_photosynthesis_measurements


    def get_phytoplankton_photosynthesis_measurements(self):
        return self.__phytoplankton_photosynthesis_measurements


    def set_lake_id(self, value):
        self.__lake_ID = value


    def set_day_of_year(self, value):
        self.__day_of_year = value


    def set_length_of_day(self, value):
        self.__length_of_day = value


    def set_noon_surface_light(self, value):
        self.__noon_surface_light = value


    def set_light_attenuation_coefficient(self, value):
        self.__light_attenuation_coefficient = value


    def set_benthic_photosynthesis_measurements(self, value):
        self.__benthic_photosynthesis_measurements = value


    def set_phytoplankton_photosynthesis_measurements(self, value):
        self.__phytoplankton_photosynthesis_measurements = value


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

        
    ##########################################################################################
    # CalculateDepthOfSpecificLightProportion
    #
    # Calculates the depth of, say, 1% light.
    # Uses: light attenuation coefficient kd. 
    # 
    ##########################################################################################
    def calculateDepthOfSpecificLightPercentage(self, 
                                                desiredLightProportion=1.0):
        '''
        Given a proportion, say 0.01 for 1%, 
        calculates the depth of the pond at which that much light will reach.
        Equation on which this is based: Iz/I0=e^-kd*z
        Given a desired proportion for Iz/I0, and solved for z, 
        this simplifies to z= kd/ln(desired proportion) 
         
        @param desiredLightProportion:a float value from 0 to 1.0 
        @return: the depth, in meters, where that proportion of light penetrates.
         
        '''
         
        depthOfSpecifiedLightProportion = 0.0 # the surface of the pond
        backgroundLightAttenuation = self.get_light_attenuation_coefficient()
         
        if(desiredLightProportion>1.0): #greater than 100%? Just set to 100%. Not strictly necessary, since the default value would be the correct answer.
            desiredLightProportion = 1.0
        if(desiredLightProportion<0.0): #less than 0%? Just set to 0%
            desiredLightProportion = 0.0
 
        if(desiredLightProportion<1.0 and desiredLightProportion>0.0):         
            naturalLogOfProportion = mat.log(desiredLightProportion)
#             print "natural log = " + str(naturalLogOfProportion)
             
            depthOfSpecifiedLightProportion = naturalLogOfProportion / -backgroundLightAttenuation #TODO: check if zero.
         
         
             
             
        return depthOfSpecifiedLightProportion        
     

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
#     def calculateTotalLittoralArea(self):
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
#         z1percent = self.calculateDepthOfSpecificLightPercentage(0.01) #1%
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
#         total_littoral_area = self.calculateTotalLittoralArea()
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
#         z1percent = self.calculateDepthOfSpecificLightPercentage(0.01)#1%
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
#         z1percent = self.calculateDepthOfSpecificLightPercentage(0.01)#1%
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
#     def calculateDepthOfSpecificLightPercentage(self, 
#                                                 desiredLightProportion=1.0):
#         '''
#         Given a proportion, say 0.01 for 1%, 
#         calculates the depth of the pond at which that much light will reach.
#         Equation on which this is based: Iz/I0=e^-kd*z
#         Given a desired proportion for Iz/I0, and solved for z, 
#         this simplifies to z= kd/ln(desired proportion) 
#         
#         @param desiredLightProportion:a float value from 0 to 1.0 
#         @return: the depth, in meters, where that proportion of light penetrates.
#         
#         '''
#         
#         depthOfSpecifiedLightProportion = 0.0 # the surface of the pond
#         backgroundLightAttenuation = self.getLightAttenuationCoefficient()
#         
#         if(desiredLightProportion>1.0): #greater than 100%? Just set to 100%. Not strictly necessary, since the default value would be the correct answer.
#             desiredLightProportion = 1.0
#         if(desiredLightProportion<0.0): #less than 0%? Just set to 0%
#             desiredLightProportion = 0.0
# 
#         if(desiredLightProportion<1.0 and desiredLightProportion>0.0):         
#             naturalLogOfProportion = mat.log(desiredLightProportion)
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
    m1 = PhotosynthesisMeasurement(1.0, 14.75637037, 404.943)
    p = Pond("lake_ID", 360, 12.0, 1440.0, 0.3429805354, m1, m1)
    
    print "depth of 1% light is ", p.calculateDepthOfSpecificLightPercentage(.01)





if __name__ == "__main__":
    main()
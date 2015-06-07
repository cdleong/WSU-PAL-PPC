# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 09:38:17 2014

@author: cdleong
"""

import math as mat
import numpy as np
from mysite.pond_layer import Pond_Layer



class Pond:
    """A pond.

    TODO: More docstrings
    """

    ###################################
    #KNOWS (default values arbitrary)
    ###################################
    lakeID = -1 #invalid lake ID I'm assuming
    dayOfYear = 0 #day of year 0-366
#     littoralArea = 0.0
    meanDepth = 1.0 #z mean
    maxDepth = 2.0 #z max
    #depthRatio = 0.5 #DR= meanDepth/maxDepth
    shapeFactor = -1.0 #aka gamma or gam. gamma = DR/(1-DR)
    totalPhos = 3 #TP (total phosphorus, mg/m^3)
    dayLength = 15 #hours of sunlight
    noonSurfaceLight = 1500 #micromol*m^(-2)*s^(-1 ) (aka microEinsteins?)
    backgroundLightAtten = 0.05 #aka "kd"
    surfaceAreaAtDepthZero = 10.0 #(m^2)
    bpMax  = 5 #max benthic production
    pondLayerList = []






    ###############
    #DOES
    ###############
    def stringTest(self):
        return "pond test"


    #default values all negative in the hope it'll break when not set properly
    def __init__(self,
                 lakeID =-1,
                 dayOfYear = -1,
                 meanDepth=-2.0,
                 maxDepth=-6.666,
                 shapeFactor = -1,
                 totalPhos = -4.0,
                 dayLength = -12.0,
                 backgroundLightAtten = -0.2, #aka kd
                 surfaceAreaAtDepthZero = -11.0,
                 noonLight=-1500.0,
                 bpMax=-5.0,
                 pondLayerList = []):
        self.setLakeID(lakeID)
        self.setDayOfYear(dayOfYear)
        self.setMeanDepth(meanDepth)
        self.setMaxDepth(maxDepth)
        self.setShapeFactor(shapeFactor)
        self.totalPhos = totalPhos
        self.dayLength = dayLength
        self.backgroundLightAtten = backgroundLightAtten
        self.surfaceAreaAtDepthZero = surfaceAreaAtDepthZero
        self.bpMax = bpMax #max benthic production
        self.pondLayerList = pondLayerList







    ######################
    #getters/setters, etc.
    ######################
    def getLakeID(self):
        return self.lakeID


    def setLakeID(self, value):
        self.lakeID = value

    def getDayOfYear(self):
        return self.dayOfYear

    def setDayOfYear(self, dayOfYear):
        if (dayOfYear<366 and dayOfYear>=0):#simple check
            self.dayOfYear=dayOfYear

    def calculateTotalLittoralArea(self):
        z1percent = self.getDepthOf1PercentLight()
        littoral_area = 0
        for layer in self.pondLayerList:
            if layer.get_depth()<z1percent: #less than equals shallower than
                littoral_area+=layer.get_area()
        return littoral_area



    def getMeanDepth(self):
        return self.meanDepth

    def setMeanDepth(self, meanDepth=2.0):
        self.meanDepth = meanDepth


    def getMaxDepth(self):
        return self.maxDepth

    def setMaxDepth(self, maxDepth = 6.666):
        if (self.meanDepth>=maxDepth): #prevents divide-by-zero errors in shapeFactor calculations
            self.meanDepth=0.999*maxDepth
        self.maxDepth = maxDepth

    def getShapeFactor(self):
        return self.shapeFactor


    def setShapeFactor(self, value):
        self.shapeFactor = value

    def getDepthRatio(self):
        return float(self.meanDepth)/float(self.maxDepth)

    def calculateShapeFactorFromDepthRatio(self):
        if(self.getDepthRatio()>0):
            return (self.getDepthRatio())/(1.0-self.getDepthRatio())
        else:
            #something is very wrong
            print "ERROR: DEPTH RATIO NOT GREATER THAN ZERO"
            return -1

    def getTotalPhos(self):
        return self.totalPhos

    def setTotalPhos(self, totalPhos = 4.0):
        self.totalPhos=totalPhos

    def getDayLength(self):
        return self.dayLength

    def setDayLength(self, dayLength=12.0):
        self.dayLength = dayLength

    def getBackgroundLightAttenuation(self):
        '''AKA kd'''
        return self.backgroundLightAtten

    def setBackgroundLightAttenuation(self, backgroundLightAtten):
        self.backgroundLightAtten=backgroundLightAtten

    def getSufaceAreaAtDepthZero(self):
        return self.surfaceAreaAtDepthZero

    def getNoonSurfaceLight(self):
        return self.noonSurfaceLight

    def setNoonSurfaceLight(self, noonSurfaceLight):
        self.noonSurfaceLight = noonSurfaceLight

    def setSufaceAreaAtDepthZero(self, surfaceAreaAtDepthZero):
        self.surfaceAreaAtDepthZero=surfaceAreaAtDepthZero


    def calculatePhytoplanktoChlorophyllFromTotalPhosphorus(self):
        return 0.41*pow(self.totalPhos,0.87) #magic

    def getBPMax(self):
        return self.bpMax

    def setBPMax(self, bpMax):
        self.bpMax = bpMax

    def getPondLayer(self, index):
        return self.pondLayerList[index]

    def popPondLayer(self, index):
        return self.pondLayerList.pop(index)

    def appendPondLayer(self, layer):
        self.pondLayerList.append(layer)

    def appendPondLayerIfPhotic(self, layer):
        z1percent = self.getDepthOf1PercentLight()
        if (layer.get_depth()<z1percent): #0 is surface, larger is deeper, smaller is shallower. We want depths shallower than z1percent

            self.pondLayerList.append(layer)



    def getPondLayerList(self):
        return self.pondLayerList

    def setPondLayerList(self, pondLayerlist):
        self.pondLayerList = pondLayerlist

    def getDepthOf1PercentLight(self):
        #depth of 1% light is 4.6/kd
        return 4.6/self.backgroundLightAtten




    #####################################################################
    #calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared
    #April 1 2015
    #Function
    #basically equation 12, TBP
    #but works with pprinputs and datareader
    #and sets layer bppr_z values
    ######################################################################
    def calculateDailyWholeLakeBenthicPrimaryProductionPerMeterSquared(self,
                                                   time_interval=0.25   #15 minutes, or a quarter-hour
                                                   ):


        noonlight = self.getNoonSurfaceLight()
        lod = self.getDayLength()
        kd =self.getBackgroundLightAttenuation() #unitless coefficient
        total_littoral_area = self.calculateTotalLittoralArea()


        #for each layer
        bppr =0.0 #mg C per day
        for layer in self.pondLayerList:
            bpprz = 0.0 #mg C* m^-2 *day

            #for every time interval
            z = layer.get_depth() #meters
            ik_z = layer.get_ik()
            benthic_pmax_z = layer.get_pmax() #units?
            f_area = layer.get_area()/total_littoral_area #fractional area of normalized 1m lake
            t = 0.0 #start of day
            while t < lod:

                light_zt = noonlight*np.sin(np.pi*t/lod) #light at depth z, time t
                izt = light_zt* np.exp(-kd*z)
                bpprzt = benthic_pmax_z* np.tanh(izt/ik_z)
                bpprz +=bpprzt

                t += time_interval
            bpprz = bpprz / (1/time_interval) #account for the fractional time interval. e.g. dividing by 1/0.25 is equiv to dividing by 4
            layer_bpprz = bpprz*f_area
            layer.set_bpprz(layer_bpprz)

            bppr+=layer_bpprz



        return bppr


    ########################################
    #calculateDailyWholeLakePelagicPrimaryProduction
    #April 9 2015
    #basically equation 10, but not
    #and works with pprinputs and datareader
    #and sets layer pppr_z values
    ########################################
    def calculateDailyWholeLakePelagicPrimaryProduction(self,
                                                        time_interval =0.25#15 minutes, or a quarter-hour
                                                        ):


        z1percent = self.getDepthOf1PercentLight()
        noonlight = self.getNoonSurfaceLight()
        lod = self.getDayLength()
        kd =self.getBackgroundLightAttenuation() #unitless coefficient

        layer = Pond_Layer

        #make sure the pond layer list is sorted
        #http://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
        sortedLayerList = sorted(self.pondLayerList, key = lambda x: x.depth, reverse = False)
#         print "sorted layer list is"
#         for layer in sortedLayerList:
#             print "depth: ", layer.depth

        pppr =0
        total_volume = self.calculateLakeVolumeAboveDepthZ(sortedLayerList[-1].get_depth())
        previous_layer_volume_above_z = 0.0
        for layer in sortedLayerList:
            #no need to filter for layers above z1percent, ideally.
            #we only add layers to the pond if they're above z1percent
            #still, might as well be careful
            if layer.get_depth()>z1percent:
                print "ERROR: layers are below depth of 1 percent light"
                return -2




            #equation 9 basically
            t = 0.0 #start of day
            z = layer.get_depth()
            ik_z = layer.get_ik()
            pelagic_pmax = self.calculatePelagicProductivityMax() #mg C per m^3 per hour

            #TODO: have this pre-calculated for each layer?
            volumeAboveLayer = self.calculateLakeVolumeAboveDepthZ(z)
            volumeOfLayer = volumeAboveLayer-previous_layer_volume_above_z
            previous_layer_volume_above_z=volumeAboveLayer #update
            f_volume = volumeOfLayer/total_volume #unitless fraction

            pppr_z = 0.0

            while t < lod:

                light_zt = noonlight*np.sin(np.pi*t/lod) #light at depth z, time t
                izt = light_zt* np.exp(-kd*z)

                pppr_zt = pelagic_pmax* np.tanh(izt/ik_z)*volumeOfLayer #(mg C *m^-3*h^-1) *m^-3, so m^3 cancels
                pppr_z+=pppr_zt #mg C *h^-1 at z
                t += time_interval
            pppr_z = pppr_z/ (1/time_interval) #account for time interval
            layer_ppr_z = pppr_z
#             f_layer_ppr_z = pppr_z*f_volume #this would be mg C *h^-1, but as a fractional part of something
            layer.set_ppprz(layer_ppr_z) #mg C *h^-1

            pppr+=layer_ppr_z




        return pppr #whole lake, all day, all depths, pelagic primary productivity. So mgC*day


    #######################################################################################
    #calculateDailyWholeLakePelagicPrimaryProductionPerSquareMeter
    #Stub. TODO: IMPLEMENT THIS
    #basically uses volume instead of area. 
    #######################################################################################
    def calculateDailyWholeLakePelagicPrimaryProductionPerSquareMeter(self,
                                                               time_interval=0.25
                                                               ):
        A0 = self.getSufaceAreaAtDepthZero()
        z1percent = self.getDepthOf1PercentLight()

        if (A0<0 or z1percent<0):
            #crash somehow I guess
            print "ERROR: values improperly set"
            return -1
        total_pppr= self.calculateDailyWholeLakePelagicPrimaryProduction(time_interval)
        ppprPerMeter = total_pppr/A0
        return ppprPerMeter


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
        backgroundLightAttenuation = self.getBackgroundLightAttenuation()
        
        if(desiredLightProportion>1.0): #greater than 100%? Just set to 100%. Not strictly necessary, since the default value would be the correct answer.
            desiredLightProportion = 1.0
        if(desiredLightProportion<0.0): #less than 0%? Just set to 0%
            desiredLightProportion = 0.0

        if(desiredLightProportion<1.0 and desiredLightProportion>0.0):         
            naturalLogOfProportion = mat.log(desiredLightProportion)
#             print "natural log = " + str(naturalLogOfProportion)
            
            depthOfSpecifiedLightProportion = naturalLogOfProportion / -backgroundLightAttenuation #TODO: check if zero.
        
        
            
            
        return depthOfSpecifiedLightProportion







    ####################################
    # Science functions.
    # Source: Vadeboncoeur et al, 2008
    ####################################


    def surfaceAreaAtDepthZ(self, z=0.0):
        """
        #1 Lake area at depth z. Calculated from area at depth zero (the surface)
        """
        if(z>self.getMaxDepth()): #deeper than max
            z=self.getMaxDepth() #set to max
        return self.surfaceAreaAtDepthZero*pow((1-(float(z)/self.maxDepth)),self.calculateShapeFactorFromDepthRatio())


    def calculateLakeVolumeAboveDepthZ(self, z):
        """
        #2 Lake volume above depth z.
        # uses shape factor (gamma)
        """
        volume=-1.0 #if it returns this something is wrong
        gamma = self.getShapeFactor()
        if(self.shapeFactor<0): #not set
            gamma = self.calculateShapeFactorFromDepthRatio()
            print "gamma not set."

        volume = (gamma*z)/(gamma+1)

        return volume


    def phytoplanktonChl(self):
        """
        # Equation 3:  phytoplankton chlorophyll Chl
        # Calculated using magic numbers from total phosphorus
        # source of magic: Prairie et al. (1989)\
        """
        return self.calculatePhytoplanktoChlorophyllFromTotalPhosphorus()


    #AKA PPmax
    def calculatePelagicProductivityMax(self):
        """
        # Equation 4: phytoplankton productivity, PP (mg C*m^-3*h^-1)
        # source of magic: Guildford, et al (1994)
        # AKA ppMax
        """
        return 2.2*self.calculatePhytoplanktoChlorophyllFromTotalPhosphorus() #magic





    def calculateLightAttenuationCoefficient(self):
        """
        # Equation 6 light-attenuation coefficient (m^-1) "kd"
        #calculated from #3,
        #or, in real life, just measured.
        #source: Light attenuation and photosynthesis of aquatic plant communities
        # Krause-Jensen and Sand-Jensen, 1998
        """
        return self.getBackgroundLightAttenuation()+0.015*self.calculatePhytoplanktoChlorophyllFromTotalPhosphorus()

    def lightAtDepthZAndTimeT(self, depths=None, t=6.0): #if day length 12, 6 is noon.
        """
        #7 light at depth z, time t (umoles*m^-2*s^-1)
        #calculated from light attenuation factor, surface light at time 0, depth.
        """
        if depths is None:
            depths = []
            depths.append(0.0)
        if isinstance(depths, (int,long,float)):
            #print depths
            depths = [depths]
            #print depths

        lightValues = []
        lightAttenuationCoefficient = self.calculateLightAttenuationCoefficient()
        surfaceLight = self.surfaceLightAtTimeT(t)
        for depth in depths:
#            z = abs(z)
            lightAttentuationFactor = np.exp(-lightAttenuationCoefficient*depth)
            light = surfaceLight*lightAttentuationFactor
            lightValues.append(light)

        if (len(lightValues)==1):
            return lightValues[0]
        else:
            return lightValues

    def surfaceLightAtTimeT(self, t=6.0): #if day length 12, 6 is noon.
        """
        #8 surface light at time t (umoles*m^-2*s^-1)
        #source of equation: McBride (1992)
        """
        return self.noonLight*np.sin((np.pi*(t/self.dayLength)))


    def dailyPPatDepthZ(self,deltaT=0.25,deltaZ=0.1, saturationLight=180, depths=None):
        """
        #9 daily phytoplankton PP at depth Z (mg C)
        #summed from sunrise to sunset.
        """
        if depths is None:
            depths = []
            depths.append(0.0)
        if isinstance(depths, (int,long,float)): #what is this?
            #print depths
            depths = [depths]
            #print depths

        ppValues = []

        #todo: more efficient code? double-nested loops are bad.
        for depth in depths:
            summation = 0.0
            ppMax = self.calculatePelagicProductivityMax()
            volumeAboveZ = self.calculateLakeVolumeAboveDepthZ(depth)
            deltaVolume = volumeAboveZ-self.calculateLakeVolumeAboveDepthZ(depth-deltaZ)
            t=0 #sunrise
            while t<self.getDayLength():
                t+=deltaT
                lightZT = self.lightAtDepthZAndTimeT(depth,t)
                hyperbolicThing = mat.tanh(lightZT/saturationLight)
                summation += ppMax*hyperbolicThing*deltaVolume
            ppValues.append(summation)

        #I put this in so you could do single values or arrays with one function.
        if(len(ppValues)==1):
            return ppValues[0]
        else:
            return ppValues



    def dailyTPP(self, deltaT=0.25, deltaZ=0.1, saturationLight=180):
        """
        # Equation 10: daily whole-lake phytoplankton production, TPP (mg C/m^2)
        #basically #9, summed from depth 0 to of 1% surface light.
        #then that quantity divided by surface area at zero.
        """
        summation = 0.0
        z=0.0 #lake surface
        z1percent=4.6/self.calculateLightAttenuationCoefficient()#depth of 1%surfaceLight
        while(z<z1percent):
            z+=deltaZ
            summation +=self.dailyPPatDepthZ(deltaT, deltaZ, saturationLight,z)
        return summation/self.surfaceAreaAtDepthZero


    def dailyBPatDepthZ(self,deltaT=0.25, deltaZ=0.1, saturationLight = 300, z=0):
        """
        #11 daily benthic (aka periphyton) primary production, BP, at depth z (mg C)
        """
        summation = 0.0
        bpMax = self.getBPMax()
        areaAtZ = self.surfaceAreaAtDepthZ(z)
        deltaArea = self.surfaceAreaAtDepthZ(z-deltaZ)-areaAtZ
        t=0 #sunrise
        while t<self.getDayLength():
            t+=deltaT
            lightZT = self.lightAtDepthZAndTimeT(z,t)
            hyperbolicThing = mat.tanh(lightZT/saturationLight)
            summation += bpMax*hyperbolicThing*deltaArea
        return summation


    def dailyTotalBenthicProduction(self, deltaT=0.25, deltaZ=0.1, saturationLight = 300):
        """
        #12 daily whole-lake periphyton (AKA, Benthic) primary production, TBP (mg C/m2 )
        """
        summation = 0.0
        z=0.0 #lake surface
        while(z<self.getMaxDepth()):
            z+=deltaZ
            summation +=self.dailyBPatDepthZ(deltaT, deltaZ, saturationLight,z)
            #print "summation is %f" %summation
        return summation/self.getSufaceAreaAtDepthZero()





def main():
    print "hello world"





if __name__ == "__main__":
    main()
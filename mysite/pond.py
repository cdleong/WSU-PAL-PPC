# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 09:38:17 2014

@author: cdleong
"""

import math as mat
import pylab as pl
import numpy as np
import matplotlib.pyplot as plt



class Pond:
    """A pond.

    TODO: More docstrings
    """

    ###################################
    #KNOWS (default values arbitrary)
    ###################################
    dayOfYear = 0 #day of year 0-366
    littoralArea = 0.0
    meanDepth = 1.0 #z mean
    maxDepth = 2.0 #z max
    #depthRatio = 0.5 #DR= meanDepth/maxDepth
    #shapeFactor = 1.0 #γ = DR/(1-DR)
    totalPhos = 3 #TP (total phosphorus, mg/m^3)
    dayLength = 15 #hours of sunlight
    noonSurfaceLight = 1500 #µmol*m^(-2)*s^(-1 ) (aka microEinsteins?)
    backgroundLightAtten = 0.05 #kd is the other name for this
    surfaceAreaAtDepthZero = 10.0 #(m^2)
    bpMax  = 5 #max benthic production
    pondLayerList = []






    ###############
    #DOES
    ###############
    def stringTest(self):
        return "pond test"


    def __init__(self,
                 meanDepth=2.0,
                 maxDepth=6.666,
                 totalPhos = 4.0,
                 dayLength = 12.0,
                 backgroundLightAtten = 0.2,
                 surfaceAreaAtDepthZero = 11.0,
                 noonLight=1500.0,
                 bpMax=5.0,
                 pondLayerList = []):
        self.setMeanDepth(meanDepth)
        self.setMaxDepth(maxDepth)
        #self.depthRatio = float(meanDepth)/float(maxDepth)
        #self.shapeFactor= float(self.depthRatio)/(1.0-float(self.depthRatio))
        self.totalPhos = totalPhos
        self.dayLength = dayLength
        self.backgroundLightAtten = backgroundLightAtten
        self.surfaceAreaAtDepthZero = surfaceAreaAtDepthZero
        self.bpMax = bpMax #max benthic production
        #print "INITIALIZING!!!!!"

    ######################
    #getters/setters, etc.
    ######################

    def getDayOfYear(self):
        return self.dayOfYear
    
    def setDayOfYear(self, dayOfYear):
        if (dayOfYear<366 and dayOfYear>=0):#simple check
            self.dayOfYear=dayOfYear
            
    def getLittoralArea(self):
        return self.littoralArea
    
    def setLittoralArea(self, littoralArea):
        self.littoralArea = littoralArea
            
    
    def getMeanDepth(self):
        return self.meanDepth

    def setMeanDepth(self, meanDepth=2.0):
        self.meanDepth = meanDepth
        #self.depthRatio = self.meanDepth/self.maxDepth
        
    def getMaxDepth(self):
        return self.maxDepth

    def setMaxDepth(self, maxDepth = 6.666):
        if (self.meanDepth>=maxDepth): #prevents divide-by-zero errors in shapeFactor calculations
            self.meanDepth=0.999*maxDepth
        self.maxDepth = maxDepth

    def getDepthRatio(self):
        return float(self.meanDepth)/float(self.maxDepth)

    def getShapeFactor(self):
        return (self.getDepthRatio())/(1.0-self.getDepthRatio())

    def getTotalPhos(self):
        return self.totalPhos

    def setTotalPhos(self, totalPhos = 4.0):
        self.totalPhos=totalPhos

    def getDayLength(self):
        return self.dayLength

    def setDayLength(self, dayLength=12.0):
        self.dayLength = dayLength

    def getBackgroundLightAttenuation(self):
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


    def getPhytoplanktoChlorophyll(self):
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
        
    def getPondLayerList(self):
        return self.pondLayerList
    
    def setPondLayerList(self, pondLayerlist):
        self.pondLayerList = pondLayerlist
        






    ####################################
    # Science functions.
    # Source: Vadeboncoeur et al, 2008
    ####################################


    def surfaceAreaAtDepthZ(self, z=0.0):
        """
        #1 Lake area at depth z. Calculated from area at depth zero (the surface)
        """        
        if(z>self.getMaxDepth()):
            z=self.getMaxDepth()
        return self.surfaceAreaAtDepthZero*pow((1-(float(z)/self.maxDepth)),self.getShapeFactor())
    
 
    def lakeVolumeAboveDepthZ(self, z):
        """
        #2 Lake volume above depth z.
        # uses shape factor (gamma)
        """
        return (self.getShapeFactor()*z)/(self.getShapeFactor()+1)

    def phytoplanktonChl(self):
        """
        # Equation 3:  phytoplankton chlorophyll Chl
        # Calculated using magic numbers from total phosphorus
        # source of magic: Prairie et al. (1989)\
        """
        return self.getPhytoplanktoChlorophyll()

    def phytoplanktonProductivity(self):
        """
        # Equation 4: phytoplankton productivity, PP (mg C*m^-3*h^-1)
        #source of magic: Guildford, et al (1994)
        """
        return 2.2*self.getPhytoplanktoChlorophyll() #magic

    
    def thermoclineDepth(self):
        """    
        # Equation 5 thermocline depth (m) 
        #calculated from surface area using magic numbers 
        #from paper (Hanna 1990)
        """
        return 6.95*pow(self.surfaceAreaAtDepthZero,0.185) #magic
    

    def calculateLightAttenuationCoefficient(self):
        """
        # Equation 6 light-attenuation coefficient (m^-1) "kd"
        #calculated from #3, 
        #or, in real life, just measured. 
        #source: Light attenuation and photosynthesis of aquatic plant communities 
        # Krause-Jensen and Sand-Jensen, 1998
        """
        return self.getBackgroundLightAttenuation()+0.015*self.getPhytoplanktoChlorophyll()

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
            ppMax = self.phytoplanktonProductivity()
            volumeAboveZ = self.lakeVolumeAboveDepthZ(depth)
            deltaVolume = volumeAboveZ-self.lakeVolumeAboveDepthZ(depth-deltaZ)
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
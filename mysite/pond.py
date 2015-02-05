# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 09:38:17 2014

@author: student
"""

import math as mat
import pylab as pl
import numpy as np
import matplotlib.pyplot as plt



class Pond:
    """A pond.

    TODO: More docstrings"""

    ###################################
    #KNOWS (default values arbitrary)
    ###################################
    meanDepth = 1.0 #z mean
    maxDepth = 2.0 #z max
    #depthRatio = 0.5 #DR= meanDepth/maxDepth
    #shapeFactor = 1.0 #γ = DR/(1-DR)
    totalPhos = 3 #TP (total phosphorus, mg/m^3)
    dayLength = 15 #hours of sunlight
    noonSurfaceLight = 1500 #µmol*m^(-2)*s^(-1 ) (aka microEinsteins?)
    backgroundLightAtten = 0.05
    surfaceAreaAtDepthZero = 10.0 #(m^2)
    noonLight = 1500.0 #surface light at solar noon
    bpMax  = 5






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
                 bpMax=5.0):
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

    def setBackgroundLightAtten(self, backgroundLightAtten):
        self.backgroundLightAtten=backgroundLightAtten

    def getSufaceAreaAtDepthZero(self):
        return self.surfaceAreaAtDepthZero

    def setSufaceAreaAtDepthZero(self, surfaceAreaAtDepthZero):
        self.surfaceAreaAtDepthZero=surfaceAreaAtDepthZero


    def getPhytoplanktoChlorophyll(self):
        return 0.41*pow(self.totalPhos,0.87) #magic

    def getBPMax(self):
        return self.bpMax

    def setBPMax(self, bpMax):
        self.bpMax = bpMax






    ######################
    #Science functions
    ######################

    # 1
    def surfaceAreaAtDepthZ(self, z=0.0):
        if(z>self.getMaxDepth()):
            z=self.getMaxDepth()
        return self.surfaceAreaAtDepthZero*pow((1-(float(z)/self.maxDepth)),self.getShapeFactor())
    # 2
    def lakeVolumeAboveDepthZ(self, z):
        return (self.getShapeFactor()*z)/(self.getShapeFactor()+1)
    #3
    def phytoplanktonChl(self):
        return self.getPhytoplanktoChlorophyll()
    #4
    def phytoplanktonProductivity(self):
        return 2.2*self.getPhytoplanktoChlorophyll() #magic
    #5
    def thermoclineDepth(self):
        return 6.95*pow(self.surfaceAreaAtDepthZero,0.185) #magic
    #6
    def calculateLightAttenuationCoefficient(self):
        return self.getBackgroundLightAttenuation()+0.015*self.getPhytoplanktoChlorophyll()
    #7
    def lightAtDepthZAndTimeT(self, depths=None, t=6.0): #if day length 12, 6 is noon.
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
    #8
    def surfaceLightAtTimeT(self, t=6.0): #if day length 12, 6 is noon.
        return self.noonLight*np.sin((np.pi*(t/self.dayLength)))
    #9
    def dailyPPatDepthZ(self,deltaT=0.25,deltaZ=0.1, saturationLight=180, depths=None):
        if depths is None:           
            depths = []
            depths.append(0.0)
        if isinstance(depths, (int,long,float)):
            #print depths
            depths = [depths]
            #print depths        
        
        ppValues = []
        
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
                
        if(len(ppValues)==1):           
            return ppValues[0]       
        else:
            return ppValues
       


    #10
    def dailyTPP(self, deltaT=0.25, deltaZ=0.1, saturationLight=180):
        summation = 0.0
        z=0.0 #lake surface
        while(z<self.maxDepth):
            z+=deltaZ
            summation +=self.dailyPPatDepthZ(deltaT, deltaZ, saturationLight,z)
        return summation/self.surfaceAreaAtDepthZero


    #11
    def dailyBPatDepthZ(self,deltaT=0.25, deltaZ=0.1, saturationLight = 300, z=0):
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
    #12
    def dailyTBP(self, deltaT=0.25, deltaZ=0.1, saturationLight = 300):
        summation = 0.0
        z=0.0 #lake surface
        while(z<self.getMaxDepth()):
            z+=deltaZ
            summation +=self.dailyBPatDepthZ(deltaT, deltaZ, saturationLight,z)
            #print "summation is %f" %summation
        return summation/self.getSufaceAreaAtDepthZero()



def main(): 

    #figures, subplots, other magic graphing stuff
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111



    #default values
    meanDepth = 20.0 #meters
    maxDepth = 20.0 #meters
    phosphorus = 100.0 #mg/m^3
    
    #try to get user value of phosphorus
    

    exampleSmallPhosVal=3.0    
    exampleLargePhosVal=500.0    
    lightIntensityAtOnsetOfSaturation = 180.0
    
    
    
        
    
    
    pond = Pond(meanDepth,maxDepth)

    print "*****************************************************"
    print pond.getMaxDepth()
    print pond.getMeanDepth()
    print pond.getDepthRatio()
    print "*****************************************************"
    print "*****************************************************"
    print "*****************************************************"
    

    
    #setup y-axis
    depths = np.linspace(0, maxDepth, 500) #500 points spaced from 0.0 to max depth
    y = depths
    print len(y)
    
    #Setup x-axis
    #plot the extreme (example) values
    pond.setTotalPhos(exampleSmallPhosVal)
    x1 =pond.dailyPPatDepthZ(0.25,0.1, lightIntensityAtOnsetOfSaturation, depths) #deltaT, deltaZ, light intensity at onset of saturation, depths
    pond.setTotalPhos(exampleLargePhosVal)
    x2 =pond.dailyPPatDepthZ(0.25,0.1, lightIntensityAtOnsetOfSaturation, depths) #deltaT, deltaZ, light intensity at onset of saturation, depths    
    pond.setTotalPhos(phosphorus)
    x3 =pond.dailyPPatDepthZ(0.25,0.1, lightIntensityAtOnsetOfSaturation, depths) #deltaT, deltaZ, light intensity at onset of saturation, depths    
    
    print len(x1)    
    
    #set labels for graph legend
    #fancy number formatting from http://stackoverflow.com/questions/21226868/superscript-in-python-plots    
    label1 = "%.1f $mg/m^3$" %exampleSmallPhosVal #fancy %f stuff learned from http://stackoverflow.com/questions/6649597/python-decimal-places-putting-floats-into-a-string
    label2 = "%.1f $mg/m^3$" %exampleLargePhosVal 
    label3 = "%.1f $mg/m^3$" %phosphorus
    
      
    #graph lines here   
    ax.plot(x1, y, 'k--', label= label1)
    ax.plot(x2, y, 'k:', label= label2)
    ax.plot(x3, y, 'r-', label= label3)
    
    
    
    
     
    
    
    
    
    
    ax.set_xlabel('Daily Pelagic Primary Productivity (mg C*$m^{-3}*d^{-1}$) for different phosphorus levels')
    ax.set_xlim([1,2000])
    
    plt.grid(True)
    
    plt.ylabel('depth (m)')

    fig.gca().invert_yaxis() #make 0 be at the top, rather than the borrom

    legend = plt.legend(loc='lower right', shadow=True)
    frame  = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
    
    
    ##uncomment this bit for running in a console
    plt.show()
    
    ##uncomment this part for the conversion to flask
    ##Source of sorcery: https://gist.github.com/liuyxpp/1250396
    ##figure to canvas, canvas to buffer, buffer to png, png to response. magic!
    #canvas = FigureCanvas(fig)
    #output = StringIO.StringIO()
    #canvas.print_png(output)
    #response = make_response(output.getvalue())
    #response.mimetype = 'image/png'
    #return response    
          
          
        




if __name__ == "__main__":
    main()
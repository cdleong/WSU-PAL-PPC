'''
Created on Jun 17, 2015

@author: cdleong
'''
from mysite.photosynthesis_measurement import PhotosynthesisMeasurement

class PhytoPlanktonPhotosynthesisMeasurement(PhotosynthesisMeasurement):
    '''
    classdocs
    '''
    ##########
    #CONSTANTS
    ##########
    MAX_VALID_LIMNION = 3
    MIN_VALID_LIMNION = 1
    MAX_VALID_DEPTH = 2000 #lake Baikal, the deepest lake on earth, is only 1642m. Adding a bit on that to be safe. Challenger Deep, the deepest part of the ocean, is about 11000 meters.
    MIN_VALID_DEPTH = 0
    MAX_VALID_PMAX = 5000 #arbitrary value an order of magnitude greater than any I've seen. 
    MIN_VALID_PMAX = 0
    MAX_VALID_ALPHA = 10 #arbitrary. Biggest I've ever seen is less than 1. 
    MIN_VALID_ALPHA = 0.00001 #arbitrary value greater than zero. Smallest I've seen is ~0.05
    MAX_VALID_BETA = 10 #arbitrary. Biggest I've ever seen is less than 1.
    MIN_VALID_BETA = 0.00001 #arbitrary value greater than zero. Smallest I've seen is ~0.01 
    
    ##################
    #VARIABLES
    ##################
    
    thermal_layer = 1 #1 is epilimnion, 2 is metalimnion, 3 is hypolimnion
    phyto_alpha = 0.0 
    phyto_beta = 0.0
    
    


    def __init__(self, thermal_layer, depth, phyto_pmax_biomass, phyto_alpha, phyto_beta):
        super(depth, phyto_pmax_biomass)
        self.set_thermal_layer(thermal_layer)
        self.set_phyto_alpha(phyto_alpha)
        self.set_phyto_beta(phyto_beta)

    def get_thermal_layer(self):
        return self.__thermal_layer


    def get_phyto_alpha(self):
        return self.__phyto_alpha


    def get_phyto_beta(self):
        return self.__phyto_beta


    def set_thermal_layer(self, value):
        self.__thermal_layer = value


    def set_phyto_alpha(self, value):
        self.__phyto_alpha = value


    def set_phyto_beta(self, value):
        self.__phyto_beta = value


    def del_thermal_layer(self):
        del self.__thermal_layer


    def del_phyto_alpha(self):
        del self.__phyto_alpha


    def del_phyto_beta(self):
        del self.__phyto_beta


    def get_depth(self):
        return PhotosynthesisMeasurement.get_depth(self)


    def get_pmax(self):
        return PhotosynthesisMeasurement.get_pmax(self)




    def set_depth(self, value):
        return PhotosynthesisMeasurement.set_depth(self, value)


    def set_pmax(self, value):
        return PhotosynthesisMeasurement.set_pmax(self, value)




    def del_depth(self):
        return PhotosynthesisMeasurement.del_depth(self)


    def del_pmax(self):
        return PhotosynthesisMeasurement.del_pmax(self)
    thermal_layer = property(get_thermal_layer, set_thermal_layer, del_thermal_layer, "thermal_layer's docstring")
    phyto_alpha = property(get_phyto_alpha, set_phyto_alpha, del_phyto_alpha, "phyto_alpha's docstring")
    phyto_beta = property(get_phyto_beta, set_phyto_beta, del_phyto_beta, "phyto_beta's docstring")







def main():
    print "hello world"
    print "let's test if the class works as intended."
    bob = PhytoPlanktonPhotosynthesisMeasurement(1, 5, 4.11, 0.05,0.01)
    
    print "thermal layer is ", bob.get_thermal_layer()
    print "depth is ", bob.get_depth()
    print "pmax is ", bob.get_pmax()
    print "alpha is ", bob.get_phyto_alpha()
    print "beta is ", bob.get_phyto_beta()
    
    print "setting everything to dumb values"
    


if __name__ == "__main__":
    main()        
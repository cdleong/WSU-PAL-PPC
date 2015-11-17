'''
Created on Jun 17, 2015

@author: cdleong
'''
from photosynthesis_measurement import PhotosynthesisMeasurement

class PhytoPlanktonPhotosynthesisMeasurement(PhotosynthesisMeasurement):
    '''
    Holds information and methods relating to P/I curve for pytoplanktonic primary production, for a specific thermal layer.
    '''
    ##########
    #CONSTANTS
    ##########
    MAX_VALID_THERMAL_LAYER = 3 #assumption: no more than three thermal layers
    MIN_VALID_THERMAL_LAYER = 1
    MAX_VALID_DEPTH = 2000 #lake Baikal, the deepest lake on earth, is only 1642m. Adding a bit on that to be safe. Alternately we could go with Challenger Deep, the deepest part of the ocean, which is about 11000 meters.
    MIN_VALID_DEPTH = 0 #If you want to 
    MAX_VALID_PMAX = 5000 #arbitrary value an order of magnitude greater than any I've seen.
    MIN_VALID_PMAX = 0
    MAX_VALID_ALPHA = 100 #arbitrary. Biggest I've ever seen is less than 1.
    MIN_VALID_ALPHA = 0.00001 #arbitrary value greater than zero. Smallest I've seen is ~0.05
    MAX_VALID_BETA = 100 #arbitrary. Biggest I've ever seen is less than 1.
    MIN_VALID_BETA = 0.0 #if zero, we use the non-photoinhibition equation

    ##################
    #VARIABLES
    ##################

    thermal_layer = 1 #1 is epilimnion, 2 is metalimnion, 3 is hypolimnion
    phyto_alpha = 0.0
    phyto_beta = 0.0




    def __init__(self, thermal_layer=0, depth=0.0, phyto_pmax_biomass=0.0, phyto_alpha=0.0, phyto_beta=0.0):
        super(PhytoPlanktonPhotosynthesisMeasurement, self).__init__(depth, phyto_pmax_biomass)
        self.set_thermal_layer(thermal_layer)
        self.set_phyto_alpha(phyto_alpha)
        self.set_phyto_beta(phyto_beta)



    def get_thermal_layer(self):
        '''
        @return: the thermal layer with which these P/I curve parameters are associated. 1=epilimnion, 2=metalimnion, 3=hypolimnion
        @rtype: int
        '''
        return self.__thermal_layer


    def get_phyto_alpha(self):
        '''
        @return: P/I curve parameter alpha.
        @rtype: double
        '''
        return self.__phyto_alpha


    def get_phyto_beta(self):
        '''
        @return: P/I curve parameter beta.
        @rtype: double
        '''
        return self.__phyto_beta


    def set_thermal_layer(self, value):
        '''
        Sets thermal layer associated with which these P/I curve parameters are associated. If given value outside min/max, sets to closest valid value.
        @param value: thermal layer. Valid values: 1=epilimnion, 2=metalimnion, 3=hypolimnion
        '''
        max_value = PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_THERMAL_LAYER
        min_value = PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_THERMAL_LAYER
        validated_value = self.validate_numerical_value(value, max_value, min_value)
        if(validated_value == value):
            self.__thermal_layer = value
        else:
            raise Exception("PhytoPlanktonPhotosynthesisMeasurement thermal layer cannot be set to value outside of reasonable range: ", value,". Must be within range ",min_value,":",  max_value, "")



    def set_depth(self, value):
        '''
        Sets lower bound of thermal layer with which these P/I curve parameters are associated. If given value outside min/max, sets to closest valid value.
        @param value: the lower bound of the thermal layer, in meters from the surface.
        '''
        max_value = PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_DEPTH
        min_value = PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_DEPTH
        validated_value = self.validate_numerical_value(value, max_value, min_value)
        if(validated_value == value):
            return PhotosynthesisMeasurement.set_depth(self, validated_value)
        else:
            raise Exception("PhytoPlanktonPhotosynthesisMeasurement depth cannot be set to value outside of reasonable range: ", value,". Must be within range ",min_value,":",  max_value, "")



    def set_pmax(self, value):
        '''
        Sets P/I curve parameter pmax. If given value outside min/max, sets to closest valid value.
        @param value: pmax  
        '''
        max_value = PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_PMAX
        min_value = PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_PMAX
        validated_value = self.validate_numerical_value(value, max_value, min_value)
        if(validated_value == value):
            return PhotosynthesisMeasurement.set_pmax(self, validated_value)
        else:
            raise Exception("PhytoPlanktonPhotosynthesisMeasurement pmax cannot be set to value outside of reasonable range: ", value,". Must be within range ",min_value,":",  max_value, "")





    def set_phyto_alpha(self, value):
        '''
        Sets P/I curve parameter alpha. If given value outside min/max, sets to closest valid value.
        @param value: alpha 
        '''
        max_value = PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_ALPHA
        min_value = PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_ALPHA
        validated_value = self.validate_numerical_value(value, max_value, min_value)
        if(validated_value == value):
            self.__phyto_alpha = value
        else:
            raise Exception("PhytoPlanktonPhotosynthesisMeasurement alpha cannot be set to value outside of reasonable range: ", value,". Must be within range ",min_value,":",  max_value, "")




    def set_phyto_beta(self, value):
        '''
        Sets P/I curve parameter alpha. If given value outside min/max, sets to closest valid value.
        @param value: beta 
        '''
        max_value = PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_BETA
        min_value = PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_BETA
        validated_value = self.validate_numerical_value(value, max_value, min_value)
        if(validated_value == value):
            self.__phyto_beta = value
        else:
            raise Exception("PhytoPlanktonPhotosynthesisMeasurement beta cannot be set to value outside of reasonable range: ", value,". Must be within range ",min_value,":",  max_value, "")





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









    def del_depth(self):
        return PhotosynthesisMeasurement.del_depth(self)


    def del_pmax(self):
        return PhotosynthesisMeasurement.del_pmax(self)




    thermal_layer = property(get_thermal_layer, set_thermal_layer, del_thermal_layer, "thermal_layer's docstring")
    phyto_alpha = property(get_phyto_alpha, set_phyto_alpha, del_phyto_alpha, "phyto_alpha's docstring")
    phyto_beta = property(get_phyto_beta, set_phyto_beta, del_phyto_beta, "phyto_beta's docstring")


    #############################################
    #VALIDATORS
    #############################################
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



def main():
    print "hello world"
    print "let's test if the class works as intended."
    bob = PhytoPlanktonPhotosynthesisMeasurement(1, 5, 4.11, 0.05,0.01)

    print "thermal layer is ", bob.get_thermal_layer()
    print "depth is ", bob.get_depth()
    print "pmax is ", bob.get_pmax()
    print "alpha is ", bob.get_phyto_alpha()
    print "beta is ", bob.get_phyto_beta()

#     print "attempting to set everything to negative values"
    #These should all give error/exception.
#     bob.set_depth(-1)
#     bob.set_phyto_alpha(-1)
#     bob.set_phyto_beta(-1)
#     bob.set_pmax(-1)
#     bob.set_thermal_layer(-1)

#     print "attempting to set everything to HUGE values"
    #These should all give error/exception.
#     usa_billion = 1000000000 #10^9, as opposed to a british billion, which is, I believe, 10^12
#     bob.set_depth(usa_billion)
#     bob.set_phyto_alpha(usa_billion)
#     bob.set_phyto_beta(usa_billion)
#     bob.set_pmax(usa_billion)
#     bob.set_thermal_layer(usa_billion)

    print "attempting to set everything to minimum values"
    #These should all work.
    bob.set_depth(PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_DEPTH)
    bob.set_phyto_alpha(PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_ALPHA)
    bob.set_phyto_beta(PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_BETA)
    bob.set_pmax(PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_PMAX)
    bob.set_thermal_layer(PhytoPlanktonPhotosynthesisMeasurement.MIN_VALID_THERMAL_LAYER)


    print "thermal layer is ", bob.get_thermal_layer()
    print "depth is ", bob.get_depth()
    print "pmax is ", bob.get_pmax()
    print "alpha is ", bob.get_phyto_alpha()
    print "beta is ", bob.get_phyto_beta()

    print "attempting to set everything to maximum values"
    #These should all work.
    bob.set_depth(PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_DEPTH)
    bob.set_phyto_alpha(PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_ALPHA)
    bob.set_phyto_beta(PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_BETA)
    bob.set_pmax(PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_PMAX)
    bob.set_thermal_layer(PhytoPlanktonPhotosynthesisMeasurement.MAX_VALID_THERMAL_LAYER)


    print "thermal layer is ", bob.get_thermal_layer()
    print "depth is ", bob.get_depth()
    print "pmax is ", bob.get_pmax()
    print "alpha is ", bob.get_phyto_alpha()
    print "beta is ", bob.get_phyto_beta()



if __name__ == "__main__":
    main()
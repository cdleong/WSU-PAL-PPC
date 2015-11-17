'''
Created on Jun 17, 2015

@author: cdleong
'''

class PondShape(object):
    '''
    abstract class. Nothing's really implemented. 
    '''
    #######################################################
    #KNOWS... nothing. Depends on implementation.
    #######################################################
    


    def get_volume(self):
        '''
        @return: The volume of the lake, in m^3 
        @rtype: double
        '''
        pass    
    
    def get_max_depth(self):
        '''
        @return: get maximum depth, in meters
        @rtype: double
        '''
        pass
    
    def get_mean_depth(self):
        '''
        @return: get mean depth, in meters
        @rtype: double
        '''        
        pass
    
    def get_water_surface_area_at_depth(self, depth =0.0):
        
        pass
    
    def get_sediment_area_at_depth(self, depth=0.0, depth_interval=0.1):
        pass
    
    def get_volume_above_depth(self, depth=0.0, depth_interval=0.1):
        pass
        
    def get_sediment_area_above_depth(self, depth=0.0):
        pass

    def get_fractional_sediment_area_at_depth(self, depth=0.0, total_sediment_area=0.0, depth_interval=0.1):
        pass    
    
    #June 22: depth intervals aren't a thing now. 

    def validate_depth(self, depth):
        pass
     
    def update_shape(self, other_pond_shape):
        pass



def main():
    print "hello world"
    


if __name__ == "__main__":
    main()    
        
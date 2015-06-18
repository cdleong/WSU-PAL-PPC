'''
Created on Jun 18, 2015

@author: cdleong
'''
from mysite.pond_shape import PondShape
import numpy as np
from scipy.interpolate import interp1d


class BathymetricPondShape(PondShape):
    '''
    Based on bethymetric measurements, i.e.
    "When depth is z, water surface area is a"
    Assumption: 
    '''
    water_surface_areas = {} #water surface water_surface_areas.
    depth_interval_percentage =1 #1%


    def __init__(self, areas = {0:100,5:50,10:1}, depth_interval_percentage = 0.01):
        '''
        Constructor
        '''
        self.water_surface_areas=areas
        self.depth_interval_percentage = depth_interval_percentage
        

    def get_depth_interval_percentage(self):
        return self.depth_interval_percentage
    
    def set_depth_interval_percentage(self, depth_interval_percentage=1):
        validated_depth_interval_percentage = 1
        if(depth_interval_percentage>100):
            validated_depth_interval_percentage = 100 #100%
        elif(depth_interval_percentage<=0):
            validated_depth_interval_percentage = 1 #1%
        self.depth_interval_percentage = validated_depth_interval_percentage
               
    def get_depth_interval_meters(self):
        '''
        the depth_interval, in meters
        
        Calculates based on depth_interval_percentage and maxDepth
        '''
        max_depth = self.get_max_depth()
        proportion = self.get_depth_interval_percentage()/100
        depth_interval_meters = max_depth()*proportion
        return depth_interval_meters
        
        
       

    ##################################
    #GET VOLUME METHOD
    ##################################    
    def get_volume(self):
        '''
        @return:  the total volume, in cubic meters
        @rtype: 
        '''            
        return self.get_volume_above_depth(self.get_max_depth())

    def addBathymetryLayer(self, depth=0, area=0):
        self.water_surface_areas[depth]=area
        


    def get_max_depth(self):
        keys = self.water_surface_areas.keys()
        maxDepth = max(keys)
        return maxDepth
    
    #########################
    #get_mean_depth(self):
    #########################
    def get_mean_depth(self):
#         depths = self.areas.keys()
#         depthsSorted = sorted(depths)
#         sediment_area_at_depth =         
        #TODO: implement this. Need to find out the proportion of each depth
        
        #total area at zero
        
        #for each depth, area at depth. Weighted based on area at depth/ total area
        
        #average depth = 
            
            
        return 3.14 #TODO: implement




    ####################################################
    #get_water_surface_area_at_depth(self, depth=0.0):
    ####################################################
    def get_water_surface_area_at_depth(self, depth=0.0):
        '''
        Figures out the surface area at depth
        
        Uses http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        For depths not in layers.  
        '''
        #TODO: implement this
        water_surface_area_at_depth = 0
        
        validated_depth = self.__validate_depth(depth)
        
        #get interpolation function
        x = self.water_surface_areas.keys()
        y = self.water_surface_areas.values() 
        f = interp1d(x, y)
        
        try:
            water_surface_area_at_depth = self.water_surface_areas[validated_depth]
        except KeyError:
            #y=mx+b
            water_surface_area_at_depth = f(validated_depth) 
        
        
        return water_surface_area_at_depth


    
    def get_sediment_surface_area_at_depth(self, depth=0.0):
        '''
        Essentially, returns an estimate of the area of cone or donut of lake bottom, 
        whose bottom edge is at depth and top edge is at (depth-interval)
        if given depth = max_depth and interval also = max_depth, should estimate sediment for the whole lake. 
        ...which should add up to water surface area at depth 0 by the way
        
        depth should be between 0 and max_depth
        interval should be between 0 and max_depth
        '''
        #how...? If I have water surface area at 0 and 10, and they ask for 5..?
        
        sediment_surface_area = 0.0
        interval = self.get_depth_interval_meters()
        
        lower_edge_depth = self.__validate_depth(depth)
        validated_interval = self.__validate_depth(interval)
        upper_edge_depth = self.__validate_depth(depth-validated_interval)
        
        
        
        
        if(lower_edge_depth>upper_edge_depth):#upper edge should be a smaller value of depth
            #all is well. Do nothing.
            pass
            
            
            
        elif (lower_edge_depth<upper_edge_depth):
            #interval was negative?
            #switch them. 
            lower_edge_depth, upper_edge_depth = upper_edge_depth,lower_edge_depth
        
            
        else: #they are the same
            print "lower and upper bounds of sediment region are the same. Area is 0"
            return 0 
            
        
        upper_water_area = self.get_water_surface_area_at_depth(upper_edge_depth)
        lower_water_area = self.get_water_surface_area_at_depth(lower_edge_depth)
        
        #The theory is, we get basically the top side of a right cone. 
        #
        # ASCII picture of a lake cross-section:
        #
        #          "sediment_surface_area"
        #          | 
        #  ________|__________
        #  |                  |
        #  \/                 \/
        #________________________     <--- upper_water_area
        #\   |              |   /
        # \  |interval      |  /
        # h\ |              | /
        #   \|______________|/        <--- lower_water_area
        #
        # What we ACTUALLY want is h, but in practice the slope is generally shallow enough in the littoral zone 
        # (the zone we are interested in) that this is a good approximation

        sediment_surface_area = upper_water_area-lower_water_area 
        
        
        
        
        return sediment_surface_area


    def get_volume_above_depth(self, depth):
        ####################################################
        # ASCII picture of an example lake cross-section:
        #
        # ________________________     <-areas[z0]
        #.\   |              |   /.
        #. \  |interval      |  / .    
        #.  \ |              | /  .
        #....\|______________|/....    <-areas[z1]
        #                        ^
        #                        |
        #                        |
        #                        x = 1/2 (areas[z0]-areas[z1])
        # error is just 2x*interval, or just (areas[z0]-areas[z1])*interval
        # Volume from z0 to z1 can be approximated using
        # areas[z0]*interval, which overestimates by error    :result is correctAnswer+error
        # areas[z1]*interval, which underestimates by error   :result is correctAnswer-error 
        # correct answer should be areas[z0]*interval -error  
        #
        ####################################################        
        return 3.14 #TODO:implement


    def get_sediment_area_above_depth(self, depth):
        return 3.14 #TODO:implement
    
    
    def __validate_depth(self,depth):
        '''
        I keep using the following bit of code.
        '''
        if(depth<0):
            depth = 0
        elif(depth>self.get_max_depth()):
            depth=self.get_max_depth()
        
        return depth

def main():
    print "hello world"
    shape_instance = BathymetricPondShape()
    print "max depth is (should be 10): ", shape_instance.get_max_depth()
    print "depths ",shape_instance.water_surface_areas.keys()
    print "areas ",shape_instance.water_surface_areas.values()
#     print "mean depth is (should be 10)",
     
    for depth in range (0, shape_instance.get_max_depth()):
        print "water surface area at depth ", depth, " is ", shape_instance.get_water_surface_area_at_depth(depth) 
        print "sediment surface area at depth ", depth, " with interval 1 is: ", shape_instance.get_sediment_surface_area_at_depth(depth, 1)
        
     
    


if __name__ == "__main__":
    main()    
                
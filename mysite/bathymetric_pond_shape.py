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
    
    # dict tutorial here: http://www.tutorialspoint.com/python/python_dictionary.htm
    water_surface_areas = {}  # water surface water_surface_areas.
    depth_interval_percentage = 1.0  # 1%


    def __init__(self, areas={0:100, 5:50, 10:1}, depth_interval_percentage=10.0):
        '''
        Constructor
        @param areas: a python dict containing depth/area pairs. 
        @param depth_interval_percentage: The "resolution" for calculations to use, 
            as a number between 0 and 100 representing the percentage of maximum depth to use.
        '''
        self.water_surface_areas = areas
        self.set_depth_interval_percentage(depth_interval_percentage)
        

    def get_depth_interval_percentage(self):
        '''
        @return: depth_interval_percentage
        '''
        return self.depth_interval_percentage
    
    def set_depth_interval_percentage(self, depth_interval_percentage=1.0):
        '''
        Set depth interval percentage.
        Setter method.
        '''
        validated_depth_interval_percentage = 1.0
        if(depth_interval_percentage > 100.0):
            validated_depth_interval_percentage = 100.0  # 100%
        elif(depth_interval_percentage <= 0.0):
            validated_depth_interval_percentage = 1.0  # 1%
        else: 
            validated_depth_interval_percentage = depth_interval_percentage
        self.depth_interval_percentage = validated_depth_interval_percentage
               
    def get_depth_interval_meters(self):
        '''
        Getter method. 
        @return: the depth_interval, in meters, calculated based on depth_interval_percentage and maxDepth
        '''
        max_depth = self.get_max_depth()
        proportion = self.get_depth_interval_percentage() / 100.0
        depth_interval_meters = max_depth * proportion
        return depth_interval_meters
        
        
       

   
    def get_volume(self):
        '''
        Get Total Lake Volume
        @return:  the total volume, in cubic meters
        @rtype: 
        '''            
        return self.get_volume_above_depth(self.get_max_depth())

    def addBathymetryLayer(self, depth=0.0, area=0.0):
        '''
        @param depth: float value, depth in meters of area measurement.
        @param area:  float value, area in meters squared at depth. 
        '''
        if (depth < 0.0 or area <= 0.0):
            raise Exception("invalid depth or area")  # todo: more details
        else:
            self.water_surface_areas[depth] = area
            
        


    def get_max_depth(self):
        keys = self.water_surface_areas.keys()
        maxDepth = max(keys)
        return maxDepth
    
    #########################
    # get_mean_depth(self):
    #########################
    def get_mean_depth(self):
        '''
        Get Mean Depth
        @return: average depth, in meters, for the whole pond.
        @rtype: float
        '''
        depth_interval = self.get_depth_interval_meters()
        max_depth = self.get_max_depth()
        total_area = self.get_sediment_area_above_depth(max_depth)
        
                
        current_depth = depth_interval  # no point starting at 0, since that's just gonna be zero anyway.
        weighted_total = 0.0 
        while current_depth <= max_depth:
            area_at_depth = self.get_sediment_surface_area_at_depth(current_depth) # there are this many square meters at this depth            
            weighted_total+=area_at_depth*current_depth 
            current_depth += depth_interval
        mean_depth  = weighted_total/total_area
        return mean_depth  




    def get_water_surface_area_at_depth(self, depth=0.0):
        '''
        Get Water Surface Area at Specified Depth
        Figures out the surface area at depth
        
        Uses http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        For depths not in layers.
        @param depth: depth in meters to calculate at   
        @rtype: float
        '''
        water_surface_area_at_depth = 0        
        validated_depth = self.__validate_depth(depth)
        
        # get interpolation function
        x = self.water_surface_areas.keys()
        y = self.water_surface_areas.values() 
        f = interp1d(x, y)
        
        try:
            water_surface_area_at_depth = self.water_surface_areas[validated_depth]
        except KeyError:
            water_surface_area_at_depth = f(validated_depth) 
        
        
        return water_surface_area_at_depth


    
    def get_sediment_surface_area_at_depth(self, depth=0.0):
        '''
        Get Sediment Surface Area at Specified Depth
        Essentially, returns an estimate of the area of the section of lake bottom, 
        whose bottom edge is at depth and top edge is at (depth-self.get_depth_interval_meters())
        On a perfectly conical lake this would form a truncated inverted cone with a hole in the middle.
        If given depth = max_depth and depth_interval also = max_depth, should estimate sediment for the whole lake. 
        ...which should add up to water surface area at depth 0 by the way
        
        @param depth: depth should be in meters, and between 0 and max_depth. It'll be set to one of those if not so.
        @return: sediment area
        @rtype: float
        '''
        
        validated_depth = self.__validate_depth(depth)
        depth_interval = self.get_depth_interval_meters()        
        lower_edge_depth = validated_depth        
        upper_edge_depth = validated_depth - depth_interval
        
        #validate the depths of the two
        if(lower_edge_depth > upper_edge_depth):  # upper edge should be a smaller value of depth
            # all is well. Do nothing.
            pass
        elif (lower_edge_depth < upper_edge_depth):
            # depth_interval was negative?
            # switch them. 
            lower_edge_depth, upper_edge_depth = upper_edge_depth, lower_edge_depth                    
        else:  # they are the same
            print "lower and upper bounds of sediment region are the same. Area is 0"
            return 0 
            
        
        upper_water_area = self.get_water_surface_area_at_depth(upper_edge_depth)
        lower_water_area = self.get_water_surface_area_at_depth(lower_edge_depth)
        

        
        # The theory is, we get basically the top side of a right cone/donut thing. 
        #
        # ASCII picture of a lake cross-section:
        #
        #          "sediment_surface_area"
        #          | 
        #  ________|__________
        #  |                  |
        #  \/                 \/
        # ________________________     <--- upper_water_area
        # \   |              |   /
        #  \  |depth_interval      |  /
        # h \ |              | /
        #    \|______________|/        <--- lower_water_area
        #
        # What we ACTUALLY want is h, but in practice the slope is generally shallow enough in the littoral zone 
        # (the zone we are interested in) that this is a good approximation
        sediment_surface_area = upper_water_area - lower_water_area 
        
        # it's _possible_ that the lake gets *wider* as it goes down. 
        sediment_surface_area = np.abs(sediment_surface_area)
        return sediment_surface_area


    def get_volume_above_depth(self, depth=0.0):
        '''
        
        O(number of depth intervals*O(get_volume_at_depth()))
        @param depth: float value. depth in meters 
        @return: volume in cubic meters
        @rtype: float
        '''
        validated_depth = self.__validate_depth(depth)
        
        # just find the volume at each interval and add them all up.
        depth_interval = self.get_depth_interval_meters()
        current_depth = depth_interval  # no point starting at 0, since that's just gonna be zero anyway.
        total_volume = 0.0  
        while current_depth <= validated_depth:
            current_volume = self.get_volume_at_depth(validated_depth)
            total_volume += current_volume
            current_depth += depth_interval
        return total_volume
         

    def get_volume_at_depth(self, depth=0.0):
        '''
        given a depth, gives the volume of the shape with a lower surface at area and upper surface at area-depth_interval 
        @param depth: float value. depth in meters. 
        @return: volume.
        @rtype: float        
        '''
        ####################################################
        # ASCII picture of an example lake cross-section:
        #
        # ________________________     <-areas[z0]
        # .\   |              |   /.
        # . \  |interval      |  / .    
        # .  \ |              | /  .
        # ....\|______________|/....    <-areas[z1]
        #                        ^
        #                        |
        #                        |
        #                        x = 1/2 (areas[z0]-areas[z1])
        # error is just 2x*interval, or just (areas[z0]-areas[z1])*interval
        # Volume from z0 to z1 can be approximated using
        # areas[z0]*interval, which overestimates by error    :result is correctAnswer+error
        # areas[z1]*interval, which underestimates by error   :result is correctAnswer-error 
        # correct answer should be areas[z0]*interval -error or areas[z1]*interval +error
        #    
        ####################################################      
        
        validated_depth = self.__validate_depth(depth)
        depth_interval = self.get_depth_interval_meters()        
        lower_edge_depth = validated_depth        
        upper_edge_depth = validated_depth - depth_interval
        
        #validate the depths of the two
        if(lower_edge_depth > upper_edge_depth):  # upper edge should be a smaller value of depth
            # all is well. Do nothing.
            pass
        elif (lower_edge_depth < upper_edge_depth):
            # depth_interval was negative?
            # switch them. 
            lower_edge_depth, upper_edge_depth = upper_edge_depth, lower_edge_depth                    
        else:  # they are the same
            print "lower and upper bounds of volume region are the same. Volume is 0"
            return 0.0 
        
        upper_water_area = self.get_water_surface_area_at_depth(upper_edge_depth)
        lower_water_area = self.get_water_surface_area_at_depth(lower_edge_depth)    
        
        upper_calculated_volume = upper_water_area*depth_interval #equivalent to correct answer + error
        lower_calculated_volume = lower_water_area*depth_interval #equivalent to correct answer - error
        
        volume_at_depth = (upper_calculated_volume+lower_calculated_volume)/2 #equivalent to (correct answer)
        return volume_at_depth

    def get_sediment_area_above_depth(self, depth=0.0):
        '''
        @param param:depth in meters. float value 
        @return: the area of the sediment above a specific depth.
        @rtype: float value
        '''
        
        validated_depth = self.__validate_depth(depth)
        
        # add up the sediment area at every interval.
        total_area = 0.0        
        depth_interval = self.get_depth_interval_meters()
        current_depth = depth_interval        
        while current_depth <= validated_depth:
            current_area = self.get_sediment_surface_area_at_depth(current_depth)
            total_area += current_area 
            current_depth += depth_interval
            
        
        return total_area 
    
    
    def __validate_depth(self, depth=0.0):
        '''
        I keep using the following bit of code.
        Given a depth, checks to see if it is between 0 and max_depth.
        If outside that range, sets it to the closest one.
        @param depth: the value to be validated.
        @return: a float value between 0 and max depth of pond 
        '''
        if(depth < 0):
            depth = 0
        elif(depth > self.get_max_depth()):
            depth = self.get_max_depth()
        
        return depth

def main():
    print "hello world"
    shape_instance = BathymetricPondShape()
    print "max depth is (should be 10): ", shape_instance.get_max_depth()
    print "depths ", shape_instance.water_surface_areas.keys()
    print "areas ", shape_instance.water_surface_areas.values()
    
    max_depth = shape_instance.get_max_depth()
    half_max_depth = max_depth / 2
    
    print "sediment area total above depth ", max_depth, " is ", shape_instance.get_sediment_area_above_depth(max_depth)
    print "sediment area total above depth ", half_max_depth, " is ", shape_instance.get_sediment_area_above_depth(half_max_depth)
    
    print "total volume is", shape_instance.get_volume()
    print "total volume above depth ", max_depth, " is ", shape_instance.get_volume_above_depth(max_depth)
    print "total volume above depth ", half_max_depth, " is ", shape_instance.get_volume_above_depth(half_max_depth)
    
    print "mean depth is ", shape_instance.get_mean_depth()

    shape_instance.addBathymetryLayer(1, 100)
     
    for depth in range (0, shape_instance.get_max_depth()):
        print "water surface area at depth ", depth, " is ", shape_instance.get_water_surface_area_at_depth(depth) 
        print "sediment surface area at depth ", depth, " with interval (in meters) of ", shape_instance.get_depth_interval_meters(), " is: ", shape_instance.get_sediment_surface_area_at_depth(depth)
        
     
    


if __name__ == "__main__":
    main()    
                

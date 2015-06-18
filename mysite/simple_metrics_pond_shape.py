'''
Created on Jun 18, 2015

@author: cdleong
'''
from mysite.pond_shape import PondShape
import math as mat

class SimpleMetricsPondShape(PondShape):
    '''
    based on simple metrics, max depth and mean depth 
    '''
    
    max_depth = 0.0
    mean_depth = 0.0    
    depth_interval = 0.0    
    surface_area_at_depth_zero = 0.0

    def __init__(self, max_depth, mean_depth, depth_interval, surface_area_at_depth_zero):
        self.max_depth = max_depth
        self.mean_depth = mean_depth
        self.depth_interval = depth_interval
        self.surface_area_at_depth_zero = surface_area_at_depth_zero

    def get_surface_area_at_depth_zero(self):
        return self.__surface_area_at_depth_zero


    def set_surface_area_at_depth_zero(self, value):
        self.__surface_area_at_depth_zero = value


    def del_surface_area_at_depth_zero(self):
        del self.__surface_area_at_depth_zero


    def get_max_depth(self):
        return self.__max_depth


    def get_mean_depth(self):
        return self.__mean_depth


    def get_depth_interval(self):
        return self.__depth_interval


    def set_max_depth(self, value):
        self.__max_depth = value


    def set_mean_depth(self, value):
        self.__mean_depth = value


    def set_depth_interval(self, value):
        self.__depth_interval = value


    def del_max_depth(self):
        del self.__max_depth


    def del_mean_depth(self):
        del self.__mean_depth


    def del_depth_interval(self):
        del self.__depth_interval



        



    
    def calculate_depth_ratio(self):
        return  self.get_mean_depth()/self.get_max_depth()


    
    def calculate_shape_factor(self):
        '''
        aka "gamma"
        '''
        depthRatio = self.calculate_depth_ratio()
        return depthRatio/(1-depthRatio) #todo: check for divide-by-zero

    def get_volume(self):
        depth = self.get_max_depth()
        volume =self.calculate_volume_above_depth(depth)
        return volume



    def get_water_surface_area_at_depth(self, depth=0.0):
        '''
        Source: Vadeboncoeur 2008, eqn. 1
        '''
        area_at_z = 0;
        surface_area_at_depth_zero = self.get_surface_area_at_depth_zero()   
        shape_factor = self.calculate_shape_factor()     
        #safety check
        if(depth<0):
            area_at_z=0;
        elif (depth> self.get_max_depth()):
            area_at_z = self.get_water_surface_area_at_depth(self.get_max_depth())#recursive call            
        else:        
            max_depth = self.get_max_depth()
            area_at_z = surface_area_at_depth_zero*mat.pow((1-(depth/max_depth), shape_factor))
        return area_at_z


    def get_sediment_surface_area_at_depth(self, depth=0.0):
        '''
        approximated as the difference between the water surface area at z and z-interval
        The two areas, subtracted, give us one side of a right triangle. 
        We actually want the hypotenuse, but the slope is generally shallow enough that they're nearly the same.   
        
        '''
        sediment_surface_area = 0
        interval = self.get_depth_interval()
        if(depth<0):
            sediment_surface_area = 0
        elif (depth>self.get_max_depth()):
            sediment_surface_area = self.get_sediment_surface_area_at_depth(self.get_max_depth())
        else:
            water_area = self.get_water_surface_area_at_depth(depth)
            shallower_water_area = self.get_water_surface_area_at_depth(depth-interval) 
            sediment_surface_area = shallower_water_area-water_area#TODO: make sure this isn't negative, eh?
        return sediment_surface_area
        
        


    def calculate_volume_above_depth(self, depth):
        '''
        Source: Vadeboncoeur 2008, eqn. 2
        '''
        shape_factor = self.calculate_shape_factor()
        volume = shape_factor*depth/(shape_factor+1)
        return volume


    def calculate_sediment_area_above_depth(self, depth):
        z =0
        depth_interval=self.get_depth_interval()
        total_area = 0;
        if(depth<0):
            total_area = 0;
        elif (depth>self.get_max_depth()):
            total_area = self.calculate_sediment_area_above_depth(self.get_max_depth())
        else:    
            while z<self.get_max_depth():
                
                interval_area = self.get_sediment_surface_area_at_depth(z)
                total_area+=interval_area
                z+=depth_interval
        return total_area
    
    
    
    
    max_depth = property(get_max_depth, set_max_depth, del_max_depth, "max_depth's docstring")
    mean_depth = property(get_mean_depth, set_mean_depth, del_mean_depth, "mean_depth's docstring")
    depth_interval = property(get_depth_interval, set_depth_interval, del_depth_interval, "depth_interval's docstring")
    surface_area_at_depth_zero = property(get_surface_area_at_depth_zero, set_surface_area_at_depth_zero, del_surface_area_at_depth_zero, "surface_area_at_depth_zero's docstring")




def main():
    print "hello world"


if __name__ == "__main__":
    main()    
                
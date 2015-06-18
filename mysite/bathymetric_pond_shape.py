'''
Created on Jun 18, 2015

@author: cdleong
'''
from mysite.pond_shape import PondShape

class BathymetricPondShape(PondShape):
    '''
    Based on bethymetric measurements, i.e.
    "When depth is z, water surface area is a"
    Assumption: 
    '''
    depths = {}


    def __init__(self, params):
        '''
        Constructor
        '''
        

    def get_volume(self):
        #TODO: 
        return PondShape.get_volume(self)


    def get_max_depth(self):
        return PondShape.get_max_depth(self)


    def get_mean_depth(self):
        return PondShape.get_mean_depth(self)


    def get_water_surface_area_at_depth(self, depth=0.0, interval=0.1):
        return PondShape.get_water_surface_area_at_depth(self, depth, interval)


    def get_sediment_surface_area_at_depth(self, depth=0.0, interval=0.1):
        return PondShape.get_sediment_surface_area_at_depth(self, depth, interval)


    def calculate_volume_above_depth(self, depth):
        return PondShape.calculate_volume_above_depth(self, depth)


    def calculate_sediment_area_above_depth(self, depth):
        return PondShape.calculate_sediment_area_above_depth(self, depth)

def main():
    print "hello world"


if __name__ == "__main__":
    main()    
                
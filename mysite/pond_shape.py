'''
Created on Jun 17, 2015

@author: cdleong
'''

class PondShape(object):
    '''
    abstract class. Nothing's really implemented. 
    '''
    ###########
    #KNOWS
    ###########
    


    def get_volume(self):
        return 0.0
    
    def get_max_depth(self):
        return 0.0
    
    def get_mean_depth(self):
        return 0.0
    
    def get_water_surface_area_at_depth(self, depth =0.0):
        return 0.0
    
    def get_sediment_surface_area_at_depth(self, depth=0.0):
        return 0.0
    
    def calculate_volume_above_depth(self, depth):
        return 0.0
        
    def calculate_sediment_area_above_depth(self, depth):
        return 0.0




def main():
    print "hello world"


if __name__ == "__main__":
    main()    
        
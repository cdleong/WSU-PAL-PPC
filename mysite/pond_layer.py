'''
Created on Mar 13, 2015

@author: web_dev
'''

class Pond_Layer(object):
    '''
    classdocs
    '''
    
    '''
    knows
    '''
    area = 0.0 #m^2
    fractional_area = 0.0 #m^2/m^2 = unitless fraction. All the layers should add up to 1 though.
    depth = 0.0
    


    def __init__(self, depth, area, fractional_area):
        '''
        Constructor
        '''
        self.depth = depth
        self.area=area
        self.fractional_area = fractional_area

    def get_fractional_area(self):
        return self.fractional_area


    def get_depth(self):
        return self.depth


    def set_fractional_area(self, value):
        self.fractional_area = value


    def set_depth(self, value):
        self.depth = value


        
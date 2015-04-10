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
    area = -1.0 #m^2
#     fractional_area = 0.0 #m^2/m^2 = unitless fraction. All the layers should add up to 1 though. Actually let us not keept this. Just calculate it. 
    depth = -1.0
    pmax = -1.0
    ik = -1.0
    bpprz =-1.0
    ppprz = -1.0


    def __init__(self, depth=-1.0, area=-1.0,  pmax =0.0, ik = 0.0, bpprz = -1.0):
        '''
        Constructor
        '''
        self.depth = depth
        self.area=area
        self.pmax = pmax
        self.ik=ik
        self.bpprz = bpprz

    def get_ppprz(self):
        return self.ppprz


    def set_ppprz(self, value):
        self.ppprz = value


    def get_area(self):
        return self.area


    def set_area(self, value):
        self.area = value


    def get_bpprz(self):
        return self.bpprz


    def set_bpprz(self, value):
        self.bpprz = value


    def get_ik(self):
        return self.ik


    def get_pmax(self):
        return self.pmax


    def set_ik(self, value):
        self.ik = value


    def set_pmax(self, value):
        self.pmax = value


    def del_ik(self):
        del self.ik




#     def get_fractional_area(self):
#         return self.fractional_area


    def get_depth(self):
        return self.depth


#     def set_fractional_area(self, value):
#         self.fractional_area = value


    def set_depth(self, value):
        self.depth = value




    


        
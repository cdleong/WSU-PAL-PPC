'''
Created on Jun 17, 2015

@author: cdleong
'''

class PhotosynthesisMeasurement(object):
    '''
    Abstract/generic class.
    double depth-         the depth, in meters, of the measurement
    double PMax         - From the Photosynthesis-Irradiance curve. Pmax = alpha*Ik
    '''
    ##########
    # KNOWS
    ##########
    depth = 0.0
    pmax = 0.0
        

    def __init__(self, depth=0.0, pmax=0.0):
        self.depth = depth
        self.pmax = pmax

    def get_depth(self):
        return self.__optical_depth


    def get_pmax(self):
        return self.__pmax



    def set_depth(self, value):
        self.__optical_depth = value


    def set_pmax(self, value):
        self.__pmax = value




    def del_depth(self):
        del self.__optical_depth


    def del_pmax(self):
        del self.__pmax



    

    depth = property(get_depth, set_depth, del_depth, "depth's docstring")
    pmax = property(get_pmax, set_pmax, del_pmax, "pmax's docstri")


    
    



def main():
    print "hello world"
    






if __name__ == "__main__":
    main()        

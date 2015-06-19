'''
Created on Jun 17, 2015

@author: cdleong
'''

class PhotosynthesisMeasurement(object):
    '''
    Abstract/generic class.
    double depth-         the depth, in meters, of the measurement
    double PMax         - From the Photosynthesis-Irradiance curve. Pmax = alpha*Ik
    double Ik        - From the Photosynthesis-Irradiance curve. Ik = Pmax/alpha    
    double alpha        - From the Photosynthesis-Irradiance curve. alpha = Pmax/Ik    (REMOVED - REDUNDANT)    
    '''
    ##########
    # KNOWS
    ##########
    depth = 0.0
    pmax = 0.0
    ik = 0.0    
#     alpha = 0.0    #TODO: maybe add this in?
        

    def __init__(self, depth=0.0, pmax=0.0, ik=0.0):
        self.depth = depth
        self.pmax = pmax
        self.ik = ik

    def get_depth(self):
        return self.__optical_depth


    def get_pmax(self):
        return self.__pmax


    def get_ik(self):
        return self.__ik
    
    def get_alpha(self):
        return self.__ik / self.__pmax 


    def set_depth(self, value):
        self.__optical_depth = value


    def set_pmax(self, value):
        self.__pmax = value


    def set_ik(self, value):
        self.__ik = value


    def del_depth(self):
        del self.__optical_depth


    def del_pmax(self):
        del self.__pmax


    def del_ik(self):
        del self.__ik
        
    

    depth = property(get_depth, set_depth, del_depth, "depth's docstring")
    pmax = property(get_pmax, set_pmax, del_pmax, "pmax's docstring")
    ik = property(get_ik, set_ik, del_ik, "ik's docstring")


    
    



def main():
    print "hello world"
    
    depths = [0, 1, 2]
    pmaxes = [14.75637037, 25.96292587, 57.98165587]
    iks = [404.943, 315.97432, 238.6559726]
    
    measurements = []
    
    
    for i in range (0, 3):
        depth = depths[i]
        pmax = pmaxes[i]
        ik = iks[i]
        print "i is", i, " and depth is ", depth
        masurement = PhotosynthesisMeasurement(depth, pmax, ik)
        measurements.append(masurement)
    
    
    m = measurements.pop()
    print "the depth is ", m.get_depth()
    print "the pmax is ", m.get_pmax()
    print "the ik is ", m.get_ik()





if __name__ == "__main__":
    main()        

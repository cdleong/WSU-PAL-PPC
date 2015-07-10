'''
Created on Jun 17, 2015

@author: cdleong
'''
from mysite.photosynthesis_measurement import PhotosynthesisMeasurement

class BenthicPhotosynthesisMeasurement(PhotosynthesisMeasurement):
    '''
    classdocs
    '''
    
    ik=0.0
    
    def __init__(self, depth, pmax, ik):
        super(BenthicPhotosynthesisMeasurement, self).__init__(depth, pmax)
        self.set_ik(ik)

    def get_ik(self):
        return self.__ik


    def set_ik(self, value):
        self.__ik = value


    def del_ik(self):
        del self.__ik


    def get_depth(self):
        return PhotosynthesisMeasurement.get_depth(self)


    def get_pmax(self):
        return PhotosynthesisMeasurement.get_pmax(self)




    def get_alpha(self):
        return PhotosynthesisMeasurement.get_alpha(self)

    def set_depth(self, value):
        return PhotosynthesisMeasurement.set_depth(self, value)


    def set_pmax(self, value):
        return PhotosynthesisMeasurement.set_pmax(self, value)




    def del_depth(self):
        return PhotosynthesisMeasurement.del_depth(self)


    def del_pmax(self):
        return PhotosynthesisMeasurement.del_pmax(self)
    ik = property(get_ik, set_ik, del_ik, "ik's docstring")





def main():
    print "hello world"
    bpm = BenthicPhotosynthesisMeasurement(0.01, 15.0, 404.943)
    print "depth is", bpm.get_depth()
    print "benthic pmax is ", bpm.get_pmax()
    print "ik is ", bpm.get_ik()
    


if __name__ == "__main__":
    main()        
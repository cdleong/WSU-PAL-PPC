'''
Created on Jun 17, 2015

@author: cdleong
'''
from mysite.photosynthesis_measurement import PhotosynthesisMeasurement

class PhytoPlanktonPhotosynthesisMeasurement(PhotosynthesisMeasurement):
    '''
    classdocs
    '''


    def __init__(self, depth, pmax, ik):
        super(depth, pmax, ik)

    def get_depth(self):
        return PhotosynthesisMeasurement.get_depth(self)


    def get_pmax(self):
        return PhotosynthesisMeasurement.get_pmax(self)


    def get_ik(self):
        return PhotosynthesisMeasurement.get_ik(self)


    def set_depth(self, value):
        return PhotosynthesisMeasurement.set_depth(self, value)


    def set_pmax(self, value):
        return PhotosynthesisMeasurement.set_pmax(self, value)


    def set_ik(self, value):
        return PhotosynthesisMeasurement.set_ik(self, value)


    def del_depth(self):
        return PhotosynthesisMeasurement.del_depth(self)


    def del_pmax(self):
        return PhotosynthesisMeasurement.del_pmax(self)


    def del_ik(self):
        return PhotosynthesisMeasurement.del_ik(self)




def main():
    print "hello world"


if __name__ == "__main__":
    main()        
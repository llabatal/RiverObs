"""
Fast access to a data base containing a set of geometries. 

The data base is created by reading a shapefile, and write an rtree index for it for future use.

All bounding boxes are assumed to be an iterable (xmin,ymin,xmax,ymax)
"""

from os.path import exists
import pysal
from rtree import index
from shapely.geometry import asShape, Polygon

def bbox_generator_3D(shape,dbf,dt,tindex=1,store_obj=False):
    """Following the rtree documentation, a fast way to load iterables into the RTree index.

    dbf: vector such that t = dbf[tindex] is the time associated with that bounding box.
    dt: tmin = t - dt/2, tmax = d + dt/2 determines the time bounding box.
    """

    if store_obj:
        for i, obj in enumerate(shape):
            yield (i, shape_bbox_dbf_as_tuple(obj,dbf[i],dt,tindex=tindex) , obj)
    else:
        for i, obj in enumerate(shape):
            yield (i, shape_bbox_dbf_as_tuple(obj,dbf[i],dt,tindex=tindex)  , i)

def bbox_generator_2D(shape,store_obj=False):
    """Following the rtree documentation, a fast way to load iterables into the RTree index."""
    if store_obj:
        for i, obj in enumerate(shape):
            yield (i, shape_bbox_as_tuple(obj) , obj)
    else:
        for i, obj in enumerate(shape):
            yield (i, shape_bbox_as_tuple(obj)  , i)            
                   
def shape_bbox_dbf_as_tuple(shape,dbf,dt,tindex=1):
    """Return a (x,y,time) bbox.

    shape: contains the bounding box
    """
    t = dbf[0][tindex]
    tmin = t - dt/2
    tmax = t + dt/2
    return (shape.bounding_box.left, shape.bounding_box.lower, tmin,
            shape.bounding_box.right, shape.bounding_box.upper, tmax)

def shape_bbox_as_tuple(shape):
    """Return a (x,y) bbox.

    shape: contains the bounding box
    """
    return (shape.bounding_box.left, shape.bounding_box.lower,
            shape.bounding_box.right, shape.bounding_box.upper)

def write_shape_rtree_3D(shape_file_root,dt,time_kwd='time',store_obj=False):
    """Write an RTree indexing structure to file."""

    shape = pysal.open(shape_file_root+'.shp')
    dbf = pysal.open(shape_file_root+'.dbf')
    tindex = dbf.header.index(time_kwd)
    p = index.Property()
    p.dimension = 3
    index.Index(shape_file_root,
                bbox_generator_3D(shape,dbf,dt,tindex=tindex,store_obj=store_obj),properties=p)

def write_shape_rtree_2D(shape_file_root,store_obj=False):
    """Write an RTree indexing structure to file.

    This will produce two files (shape_file_root.dat and shape_file_root.idx)
    which are used for rtree look-up.
    """

    shape = pysal.open(shape_file_root+'.shp')
    index.Index(shape_file_root,
                bbox_generator_2D(shape,store_obj=store_obj))  

class GeometryDataBase2D:
    """Read geometry shapefile and rtree and perform queries on it"""

    def __init__(self,shape_file_root,store_obj=False,dimension=2):
        """Return an rtree index object containing the bounding boxes of the shapefile object.
        If the files required by rtree (.idx and .dat) do not exist in the shapefile directory, they
        are created on initialization.

        shape_file_root: root shapefile name
        store_obj: if the rtree file does not exist, this is passed to write_shape_rtree_2D
        and determines whether the shape index (store_obj = False) or the shape are stored.
        """

        # Check that the rtree files are there, otherwise, create them

        if not ( exists(shape_file_root+'idx') and exists(shape_file_root+'dat') ):
            write_shape_rtree_2D(shape_file_root,store_obj=store_obj)
        
        self.shape = pysal.open(shape_file_root+'.shp')
        p = index.Property()
        p.dimension = dimension
        p.overwrite = False
        self.idx = index.Index(shape_file_root,properties=p)

    def intersects_xy_bbox(self,xy_bbox):
        """Return the ids for objects which intersect by the input 2D bbox."""

        shapely_bbox = Polygon([(xy_bbox[0],xy_bbox[1]),(xy_bbox[0],xy_bbox[3]),(xy_bbox[2],xy_bbox[3]),(xy_bbox[2],xy_bbox[1])])

        return [id for id in self.idx.intersection(xy_bbox,objects='raw') if shapely_bbox.intersects(asShape(self.shape[id]))]

    def get_reach_intersect_xy_bbox(self,xy_bbox):
        """Return the shapely objects which intersect by the input 2D bbox."""

        shapely_bbox = Polygon([(xy_bbox[0],xy_bbox[1]),(xy_bbox[0],xy_bbox[3]),(xy_bbox[2],xy_bbox[3]),(xy_bbox[2],xy_bbox[1])])

        return [asShape(self.shape[id]) for id in self.idx.intersection(xy_bbox,objects='raw') 
                        if shapely_bbox.intersects(asShape(self.shape[id]))]
    
    def contains_point(self,x, y,eps=1.e-6):
        """Return the ids for objects which intersect by the input 2D point."""

        xy_bbox = (x-eps, y-eps, x+eps, y+eps)

        return self.intersects_xy_bbox(xy_bbox)

    
class ReachDataBase3D:
    """Read geometry shapefile and dbf containing time and rtree and perform queries on it"""

    def __init__(self,shape_file_root,dt=1,time_kwd='time',store_obj=False,dimension=3):
        """Return an rtree index object containing the bounding boxes of the shapefile object."""

        # Check that the rtree files are there, otherwise, create them

        if not ( exists(shape_file_root+'idx') and exists(shape_file_root+'dat') ):
            write_shape_rtree_3D(shape_file_root,dt,time_kwd=time_kwd,store_obj=store_obj)
        
        self.shape = pysal.open(shape_file_root+'.shp')
        self.dbf = pysal.open(shape_file_root+'.dbf')
        self.tindex = self.dbf.header.index(time_kwd)
        p = index.Property()
        p.dimension = dimension
        p.overwrite = False
        self.idx = index.Index(shape_file_root,properties=p)

    def intersects_xy_time_bbox(self,xyt_bbox):
        """Return the ids for objects which intersect by the input 3D bbox."""

        shapely_bbox = Polygon([(xyt_bbox[0],xyt_bbox[1]),(xyt_bbox[0],xyt_bbox[4]),(xyt_bbox[3],xyt_bbox[4]),(xyt_bbox[3],xyt_bbox[1])])

        return [id for id in self.idx.intersection(xyt_bbox,objects='raw') if shapely_bbox.intersects(asShape(self.shape[id]))]

    def intersects_xy_bbox(self,xy_bbox,large_time=1.e16):
        """Return the ids for objects which intersect by the input 3D bbox."""

        xyt_bbox = (xy_bbox[0], xy_bbox[1], -large_time, xy_bbox[2], xy_bbox[3], large_time)
        shapely_bbox = Polygon([(xy_bbox[0],xy_bbox[1]),(xy_bbox[0],xy_bbox[3]),(xy_bbox[2],xy_bbox[3]),(xy_bbox[2],xy_bbox[1])])

        return [id for id in self.idx.intersection(xyt_bbox,objects='raw') if shapely_bbox.intersects(asShape(self.shape[id]))]


    def contains_point_time(self,x, y, time,eps=1.e-6):
        """Return the ids for objects which intersect by the input 3D point."""

        xyt_bbox = (x-eps, y-eps, time-eps, x+eps, y+eps, time+eps)

        return self.intersects_xy_time_bbox(xyt_bbox)
    
    def contains_point(self,x, y,eps=1.e-6):
        """Return the ids for objects which intersect by the input 2D point."""

        xy_bbox = (x-eps, y-eps, x+eps, y+eps)

        return self.intersects_xy_bbox(xy_bbox)
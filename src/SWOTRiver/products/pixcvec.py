'''
Copyright (c) 2018-, California Institute of Technology ("Caltech"). U.S.
Government sponsorship acknowledged.
All rights reserved.

Author (s): Alex Fore
'''
import os
import netCDF4
import warnings
import numpy as np
from collections import OrderedDict as odict

from SWOTWater.products.product import Product, FILL_VALUES, textjoin
from RiverObs.RiverObs import \
    MISSING_VALUE_FLT, MISSING_VALUE_INT4, MISSING_VALUE_INT9

class L2PIXCVector(Product):
    UID = "l2_hr_pixcvector"

    # copied from L2HRPIXC
    ATTRIBUTES = odict([
        ['Conventions', {
            'dtype': 'str', 'docstr': textjoin("""
                NetCDF-4 conventions adopted in this product. This attribute
                should be set to CF-1.7 to indicate that the group is compliant
                with the Climate and Forecast NetCDF conventions."""),
            'value': textjoin("""
                NetCDF-4 conventions adopted in this product. This attribute
                should be set to CF-1.7 to indicate that the group is compliant
                with the Climate and Forecast NetCDF conventions.""")}],
        ['title', {
            'dtype': 'str', 'docstr': textjoin("""
                Level 2 KaRIn high rate pixel cloud vector river product."""),
            'value': textjoin("""
                Level 2 KaRIn high rate pixel cloud vector river product.""")}],
        ['institution', {
            'dtype': 'str', 'docstr': textjoin("""
                Name of producing agency."""), 'value': 'JPL'}],
        ['source', {
            'dtype': 'str', 'docstr': textjoin("""
                The method of production of the original data. If it was
                model-generated, source should name the model and its version,
                as specifically as could be useful. If it is observational,
                source should characterize it (e.g., 'radiometer')."""),
            'value': ''}],
        ['history', {'dtype': 'str',
            'docstr': textjoin("""
                UTC time when file generated. Format is:
                'YYYY-MM-DD hh:mm:ss : Creation' """)}],
        ['mission_name', {'dtype': 'str' ,'value':'SWOT','docstr': 'SWOT'}],
        ['references', {'dtype': 'str',
            'docstr': textjoin("""
                Published or web-based references that describe
                the data or methods used to product it. Provides version number
                of software generating product.""")}],
        ['reference_document', {'dtype': 'str',
            'docstr': textjoin("""
                Name and version of Product Description Document
                to use as reference for product.""")}],
        ['contact', {'dtype': 'str',
            'docstr': textjoin("""
                Contact information for producer of product.
                (e.g., 'ops@jpl.nasa.gov').""")}],
        ['cycle_number', {'dtype': 'i2',
            'docstr': 'Cycle number of the product granule.'}],
        ['pass_number', {'dtype': 'i2',
            'docstr': 'Pass number of the product granule.'}],
        ['tile_number', {'dtype': 'i2',
            'docstr': 'Tile number in the pass of the product granule.'}],
        ['swath_side', {'dtype': 'str',
            'docstr': textjoin(
                """'L' or 'R' to indicate left and right swath,respectively.
                """)}],
        ['tile_name', {'dtype': 'str',
            'docstr': textjoin("""
                Tile name using format PPP_TTTS, where PPP is a 3 digit
                pass number with leading zeros, TTT is a 3 digit tile number
                within the pass, and S is a character 'L' or 'R' for the left
                and right swath, respectively.""")}],
        ['near_range', {'dtype': 'f8',
            'docstr': 'The slant range (m) for the first image pixel.'}],
        ['nominal_slant_range_spacing', {'dtype': 'f8',
            'docstr': textjoin("""
                The range spacing (m) corresponding to the 200 MHz
                sampling frequency""")}],
        ['start_time', {'dtype': 'str',
            'docstr': textjoin("""
                UTC time of first measurement. Format is: YYYY-MM-DD
                hh:mm:ss.ssssssZ""")}],
        ['stop_time', {'dtype': 'str',
            'docstr': textjoin("""
                UTC time of last measurement. Format is: YYYY-MM-DD
                hh:mm:ss.ssssssZ""")}],
        ['inner_first_latitude', {'dtype': 'str',
            'docstr': textjoin("""
                 Nominal swath corner latitude (degrees_north) for the first
                 range line and inner part of the swath""")}],
        ['inner_first_longitude', {'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner longitude (degrees_east) for the first
                 range line and inner part of the swath""")}],
        ['inner_last_latitude', {'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner latitude (degrees_north)  for the last
                 range line and inner part of the swath""")}],
        ['inner_last_longitude', {'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner longitude (degrees_east) for the last
                 range line and inner part of the swath""")}],
        ['outer_first_latitude', {'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner latitude (degrees_north) for the first
                 range line and outer part of the swath""")}],
        ['outer_first_longitude', {'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner longitude (degrees_east) for the first
                 range line and outer part of the swath""")}],
        ['outer_last_latitude', {'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner latitude (degrees_north) for the last
                 range line and outer part of the swath""")}],
        ['outer_last_longitude',{'dtype': 'f4',
            'docstr': textjoin("""
                 Nominal swath corner longitude (degrees_east) for the last
                 range line and outer part of the swath""")}],
        ['xref_input_l2_hr_pixc_files', {'dtype': 'str',
            'docstr': textjoin("""
                List of water mask pixel cloud files used to generate data in
                product.""")}],
        ['xref_static_river_db_file', {'dtype': 'str',
            'docstr': textjoin("""
                Name of static river a priori database file used to generate
                data in product.""")}],
        ['xref_static_river_db_file', {'dtype': 'str',
            'docstr': textjoin("""
                Name of static river a priori database file used to generate
                data in product.""")}],
        ['ellipsoid_semi_major_axis', {'dtype': 'f8',
            'docstr': 'Semi-major axis of reference ellipsoid in meters.'}],
        ['ellipsoid_flattening', {'dtype': 'f8',
            'docstr': 'Flattening of reference ellipsoid'}],
        ])

    DIMENSIONS = odict([['points', 0]])
    VARIABLES = odict([
        ['azimuth_index',
         odict([['dtype', 'i4'],
                ['long_name', 'rare interferogram azimuth index'],
                ['units', '1'],
                ['valid_min', 0],
                ['valid_max', 999999],
                ['comment', 'Rare interferogram azimuth index.'],
                ])],
        ['range_index',
         odict([['dtype', 'i4'],
                ['long_name', 'rare interferogram range index'],
                ['units', '1'],
                ['valid_min', 0],
                ['valid_max', 999999],
                ['comment', 'Rare interferogram range index.'],
                ])],
        ['latitude_vectorproc',
         odict([['dtype', 'f8'],
                ['long_name', 'latitude'],
                ['standard_name', 'improved geolocation latitude'],
                ['units', 'degrees_north'],
                ['valid_min', -90],
                ['valid_max', 90],
                ['comment', textjoin("""
                    Improved geodetic latitude of the pixel. Units are in
                    degrees north of the equator.""")],
                ])],
        ['longitude_vectorproc',
         odict([['dtype', 'f8'],
                ['long_name', 'longitude'],
                ['standard_name', 'improved geolocation longitude'],
                ['units', 'degrees_east'],
                ['valid_min', -180],
                ['valid_max', 180],
                ['comment', textjoin("""
                    Improved geodetic longitude of the pixel. Positive=degrees
                    east of the Prime Meridian. Negative=degrees west of the
                    Prime Meridian.""")],
                ])],
        ['height_vectorproc',
         odict([['dtype', 'f4'],
                ['long_name', 'height above reference ellipsoid'],
                ['units', 'm'],
                ['valid_min', -999999],
                ['valid_max', 999999],
                ['comment',
                 'Improved height of the pixel above the reference ellipsoid.'],
                ])],
        ['reach_id',
         odict([['dtype', 'i4'],
                ['long_name', 'identifier of the associated prior river reach'],
                ['valid_min', 0],
                ['valid_max', 2147483647],
                ['comment', textjoin("""
                    Unique reach identifier from the prior river database.
                    The format of the identifier is CBBBBBRRRT, where
                    C=continent, B=basin, R=reach, T=type.""")],
                ])],
        ['node_id',
         odict([['dtype', 'i4'],
                ['long_name',
                 "identifier of the associated prior river node"],
                ['valid_min', 0],
                ['valid_max', 2147483647],
                ['comment', textjoin("""
                    Unique node identifier from the prior river database. The
                    format of the identifier is CBBBBBRRRNNNT, where
                    C=continent, B=basin, R=reach, N=node, T=type of water
                    body.""")],
                ])],
        ['ice_clim_f',
         odict([['dtype', 'u1'],
                ['long_name', 'climatological ice cover flag'],
                ['source', 'UNC'],
                ['flag_meanings', textjoin("""
                    no_ice_cover partial_ice_cover full_ice_cover
                    not_available""")],
                ['flag_values', np.array([0, 1, 2, 255]).astype('i2')],
                ['valid_min', 0],
                ['valid_max', 255],
                ['comment', textjoin("""
                    Climatological ice cover flag indicating whether the node
                    is ice-covered on the day of the observation based on
                    external climatological information (not the SWOT
                    measurement).  Values of 0, 1, and 2 indicate that the
                    node is not ice covered, partially ice covered, and fully
                    ice covered, respectively. A value of 255 indicates that
                    this flag is not available.""")],
                ])],
        ['ice_dyn_f',
         odict([['dtype', 'u1'],
                ['long_name', 'dynamical ice cover flag'],
                ['source', 'UNC'],
                ['flag_meanings', textjoin("""
                    no_ice_cover partial_ice_cover full_ice_cover
                    not_available""")],
                ['flag_values', np.array([0, 1, 2, 255]).astype('i2')],
                ['valid_min', 0],
                ['valid_max', 255],
                ['comment', textjoin("""
                    Dynamic ice cover flag indicating whether the surface is
                    ice-covered on the day of the observation based on
                    analysis of external satellite optical data.  Values of
                    0, 1, and 2 indicate that the node is not ice covered,
                    partially ice covered, and fully ice covered, respectively.
                    A value of 255 indicates that this flag is not available.
                    """)],
                ])],
        ['pixc_index',
         odict([['dtype', 'i4'],
                ['long_name', 'pixel cloud index'],
                ['units', '1'],
                ['valid_min', 0],
                ['valid_max', 2147483647],
                ['comment', textjoin("""
                    Index of the data in the pixel_cloud group of the
                    L2_HR_PIXC file that is associated with the pixel.""")],
                ])],
        ['lake_flag',
         odict([['dtype', 'u1'],
                ['long_name', 'lake flag'],
                ['valid_min', 0],
                ['valid_max', 1],
                ['comment', textjoin("""
                    Flag indicating if the pixel is to be processed by the
                    L2_HR_LakeTile processor.  0= pixel is not to be processed
                    by the L2_HR_LakeTile processor.  1= pixel is to be
                    processed by the L2_HR_LakeTile processor.  A value of 1
                    can occur for pixels that are associated with a connected
                    lake type (T=3) in the reach_id and node_id.""")],
                ])],
        ['segmentation_label',
         odict([['dtype', 'i4'],
                ['long_name', 'segmentation label'],
                ['units', '1'],
                ['valid_min', 0],
                ['valid_max', 2147483647],
                ['comment', textjoin("""
                    A unique number of identifying which connected water
                    segment the pixel was assigned to.""")],
                ])],
        ['good_height_flag',
         odict([['dtype', 'u1'],
                ['long_name', 'good height flag'],
                ['valid_min', 0],
                ['valid_max', 1],
                ['comment', textjoin("""
                    Flag indicating that the pixel has a valid improved
                    height.""")],
                ])],
        ['distance_to_node',
         odict([['dtype', 'f4'],
                ['long_name', 'distance to node'],
                ['units', 'm'],
                ['valid_min', 0],
                ['valid_max', 9999],
                ['comment', textjoin("""
                    Distance from the pixel to the PRD node that it is
                    associated with.""")],
                ])],
        ['along_reach',
         odict([['dtype', 'f4'],
                ['long_name', 'along reach distance'],
                ['units', 'm'],
                ['valid_min', -999999],
                ['valid_max', 999999],
                ['comment', textjoin("""
                    Along-reach component of pixel location relative to PRD
                    node location. Negative=nominally upstream of PRD node.
                    Positive=nominally downstream of PRD node""")],
                ])],
        ['cross_reach',
         odict([['dtype', 'f4'],
                ['long_name', 'across reach distance'],
                ['units', 'm'],
                ['valid_min', -999999],
                ['valid_max', 999999],
                ['comment', textjoin("""
                    Cross-reach component of pixel location relative to PRD
                    node location. Negative= left side of centerline.
                    Positive= right side of centerline.""")],
                ])],
        ])

    for name, reference in VARIABLES.items():
        reference['dimensions'] = DIMENSIONS

    @staticmethod
    def dump_xml(pixcvectorriver_xml_file):
        with open(pixcvectorriver_xml_file, 'w') as ofp:
            L2PIXCVector.print_xml(ofp=ofp)

    def update_from_rivertile(self, rivertile):
        """Updates some stuff in PIXCVecRiver from RiverTile"""
        for node_id, ice_clim_f, ice_dyn_f in zip(
            rivertile.nodes.node_id, rivertile.nodes.ice_clim_f,
            rivertile.nodes.ice_dyn_f):
            mask = self.node_id == node_id
            self.ice_clim_f[mask] = ice_clim_f
            self.ice_dyn_f[mask] = ice_dyn_f

    def update_from_pixc(self, pixc_file):
        """Adds some attributes from PIXC file"""

        ATTRS_2COPY_FROM_PIXC = [
            'cycle_number', 'pass_number', 'tile_number', 'swath_side',
            'tile_name', 'start_time', 'stop_time', 'inner_first_latitude',
            'inner_first_longitude', 'inner_last_latitude',
            'outer_last_longitude', 'outer_first_latitude',
            'outer_first_longitude', 'outer_last_latitude',
            'ellipsoid_semi_major_axis', 'ellipsoid_flattening',
            'near_range', 'nominal_slant_range_spacing']

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            with netCDF4.Dataset(pixc_file, 'r') as ifp:
                for attr in ATTRS_2COPY_FROM_PIXC:
                    try:
                        value = getattr(ifp, attr)
                    except AttributeError:
                        value = getattr(ifp.groups['pixel_cloud'], attr, 'None')
                    self[attr] = value

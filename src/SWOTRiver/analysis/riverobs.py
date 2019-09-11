"""
Copyright (c) 2017-, California Institute of Technology ("Caltech"). U.S.
Government sponsorship acknowledged.
All rights reserved.

Author(s): Dustin Lagoy

"""
import warnings

import numpy as np

import SWOTWater.products.product
import SWOTRiver.analysis.tabley


def load_rivertiles(truth_file, data_file):
    truth = SWOTWater.products.product.MutableProduct.from_ncfile(truth_file)
    data = SWOTWater.products.product.MutableProduct.from_ncfile(data_file)
    return truth, data


def match_rivertiles(truth, data):
    match_reaches(truth, data)
    match_nodes(truth, data)


def match_reaches(truth, data):
    # get common reach ids from intersection
    common_ids = np.intersect1d(data.reaches.reach_id, truth.reaches.reach_id)
    data_mapping = [
        np.where(data.reaches.reach_id == i)[0][0] for i in common_ids]
    true_mapping = [
        np.where(truth.reaches.reach_id == i)[0][0] for i in common_ids]

    new_reaches = data.reaches.copy(with_variables=False)
    for name in data.reaches.variables:
        new_reaches[name] = data.reaches[name][data_mapping]
    data.reaches = new_reaches

    new_reaches = truth.reaches.copy(with_variables=False)
    for name in truth.reaches.variables:
        new_reaches[name] = truth.reaches[name][true_mapping]
    truth.reaches = new_reaches


def match_nodes(truth, data):
    common_ids = np.intersect1d(data.nodes.node_id, truth.nodes.node_id)
    data_mapping = [
        np.where(data.nodes.node_id == node)[0][0] for node in common_ids]
    true_mapping = [
        np.where(truth.nodes.node_id == node)[0][0] for node in common_ids]

    new_nodes = data.nodes.copy(with_variables=False)
    for name in data.nodes.variables:
        new_nodes[name] = data.nodes[name][data_mapping]
    data.nodes = new_nodes

    new_nodes = truth.nodes.copy(with_variables=False)
    for name in truth.nodes.variables:
        new_nodes[name] = truth.nodes[name][true_mapping]
    truth.nodes = new_nodes


def get_metrics(truth, data):
    metrics = {
        'area': (
            (data.area_total - truth.area_total) / truth.area_total) * 100.0,
        'area_detct':(
            (data.area_detct - truth.area_detct) / truth.area_detct) * 100.0,
        'height': (data.wse - truth.wse) * 1e2,#convert m to cm
        'slope': (data.slope - truth.slope) * 1e5,#convert from m/m to cm/km
        'width': data.width - truth.width,
    }
    return metrics

def mask_for_sci_req(metrics, truth, scene):
    
    msk = np.logical_and((np.abs(truth.reaches['xtrk_dist'])>10000),
          np.logical_and((np.abs(truth.reaches['xtrk_dist'])<60000), 
          np.logical_and((truth.reaches['width']>100),
              truth.reaches['area_total']>1e6)))
    return msk

def print_errors(metrics, msk=True):
    # get statistics of area error
    area_68 = np.nanpercentile(abs(metrics['area'][msk]), 68)
    area_50 = np.nanpercentile(metrics['area'][msk], 50)
    area_mean = np.nanmean(metrics['area'][msk])
    area_num = np.count_nonzero(~np.isnan(metrics['area'][msk]))
    # get statistics of height error
    height_68 = np.nanpercentile(abs(metrics['height'][msk]), 68)
    height_50 = np.nanpercentile(metrics['height'][msk], 50)
    height_mean = np.nanmean(metrics['height'][msk])
    height_num = np.count_nonzero(~np.isnan(metrics['height'][msk]))
    # get statistics of slope error
    slope_68 = np.nanpercentile(abs(metrics['slope'][msk]), 68)
    slope_50 = np.nanpercentile(metrics['slope'][msk], 50)
    slope_mean = np.nanmean(metrics['slope'][msk])
    slope_num = np.count_nonzero(~np.isnan(metrics['slope'][msk]))

    table = {
        'metric': ['area (%)', 'height (cm)', 'slope (cm/km)'],
        '|68%ile|': [area_68, height_68, slope_68],
        '50%ile': [area_50, height_50, slope_50],
        'mean': [area_mean, height_mean, slope_mean],
        'count': [area_num, height_num, slope_num],
    }
    SWOTRiver.analysis.tabley.print_table(table, precision=8)


def print_metrics(metrics, truth, scene, msk=None):
    table = {}
    if msk is None:
        msk = np.ones(np.shape(metrics['height']),dtype = bool)
    print(np.array(scene)[msk])
    table['hgt e (cm)'] = metrics['height'][msk]
    table['slp e (cm/km)'] = metrics['slope'][msk]
    table['area e (%)'] = metrics['area'][msk]
    table['wid e (m)'] = metrics['width'][msk]
    table['width (m)'] = truth.reaches['width'][msk]
    table['reach'] = truth.reaches['reach_id'][msk]
    table['xtrk (km)'] = truth.reaches['xtrk_dist'][msk]/1e3
    table['scene'] = np.array(scene)[msk]
    
    SWOTRiver.analysis.tabley.print_table(table, precision=5)

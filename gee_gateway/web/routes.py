import logging

from flask import request, jsonify, render_template
from flask_cors import CORS, cross_origin

from .. import gee_gateway
from ..gee.gee_exception import GEEException
from ..gee.utils import *

logger = logging.getLogger(__name__)

@gee_gateway.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@gee_gateway.route('/image', methods=['POST'])
def image():
    """ Return

    .. :quickref: Image; Get the MapID of a EE Image.

    **Example request**:

    .. code-block:: javascript

        {
            imageName: "XXX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX",
                gamma: 0.0
           }
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String imageName: name of the image
    :<json Object visParams: visualization parameters
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            imageName = json.get('imageName', None)
            if imageName:
                visParams = json.get('visParams', None)
                values = imageToMapId(imageName, visParams)
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200

@gee_gateway.route('/imageByMosaicCollection', methods=['POST'])
def imageByMosaicCollection():
    """
    .. :quickref: ImageCollection; Get the MapID of a EE ImageCollection.

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            visParams: {
                min: 0.0,
                max: 0.0,
                bands: "XX,XX,XX",
                gamma: 0.0
            },
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            mapid: "XXX",
            token: "XXX"
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json Object visParams: visualization parameters
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionName', None)
            if collectionName:
                visParams = json.get('visParams', None)
                dateFrom = json.get('dateFrom', None)
                dateTo = json.get('dateTo', None)
                values = firstImageInMosaicToMapId(collectionName, visParams, dateFrom, dateTo)
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200

@gee_gateway.route('/timeSeriesIndex', methods=['POST'])
def timeSeriesIndex():
    """
    .. :quickref: TimeSeries; Get the timeseries for a specific ImageCollection index, date range and a polygon OR a point

    **Example request**:

    .. code-block:: javascript

        {
            collectionName: "XX",
            indexName: "XX"
            scale: 0.0,
            geometry: [
                [0.0, 0.0],
                [...]
            ] OR [0.0, 0.0],
            dateFrom: "YYYY-MM-DD",
            dateTo: "YYYY-MM-DD"
        }

    **Example response**:

    .. code-block:: javascript

        {
            timeseries: [
                [0, 0.0],
                ...
            ]
        }

    :reqheader Accept: application/json
    :<json String collectionName: name of the image collection
    :<json String index: name of the index:  (e.g. NDVI, NDWI, NVI)
    :<json Float scale: scale in meters of the projection
    :<json Array polygon: the region over which to reduce data
    :<json String dateFrom: start date
    :<json String dateTo: end date
    :resheader Content-Type: application/json
    """
    values = {}
    try:
        json = request.get_json()
        if json:
            collectionName = json.get('collectionNameTimeSeries', None)
            geometry = json.get('polygon', None) #deprecated
            if not geometry:
                geometry = json.get('geometry', None)
            if collectionName and geometry:
                indexName = json.get('indexName', 'NDVI')
                scale = float(json.get('scale', 30))
                dateFrom = json.get('dateFromTimeSeries', None)
                dateTo = json.get('dateToTimeSeries', None)
                timeseries = getTimeSeriesByCollectionAndIndex(collectionName, indexName, scale, geometry, dateFrom, dateTo)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200

@gee_gateway.route('/timeSeriesIndex2', methods=['POST'])
def timeSeriesIndex2():
    """  """
    values = {}
    try:
        json = request.get_json()
        if json:
            geometry = json.get('polygon', None) #deprecated
            if not geometry:
                geometry = json.get('geometry', None)
            if geometry:
                indexName = json.get('indexName', 'NDVI')
                scale = float(json.get('scale', 30))
                timeseries = getTimeSeriesByIndex(indexName, scale, geometry)
                values = {
                    'timeseries': timeseries
                }
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200

@gee_gateway.route('/getStats', methods=['POST'])
def getStats():
    """
    .. :quickref: getStats; Get the population and elevation for a polygon

    **Example request**:

    .. code-block:: javascript

        {
            paramType: "XX",
            paramValue: [
                [0.0, 0.0],
                [...]
            ]
        }

    **Example response**:

    .. code-block:: javascript

        {maxElev: 1230, minElev: 1230, pop: 0}

    :reqheader Accept: application/json
    :<json String paramType: basin, landscape, or ''
    :<json Array polygon: the region over which to reduce data
    :resheader Content-Type: application/json
    """
    try:
        values = {}
        json = request.get_json()
        paramType = json.get('paramType', None)
        paramValue = json.get('paramValue', None)
        values = getStatistics(paramType, paramValue)
    except GEEException as e:
        logger.error(e.message)
        values = {
            'errMsg': e.message
        }
    return jsonify(values), 200
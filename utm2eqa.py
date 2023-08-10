#from pyproj import Proj
#from pyproj import CRS, Transformer
#import utm
from mgrs import MGRS
import configparser

#ConfigParserオブジェクトを生成
config = configparser.ConfigParser()

#設定ファイル読み込み
config.read('set_exif.ini','utf-8')

def calculate_MGRS_suffix1(mgrs_coord):
    #mgrs_coord = "53SPU7932092059"
    mgrs_obj = MGRS()
    lat_lng = mgrs_obj.toLatLon(mgrs_coord)

    latitude = lat_lng[0]
    longitude = lat_lng[1]

    print("Latitude:", latitude)
    print("Longitude:", longitude)
    return latitude,longitude

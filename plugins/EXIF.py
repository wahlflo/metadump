from PIL import Image, ExifTags
from PIL.ExifTags import TAGS


KEY_TO_CATEGORIES = dict()
KEY_TO_CATEGORIES['DateTimeOriginal'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['DateTimeDigitized'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['CreateDate'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['DateTime'] = (['time', 'modify_time'], 1)

KEY_TO_CATEGORIES['CameraOwnerName'] = (['author', 'author_name'], 1)
KEY_TO_CATEGORIES['OwnerName'] = (['author', 'author_name'], 1)
KEY_TO_CATEGORIES['XPAuthor'] = (['author'], 1)
KEY_TO_CATEGORIES['Copyright'] = (['author'], 1)
KEY_TO_CATEGORIES['Artist'] = (['author'], 1)
KEY_TO_CATEGORIES['UserComment'] = (['author', 'comment'], 1)
KEY_TO_CATEGORIES['ImageDescription'] = (['author', 'comment'], 1)

KEY_TO_CATEGORIES['Make'] = (['tool', 'hardware'], 1)
KEY_TO_CATEGORIES['Model'] = (['tool', 'hardware'], 1)
KEY_TO_CATEGORIES['SerialNumber'] = (['tool', 'hardware'], 1)
KEY_TO_CATEGORIES['BodySerialNumber'] = (['tool'], 1)
KEY_TO_CATEGORIES['CameraSerialNumber'] = (['tool', 'hardware'], 1)
KEY_TO_CATEGORIES['Software'] = (['tool', 'software'], 1)

KEY_TO_CATEGORIES['GPSInfo'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSLatitudeRef'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSLatitude'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSLongitudeRef'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSLongitude'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSAltitudeRef'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSAltitude'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:GPSTimeStamp'] = (['time'], 2)
KEY_TO_CATEGORIES['GPSInfo:Latitude'] = (['location'], 2)
KEY_TO_CATEGORIES['GPSInfo:Longitude'] = (['location'], 2)

KEY_TO_CATEGORIES['GPSInfo => Latitude'] = (['location', 'position_latitude'], 1)
KEY_TO_CATEGORIES['GPSInfo => Longitude'] = (['location', 'position_longitude'], 1)
KEY_TO_CATEGORIES['GPSInfo => Altitude'] = (['location'], 1)



class Exif_Analyser:
    def name(self):
        return 'EXIF'

    def extract_metadata(self, path_to_file: str) -> dict:
        metadata = self.__extract_metadata(path_to_file=path_to_file)
        metadata = self.__enrich_with_GPS_Information(metadata=metadata)
        metadata = [(key, metadata[key][0], metadata[key][1]) for key in metadata]
        metadata = self._enrich_with_categories(metadata=metadata)
        return metadata
    
    def __enrich_with_categories(self, metadata: dict) -> dict:
        enriched_metadata = list()
        for key, value, describtion in metadata:
            category, vlevel = KEY_TO_CATEGORIES.get(key, (list(), 3))
            enriched_metadata.append((key, value, describtion, category, vlevel))
        return enriched_metadata

    def __extract_metadata(self, path_to_file):
        try:
            image_file = Image.open(path_to_file, mode='r')
            try:
                metadata = image_file._getexif()
                metadata = self.__decode_metadata(metadata=metadata)
                return metadata
            except AttributeError:
                return list()
        except OSError:
            return list()
        
    def __decode_metadata(self, metadata: dict) -> dict:
        decoded = dict()
        for (tag, value) in metadata.items():
            decoded_key = TAGS.get(tag, tag)
            if type(value) is bytes:
                try:
                    decoded_value = value.decode('utf-8', 'ignore')
                except:
                    decoded_value = '[DECODING ERROR]'
            else:
                decoded_value = value
            decoded[decoded_key] = (decoded_value, 'embedded EXIF metadata')
        return decoded

    ############################################################################################## 
    # GPS

    def __enrich_with_GPS_Information(self, metadata: dict):
        if 'GPSInfo' in metadata:
            gps_info = self.__decode_GPSInfo(gps_info_encoded=metadata['GPSInfo'][0])
            for key, value in gps_info.items():
                metadata['GPSInfo:{0}'.format(key)] = (value, 'extracted from EXIF GPSInfo metadata')
            if self.__gps_info_contains_GPS_position(decoded_gps_info=gps_info):
                lat, lat_ref, lon, lon_ref = self.__decode_GPS_position(decoded_gps_info=gps_info)
                metadata['GPSInfo => Latitude'] = ('{0} {1}'.format(lat, lat_ref), 'extracted from EXIF GPSInfo metadata')
                metadata['GPSInfo => Longitude'] = ('{0} {1}'.format(lon, lon_ref), 'extracted from EXIF GPSInfo metadata')
            if self.__gps_info_contains_altitude(decoded_gps_info=gps_info):
                altitude, alt_ref = self.__decode_GPS_altitude(decoded_gps_info=gps_info)
                metadata['GPSInfo => Altitude'] = ('{0} meter'.format(altitude), 'extracted from EXIF GPSInfo metadata')
                metadata['GPSInfo:GPSAltitudeRef'] = ('{0}'.format(alt_ref), 'extracted from EXIF GPSInfo metadata')
        return metadata

    def __decode_GPSInfo(self, gps_info_encoded: dict):
        gps_info = dict()
        for key in gps_info_encoded.keys():
            decoded_key = ExifTags.GPSTAGS.get(key, key)
            gps_info[decoded_key] = gps_info_encoded[key]
        return gps_info

    def __gps_info_contains_GPS_position(self, decoded_gps_info: dict):
        return 'GPSLongitude' in decoded_gps_info and 'GPSLatitude' in decoded_gps_info and 'GPSLatitudeRef' in decoded_gps_info and 'GPSLongitudeRef' in decoded_gps_info
    
    def __decode_GPS_position(self, decoded_gps_info: dict):
        try:
            lat = self.__convert_degree_to_decimal(decoded_gps_info['GPSLatitude'])
            lat_ref = decoded_gps_info['GPSLatitudeRef']
            lon = self.__convert_degree_to_decimal(decoded_gps_info['GPSLongitude'])
            lon_ref = decoded_gps_info['GPSLongitudeRef']
            return lat, lat_ref, lon, lon_ref
        except:
            return None

    def __gps_info_contains_altitude(self, decoded_gps_info: dict):
        return 'GPSAltitude' in decoded_gps_info and 'GPSAltitudeRef' in decoded_gps_info 

    def __decode_GPS_altitude(self, decoded_gps_info: dict):
        altitude = float(decoded_gps_info['GPSAltitude'][0]) / float(decoded_gps_info['GPSAltitude'][1])
        if decoded_gps_info['GPSAltitudeRef'] == b'\x00':
            alt_ref = 'Above sea level'
            modifier = 1
        elif decoded_gps_info['GPSAltitudeRef'] == b'\x01':
            alt_ref = 'Below sea level'
            modifier = -1
        return altitude * modifier, alt_ref 

    def __convert_degree_to_decimal(self, value):
        degree = float(value[0][0]) / float(value[0][1])
        minutes_reference = float(value[1][1])
        seconds_reference = float(value[2][1])
        if minutes_reference == 1:
            minutes = float(value[1][0]) / minutes_reference
            seconds = float(value[2][0]) / seconds_reference
        else:
            seconds = (float(value[1][0]) / minutes_reference) % 1
            minutes = (float(value[1][0]) / minutes_reference) - seconds
            seconds *= 100
        return degree + (minutes / 60.0) + (seconds / 3600.0)
        

ANALYSER = Exif_Analyser

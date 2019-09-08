import os
from libxmp.utils import file_to_dict       # Does not work on windows machine


KEY_TO_CATEGORIES = dict()

# XMP tags
KEY_TO_CATEGORIES['xmp:CreateDate'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['xmp:MetadataDate'] = (['time'], 1)
KEY_TO_CATEGORIES['xmp:ModifyDate'] = (['time', 'modify_time'], 1)
KEY_TO_CATEGORIES['xmp:CreatorTool'] = (['tool'], 1)
KEY_TO_CATEGORIES['xmp:Author'] = (['author', 'author_name'], 1)
KEY_TO_CATEGORIES['xmp:Nickname'] = (['author'], 1)

# TIFF tags
KEY_TO_CATEGORIES['tiff:Make'] = (['tool', 'hardware'], 1)
KEY_TO_CATEGORIES['tiff:Model'] = (['tool', 'hardware'], 1)
KEY_TO_CATEGORIES['tiff:Artist'] = (['author'], 1)
KEY_TO_CATEGORIES['tiff:DateTime'] = (['time'], 1)
KEY_TO_CATEGORIES['tiff:Software'] = (['tool', 'software'], 1)

# EXIF tags
KEY_TO_CATEGORIES['exif:DateTimeDigitized'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['exif:DateTimeOriginal'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['exif:UserComment'] = (['author'], 1)
KEY_TO_CATEGORIES['exif:GPSAltitude'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSAltitudeRef'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSAreaInformation'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDestBearing'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDestBearingRef'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDestDistance'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDestDistanceRef'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDestLatitude'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDestLongitude'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDifferential'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSLatitude'] = (['location', 'position_latitude'], 1)
KEY_TO_CATEGORIES['exif:GPSLongitude'] = (['location', 'position_longitude'], 1)
KEY_TO_CATEGORIES['exif:GPSSpeed'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSSpeedRef'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSStatus'] = (['location'], 1)
KEY_TO_CATEGORIES['exif:GPSDateTime'] = (['time'], 1)
KEY_TO_CATEGORIES['exif:GPSTimeStamp'] = (['time'], 1)

# Photoshop tags
KEY_TO_CATEGORIES['photoshop:AuthorsPosition'] = (['author'], 1)
KEY_TO_CATEGORIES['photoshop:CaptionWriter'] = (['author'], 1)
KEY_TO_CATEGORIES['photoshop:City'] = (['location'], 1)
KEY_TO_CATEGORIES['photoshop:Country'] = (['location'], 1)
KEY_TO_CATEGORIES['photoshop:Credit'] = (['author'], 1)
KEY_TO_CATEGORIES['photoshop:DateCreated'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['photoshop:Credit'] = (['author'], 1)
KEY_TO_CATEGORIES['photoshop:History'] = (['author', 'time'], 1)
KEY_TO_CATEGORIES['photoshop:Source'] = (['author'], 1)


class XMP_Analyser:
    def name(self):
        return 'XMP'

    def extract_metadata(self, path_to_file: str) -> dict:
        if os.name == 'nt':  
            return list()
        metadata = self.__extract_metadata(path_to_file=path_to_file)
        metadata = self.__enrich_with_categories(metadata=metadata)
        return metadata
    
    def __enrich_with_categories(self, metadata: dict) -> dict:
        enriched_metadata = list()
        for key, value, describtion in metadata:
            category, vlevel = KEY_TO_CATEGORIES.get(key, (list(), 3))
            enriched_metadata.append((key, value, describtion, category, vlevel))
        return enriched_metadata

    def __extract_metadata(self, path_to_file):
        try:
            xmp_meta_data = file_to_dict(path_to_file)
            meta_data_entries = list()
            for level_1_key in xmp_meta_data.keys():
                for key, value, parameters in xmp_meta_data[level_1_key]:
                    meta_data_entries.append((key, value, 'embedded XMP metadata'))
            return meta_data_entries
        except libxmp.ExempliLoadError:
            return list()


ANALYSER = XMP_Analyser
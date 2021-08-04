import zipfile
import lxml.etree


KEY_TO_CATEGORIES = dict()
KEY_TO_CATEGORIES['lastPrinted'] = (['time'], 1)
KEY_TO_CATEGORIES['created'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['modified'] = (['time', 'modify_time'], 1)

KEY_TO_CATEGORIES['Application'] = (['tool', 'software'], 1)
KEY_TO_CATEGORIES['AppVersion'] = (['tool', 'software'], 1)

KEY_TO_CATEGORIES['lastModifiedBy'] = (['author', 'author_name'], 1)
KEY_TO_CATEGORIES['creator'] = (['author', 'author_name'], 1)
KEY_TO_CATEGORIES['Company'] = (['author'], 1)


class Office_Analyser:
    def name(self):
        return 'Office'

    def extract_metadata(self, path_to_file: str) -> dict:
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
        if zipfile.is_zipfile(path_to_file):
            try:
                zip_file = zipfile.ZipFile(path_to_file)
                meta_data_from_core = self.__meta_data_from_core(zip_file=zip_file)
                meta_data_from_app = self.__meta_data_from_app(zip_file=zip_file)
                return meta_data_from_core + meta_data_from_app
            except zipfile.BadZipFile:
                return list()
        return list()

    def __meta_data_from_core(self, zip_file):
        meta_data = list()
        try:
            meta_data_as_xml = lxml.etree.fromstring(zip_file.read('docProps/core.xml'))    
        except KeyError:
            return meta_data   # No file docProps/core.xml
        
        for child in meta_data_as_xml.iterchildren():
            if child.text == None:
                text = ''
            else:
                text = child.text
            tag = Office_Analyser.__get_purified_tag(child)
            meta_data.append((tag, text, 'Microsoft Office - docProps/core.xml'))
        return meta_data

    def __meta_data_from_app(self, zip_file):
        meta_data = list()
        try:
            meta_data_as_xml = lxml.etree.fromstring(zip_file.read('docProps/app.xml'))    
        except KeyError:
            return meta_data   # No file docProps/app.xml
        
        for child in meta_data_as_xml.iterchildren():
            if child.text == None:
                text = ''
            else:
                text = child.text
            tag = Office_Analyser.__get_purified_tag(child)
            meta_data.append((tag, text, 'Microsoft Office - docProps/app.xml'))
        return meta_data

    @staticmethod
    def __get_purified_tag(element):
        tag = element.tag
        tag = tag.replace('{' + str(element.nsmap[element.prefix]) + '}', '')
        return tag  


ANALYSER = Office_Analyser
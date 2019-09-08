import PyPDF2


KEY_TO_CATEGORIES = dict()
KEY_TO_CATEGORIES['/Author'] = (['author', 'author_name'], 1)
KEY_TO_CATEGORIES['/Producer'] = (['author', 'author_name', 'tool', 'software'], 1)
KEY_TO_CATEGORIES['/CreationDate'] = (['time', 'creation_time'], 1)
KEY_TO_CATEGORIES['/ModDate'] = (['time', 'modify_time'], 1)


class PDF_Analyser:
    def name(self):
        return 'PDF'

    def extract_metadata(self, path_to_file: str) -> dict:
        metadata = self.__extract_metadata(path_to_pdf=path_to_file)
        metadata = self.__enrich_with_categories(metadata=metadata)
        return metadata

    def __enrich_with_categories(self, metadata: dict) -> dict:
        enriched_metadata = list()
        for key, value, describtion in metadata:
            category, vlevel = KEY_TO_CATEGORIES.get(key, (list(), 3))
            enriched_metadata.append((key, value, describtion, category, vlevel))
        return enriched_metadata

    def __extract_metadata(self, path_to_pdf: str) -> dict:
        try:
            with open(path_to_pdf, mode='rb') as file_stream:
                pdf_file = PyPDF2.PdfFileReader(file_stream, strict=False)

                meta_data = pdf_file.getDocumentInfo() 
                return [(key, meta_data[key], 'embedded PDF metadata') for key in meta_data]
        except PyPDF2.utils.PdfReadError:
            return list()
        except OSError:
            return list()


ANALYSER = PDF_Analyser
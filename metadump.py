#!/usr/bin/env python

__description__ = 'Metadata dump utility'
__author__ = 'Florian Wahl'
__version__ = '1.0.0'
__date__ = '2019/03/17'


import os
import importlib.util
from datetime import datetime
import argparse
import sys

BANNER_TEXT = """    __  ___     __            __                    
   /  |/  /__  / /_____ _____/ /_  ______ ___  ____ 
  / /|_/ / _ \/ __/ __ `/ __  / / / / __ `__ \/ __ \\
 / /  / /  __/ /_/ /_/ / /_/ / /_/ / / / / / / /_/ /
/_/  /_/\___/\__/\__,_/\__,_/\__,_/_/ /_/ /_/ .___/ 
by Florian Wahl                            /_/     

"""

VERSION_INFO = """version: {0} from {1}
developed by: {2}
""".format(__version__, __date__, __author__)

FILTER_OPTIONS = """You can pass names of categories after the --filter option. Then only metadata from these categories will be printed out.
The categories are structured in a tree:

|--time
|   |-- creation_time
|   |-- modify_time
|
|-- author
|   |-- author_name
|   |-- comment
|
|-- tool
|   |-- hardware
|   |-- software
|
|--location
    |-- position_latitude
    |-- position_longitude


Examples:
'python3 metadump.py -i INPUT -f time'                      Shows only timestamps 
'python3 metadump.py -i INPUT -f location author_name'      Shows only information about the location and the name of the author

"""

MAIN_CATEGORIES = ['time', 'author', 'tool', 'location']

UNICODE_SUPPORT = sys.stdout.encoding.lower().startswith('utf')

######################################################################################
# helper classes and functions
class VAction(argparse.Action):
    """
    For parsing the verbosity level
    """
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        super(VAction, self).__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)
        self.values = 0

    def __call__(self, parser, args, values, option_string=None):
        if values is None:
            self.values += 1
        else:
            try:
                self.values = int(values)
            except ValueError:
                self.values = values.count('v')+1
        setattr(args, self.dest, self.values)


def __filter_for_category(metadata, categories: list):
    filtered_metadata = list()
    for key, value, description, category, vlevel in metadata:
        filter_passed = False
        for cat in category:
            if cat in categories:
                filter_passed = True
                break
        if filter_passed:
            filtered_metadata.append((key, value, description, category, vlevel))
    return filtered_metadata


def __parse_date_string(date_string):
    datetime_formats = ['%Y:%m:%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    for datetime_format in datetime_formats:
        try:
            return datetime.strptime(date_string, datetime_format)
        except ValueError:
            pass
    return None


def __convert_gps_specification(gps_coordinate: str):
    reference_direction = __extract_gps_reference_direction(gps_coordinate=gps_coordinate)
    if reference_direction is None:
        print('reference_direction')
        return None
    gps_coordinate = gps_coordinate.replace(reference_direction, '').strip()
    if ',' in gps_coordinate and '.' in gps_coordinate: # in degree format
        try:
            degree = int(gps_coordinate.split(',')[0])
            minutes = int(gps_coordinate.split(',')[1].split('.')[0])
            seconds = int(gps_coordinate.split(',')[1].split('.')[1])
            gps_coordinate =  degree + (minutes / 60.0) + (seconds / 3600.0)
        except Exception as e:
            print(e)
            return None
    else:  # in decimal format
        try:
            gps_coordinate = float(gps_coordinate)
        except:
            return None
    return gps_coordinate, reference_direction
    

def __extract_gps_reference_direction(gps_coordinate: str):
    directions = ['N', 'E', 'W', 'S']
    for direction in directions:
        if direction in gps_coordinate:
            return direction


######################################################################################
# load plugins dynamically
def __load_plugins():
    path_to_plugins = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'plugins'
    plugin_files = list()
    for file_path in os.listdir(path_to_plugins):
        if os.path.isfile(path_to_plugins + os.sep + file_path) and file_path.endswith('.py'):
            plugin_files.append(path_to_plugins + os.sep + file_path)

    plugins = list()
    for counter, plugin_file in enumerate(plugin_files):
        specification = importlib.util.spec_from_file_location(name='plugin_{}'.format(counter), location=plugin_file)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        plugins.append(module.ANALYSER())
    return plugins

PLUGINS = __load_plugins()


######################################################################################
# functions which can be imported by other scripts

def extract_metadata_of_file(path_to_file, specified_plugins=None):
    """
    extracts all metadata of a file using the specified plugins
    :param path_to_file: path to the file which should be parsed
    """
    metadata = list()
    for plugin in PLUGINS:
        if specified_plugins != None and plugin.name() not in specified_plugins:
            continue
        metadata += plugin.extract_metadata(path_to_file)
    return metadata


def get_creation_date(metadata: list):
    filtered_metadata = __filter_for_category(metadata=metadata, categories=['creation_time'])
    metadata_values = [x[1] for x in filtered_metadata]
    parsed_dates = [__parse_date_string(x) for x in metadata_values]
    parsed_dates = [x for x in parsed_dates if x is not None]
    if len(parsed_dates) == 0:
        return None    
    return parsed_dates.pop()


def get_modify_date(metadata: list):
    filtered_metadata = __filter_for_category(metadata=metadata, categories=['modify_time'])
    metadata_values = [x[1] for x in filtered_metadata]
    parsed_dates = [__parse_date_string(x) for x in metadata_values]
    parsed_dates = [x for x in parsed_dates if x is not None]
    if len(parsed_dates) == 0:
        return None    
    return parsed_dates.pop()


def get_GPS_coordinates(metadata: list):
    latitude_filtered = __filter_for_category(metadata=metadata, categories=['position_latitude'])
    longitude_filtered = __filter_for_category(metadata=metadata, categories=['position_longitude'])
    latitude_values = [x[1] for x in latitude_filtered if x[1] != '']
    longitude_values = [x[1] for x in longitude_filtered if x[1] != '']
    converted_lat = [__convert_gps_specification(x) for x in latitude_values]
    converted_lon = [__convert_gps_specification(x) for x in longitude_values]
    converted_lat = [x for x in converted_lat if x is not None]
    converted_lon = [x for x in converted_lon if x is not None]
    if len(converted_lat) == 0 or len(converted_lon) == 0:
        return None
    lat, lat_ref = converted_lat.pop()
    lon, lon_ref = converted_lon.pop()
    return lat, lat_ref, lon, lon_ref


def get_author_name(metadata: list):
    filtered_metadata = __filter_for_category(metadata=metadata, categories=['author_name'])
    metadata_values = [x[1] for x in filtered_metadata if x[1] != '']
    if len(metadata_values) == 0:
        return None
    return '; '.join(metadata_values)


######################################################################################
# main program
def __progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=70):
    if UNICODE_SUPPORT:
        fill = '█'
    else:
        fill = '#'
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line when its complete
    if iteration == total: 
        print()


def __extract_metadata_of_list_of_files(file_paths: list, path_to_input, arguments):
    extracted = list()
    total_number_of_files = len(file_paths)
    __progress_bar(iteration=0, total=total_number_of_files, prefix='Analysing Files:', suffix='', decimals=2)
    for index, path_to_file in enumerate(file_paths):
        metadata = extract_metadata_of_file(path_to_file=path_to_file, specified_plugins=arguments.plugins)
        extracted.append((path_to_file, metadata))
        __progress_bar(iteration=index+1, total=total_number_of_files, prefix='Analysing Files:', suffix='', decimals=2)
    print()
    return extracted


def __preprocess_extracted_metadata(arguments, metadata):
    # filter verbosity level 
    filtered_metadata = list()
    for key, value, description, category, vlevel in metadata:
        value = str(value)
        if vlevel > arguments.verbose:
            continue
        if arguments.verbose < 3:
            if value == '':
                continue
        filtered_metadata.append((str(key), value, description, category, vlevel))
    metadata = filtered_metadata

    # applies filter
    if arguments.filter != None:
        metadata = __filter_for_category(metadata=metadata, categories=arguments.filter)

    # applies value length limit 
    if arguments.limit is not None:
        metadata = [(key, value[:arguments.limit], description, category, vlevel) for (key, value, description, category, vlevel) in metadata]

    return metadata


def __display_result(arguments, metadata_of_files, path_to_input, display_part_of_stream=False):
    # filter empty files
    if not arguments.showemptyfiles: 
        metadata_of_files = [(file_path, metadata) for file_path, metadata in metadata_of_files if len(metadata) > 0]

    # shorten the file paths
    metadata_of_files = [(file_path.replace(path_to_input, ''), metadata) for file_path, metadata in metadata_of_files]

    if len(metadata_of_files) == 0 and not display_part_of_stream:
        print('No metadata found')
        return None
   
    # printing parameters
    key_max = 0
    value_max = 0
    description_max = 0
    for _, data in metadata_of_files:
        for key, value, description, _, _ in data:
            key_max = max(key_max, len(key))
            value_max = max(value_max, len(value))
            description_max = max(description_max, len(description))
        
    for file_name, metadata in metadata_of_files:
        print(100*'=')
        print('File: {}'.format(file_name))
        if len(metadata) == 0:
            print('\tNo metadata found\n')
            continue

        if arguments.order:
            metadata = sorted(metadata, key=lambda x: x[3])
            categories = MAIN_CATEGORIES + ['other']
            sorted_metadata = {x: list() for x in categories}
            for key, value, description, category, vlevel in metadata:
                found = False
                for cat in category:
                    if cat in sorted_metadata:
                        sorted_metadata[cat].append((key, value, description, category, vlevel))
                        found = True
                if not found:
                    sorted_metadata['other'].append((key, value, description, category, vlevel))
            for cat in categories:
                data = sorted_metadata[cat]
                if len(data) == 0:
                    continue
                print('\tCATEGORY: {0}'.format(cat.upper()))

                __print_meta_data(key_max=key_max, value_max=value_max, description_max=description_max, indentation=2, metadata=data, arguments=arguments)
                print()
        else:
            __print_meta_data(key_max=key_max, value_max=value_max, description_max=description_max, indentation=1, metadata=metadata, arguments=arguments)
            print()
        

def __print_meta_data(key_max, value_max, description_max, indentation, metadata, arguments):
    spacing = 3
    print()
    if arguments.printcategories:
        print(indentation*'\t', 'KEY'.ljust(key_max + spacing) + '|   ' + 'VALUE'.ljust(value_max + spacing) + '|   ' + 'DESCRIPTION'.ljust(description_max + spacing) + '|   CATEGORIES')
        print(indentation*'\t', (key_max + value_max + description_max+29)*'-')    
    else:
        print(indentation*'\t', 'KEY'.ljust(key_max + spacing) + '|   ' + 'VALUE'.ljust(value_max + spacing) + '|   ' + 'DESCRIPTION')
        print(indentation*'\t', (key_max + value_max + description_max+9)*'-')  
    for key, value, description, category, _ in metadata: 
        key = str(key)
        value = str(value)
        description = str(description)
        try:
            if arguments.printcategories:
                cat = ', '.join(category)
                print(indentation*'\t', key.ljust(key_max + spacing) + '|   ' + value.ljust(value_max + spacing) + '|   ' + description.ljust(description_max + spacing) + '|   ' + cat)
            else:
                print(indentation*'\t', key.ljust(key_max + spacing) + '|   ' + value.ljust(value_max + spacing) + '|   ' + description)
        except:
            print(indentation*'\t', '  ----  Encoding ERROR  ----- ')


if __name__ == '__main__':
    print(BANNER_TEXT)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="Path to the file or directory which should be analysed", type=str)    
    parser.add_argument('-f', '--filter', nargs='+', default=None, help="Filter metadata for special kategory")
    parser.add_argument('--filteroptions', action='store_true', help="Shows options for filtering extracted metadata")
    parser.add_argument('--version', action='store_true', help="Shows version of metadump")
    parser.add_argument('-v', nargs='?', action=VAction, default=1, dest='verbose', help="Defines verbosity level [-v, -vv, -vvv, -vvv]")
    parser.add_argument('-l', '--limit', type=int, default=30, help="Maximal characters of metadata value")
    parser.add_argument('-o', '--order', action='store_true', default=False, help="Order key-value pairs by their category")
    parser.add_argument('-r', '--recursive', action='store_true', default=False, help="If the input is a path to a directory this flag will metadump seleact all files in this directory and subdirectories recursive")
    parser.add_argument('-c', '--printcategories', action='store_true', default=False, help="Will print the categories of the extracted metadata")
    parser.add_argument('-s', '--stream', action='store_true', default=False, help="When a file is analysed the results will be printed directly")
    parser.add_argument('--showplugins', action='store_true', default=False, help="Prints all loaded plugins")
    parser.add_argument('-p', '--plugins', nargs='+', default=None, help="Only use the specified Plugins")
    parser.add_argument('--showemptyfiles', action='store_true', default=False, help="Prints a file although no metadata could be extracted")
    
    arguments = parser.parse_args()
    
    if arguments.filteroptions:
        print(FILTER_OPTIONS)
        exit()

    if arguments.version:
        print(VERSION_INFO)
        exit()

    if arguments.showplugins:
        print('Loaded Plugins:')
        for plugin in PLUGINS:
            print('\t', plugin.name())
        exit()

    # check that input is valid
    if arguments.input == None:
        print('ERROR: Path to input must be set\n')
        parser.print_help()
        exit()

    path_to_input = os.path.abspath(arguments.input)

    if not os.path.exists(path_to_input):
        print('ERROR: Path "{}" does not exist\n'.format(path_to_input))
        exit()

    # gather absolute paths to the files which should be scanned
    input_list = list()
    if os.path.isdir(path_to_input):
        directory_queue = [path_to_input]
        while len(directory_queue) > 0:
            path_to_dir = directory_queue.pop(0)
            for file_path in os.listdir(path_to_dir):
                file_path = os.path.join(path_to_dir, file_path)
                if os.path.isdir(file_path):
                    if arguments.recursive:
                        directory_queue.append(file_path)
                else:
                    input_list.append(file_path)
    else:
        input_list.append(path_to_input)
    
    if len(input_list) == 0:
        print('no files found')
        exit()
    
    try:
        if arguments.stream:
            for path_to_file in input_list:
                extract_metadata = extract_metadata_of_file(path_to_file=path_to_file, specified_plugins=arguments.plugins)
                metadata_of_files = [(path_to_file, extract_metadata)]
                # preprocess the extracted metadata
                metadata_of_files = [ (path_to_file, __preprocess_extracted_metadata(arguments=arguments, metadata=metadata)) for path_to_file, metadata in metadata_of_files]
                # display metadata
                __display_result(arguments, metadata_of_files=metadata_of_files, path_to_input=path_to_input, display_part_of_stream=True)
        else:
            metadata_of_files = __extract_metadata_of_list_of_files(file_paths=input_list, path_to_input=path_to_input, arguments=arguments)
            # preprocess the extracted metadata
            metadata_of_files = [ (path_to_file, __preprocess_extracted_metadata(arguments=arguments, metadata=metadata)) for path_to_file, metadata in metadata_of_files]
            # display metadata
            __display_result(arguments, metadata_of_files=metadata_of_files, path_to_input=path_to_input)
    except KeyboardInterrupt:
        print()
        print('Keyboard Interrupt: Stopping search')

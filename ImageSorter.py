"""
###----------------------------------------------------------------------------------------------###
###     Program: ImageSorter.py                                                                  ###
###   Developer: A.Dubz                                                                          ###
### Description: Script to sort images with metadata into dated folders                          ###
###  Python Ver: 3.6.3                                                                           ###
###     Created: 2017-03-25                                                                      ###
###     Modules: exifRead                                                                        ###
###----------------------------------------------------------------------------------------------###
"""

# Standard Library
import argparse
import os
import json
import logging
import imghdr
from sys import exit
from platform import system
from shutil import copy2, move
from datetime import datetime

# Third-party Modules
import exifread

CONFIG_FILE = 'configs.json'


def run_sorter(args):
    """
    Run sorter with args options

    :param args: Args passed into script
    """

    images = scan_images(args['dir'])

    copy_to_new_paths(images, args)

def scan_images(dirpath):
    """
    Scan images from specified directory

    :param dirpath (str): directory that contains the files. Absolute or relative paths can be used
    :return (list<dict()>):  List of image dictionaries. { filename=(str), date=(date) }.
    """
    images_data = []

    for root, _, files in os.walk(dirpath):
        for name in files:
            fpath = os.path.join(root, name)

            if imghdr.what(fpath):
                try:
                    file = open(fpath, 'rb')
                    tags = exifread.process_file(file)

                    if 'Image DateTime' in tags:
                        date = str(tags['Image DateTime'])
                    elif 'EXIF DateTimeOriginal' in tags:
                        date = str(tags['EXIF DateTimeOriginal'])
                    else:
                        date = None

                    images_data.append(dict(
                        filename=name,
                        path=fpath,
                        date=date
                    ))
                finally:
                    file.close()

    return images_data

def copy_to_new_paths(images, args):
    """
    Copy images to new dated folders

    :param images (list<dict()>): List of image dictionaries. { filename=(str), path=(str),
                                 date=(str) }
    :param depth (str): Folder date depth
    """
    sorted_dir = 'images_sorted'
    depth = args['depth']

    if not os.path.exists(sorted_dir):
        os.mkdir(sorted_dir)

    for image in images:
        # Exif Date format: 2016:10:03 18:49:30
        if image['date']:
            date = datetime.strptime(image['date'], '%Y:%m:%d %H:%M:%S')

            if depth == 'year':
                new_path = os.path.join(sorted_dir, str(date.year))

            elif depth == 'month':
                new_path = os.path.join(sorted_dir, str(date.year), date.strftime('%B'))

            elif depth == 'day':
                new_path = os.path.join(sorted_dir, str(date.year), date.strftime('%B'),
                                        date.strftime('%d_%a'))
        else:
            new_path = os.path.join(sorted_dir, 'Unknown_date')

        if not os.path.exists(new_path):
            os.makedirs(new_path, exist_ok=True)

        if args['move']:
            dest = move(image['path'], new_path, copy2)
        else:
            dest = copy2(image['path'], new_path)

        logging.info(f'{image["filename"]} copied from \'{image["path"]}\' --> \'{dest}\'')

# -----------------------------------------Main function------------------------------------------ #

def main():
    """
    Main
    """
    parser = argparse.ArgumentParser(description='Script to organize images into respective '
                                                 'folders by dates')
    parser.add_argument('dir',
                        nargs=1,
                        help='Directory where the image files are stored')
    parser.add_argument('-d',
                        '--depth',
                        default='month',
                        choices=['year', 'month', 'day'],
                        help='Folder date depth. Default: \'month\'. Example: 2017/March/foo.jpg')
    parser.add_argument('-m',
                        '--move',
                        action='store_true',
                        help='Move files in the images dir to new dir instead of copying')
    parser.add_argument('-l',
                        '--log',
                        action='store_true',
                        help='Log the process in log file, otherwise to console')

    args = vars(parser.parse_args())

    # Verify if directory exists
    args['dir'] = args['dir'][0]
    if not os.path.isdir(args['dir']):
        print('Directory does not exist. Exiting...')
        exit()

    cwd = os.getcwd()
    try:
        with open(f'{cwd}/{CONFIG_FILE}', 'r') as file:
            data = file.read().replace('\n', '')

        configs = json.loads(data)
    except OSError:
        print(f'Error opening config file. Error: {OSError}')

    if args['log']:
        logging.basicConfig(filename='report.log',
                            filemode='w',
                            level=logging.INFO,
                            format='%(message)s')

    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(message)s')

    logging.info(configs['reportHead'])

    start = datetime.now()
    logging.info(f'Report started at: {start.strftime(configs["timeFormat"])}')

    # Main entry
    run_sorter(args)

    end = datetime.now()
    logging.info(f'Report ended at: {end.strftime(configs["timeFormat"])}')

    diff = end - start
    mins, secs = divmod(diff.days * 86400 + diff.seconds, 60)

    logging.info(f'Total run time: {mins} minutes, {secs} seconds')
    logging.info(configs['reportFoot'])

if __name__ == '__main__':
    main()

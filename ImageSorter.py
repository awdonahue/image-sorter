"""
###----------------------------------------------------------------------------------------------###
###     Program: ImageSorter.py                                                                  ###
###   Developer: A.Dubz                                                                          ###
### Description: Script to sort images with metadata into dated folders                          ###
###  Python Ver: 3.6.3                                                                           ###
###     Created: 2017-03-25                                                                      ###
###     Modules: exifRead                                                                        ###
###----------------------------------------------------------------------------------------------###
###                                     Modification Log                                         ###
###  Date        Name       Details                                                              ###
###  ---------   --------   ---------------------------------------------------------------------###
###                                                                                              ###
###----------------------------------------------------------------------------------------------###
"""
# Standard Library
import argparse
import os
import sys
import json
import logging
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
    try:
        entries = os.scandir(dirpath)
    except OSError:
        print('Error finding dir: %s', dirpath)
        input('Press enter to exit...')
        sys.exit()

    images_data = []
    for entry in entries:
        date = None

        # TODO do an os.walk to find images
        # TODO import config imageFormat list and check each

        if not entry.name.startswith('.') and entry.is_file():
            file = open(entry.path, 'rb')
            tags = exifread.process_file(file)
            file.close()

            for tag in tags:
                if tag in ('Image DateTime', 'EXIF DateTimeOriginal'):
                    date = str(tags[tag])
                    break

            images_data.append(dict(
                filename=entry.name,
                path=entry.path,
                date=date
                size=entry.size
            ))

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
        date = datetime.strptime(image['date'], '%Y:%m:%d %H:%M:%S')

        if depth == 'year':
            new_path = os.path.join(sorted_dir, str(date.year))

        elif depth == 'month':
            new_path = os.path.join(sorted_dir, str(date.year), date.strftime('%B'))

        elif depth == 'day':
            new_path = os.path.join(sorted_dir, str(date.year), date.strftime('%B'),
                                    date.strftime('%d_%a'))
        else:
            new_path = sorted_dir

        if not os.path.exists(new_path):
            os.makedirs(new_path, exist_ok=True)

        if args['move']:
            dest = move(image['path'], new_path, copy2)
        else:
            dest = copy2(image['path'], new_path)

        logging.info('%s copied from \'%s\' --> \'%s\'', image['filename'], image['path'], dest)

# -----------------------------------------Main function------------------------------------------ #

def main():
    """
    Main
    """
    parser = argparse.ArgumentParser(description='Script to organize images into respective '
                                                 'folders by dates')
    parser.add_argument('dir',
                        nargs='?',
                        default='images',
                        help='Directory where the image files are stored. Default: \'images\'')
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

    run_sorter(args)

    end = datetime.now()
    logging.info(f'Report ended at: {end.strftime(configs["timeFormat"])}')

    diff = end - start
    mins, secs = divmod(diff.days * 86400 + diff.seconds, 60)

    logging.info(f'Total run time: {mins} minutes, {secs} seconds')
    logging.info(configs['reportFoot'])

if __name__ == '__main__':
    main()

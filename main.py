from lib.pdflib import *
import time
import configparser
import logging

if __name__ == '__main__':

    # Load the config file
    config = configparser.ConfigParser()
    config.read('settings.ini')
    include_shipping_list = config["SHIPPING LISTS"].getboolean('Process')
    rotate_labels = config["PRINTER"].getboolean('Rotate')

    # Open the log file
    logging.basicConfig(filename='info.log', filemode='a', format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create the output folder if it doesn't exists
    os.makedirs('archive', exist_ok=True)
    os.makedirs('archive/labels', exist_ok=True)
    os.makedirs('archive/lists', exist_ok=True)
    os.makedirs('archive/originals', exist_ok=True)
    os.makedirs('pdfs', exist_ok=True)

    while True:
        process_files(include_shipping_list, rotate_labels)
        # Check for new files every .5 secs.
        time.sleep(.500)

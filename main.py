import configparser

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from lib.pdflib import *


def wait_for_file_to_finish_copy(filename: str):
    copy_finished = False
    print("Waiting for file to finish copying...")
    while not copy_finished:
        old_size = os.path.getsize(filename)
        time.sleep(0.3)
        if os.path.getsize(filename) == old_size:
            copy_finished = True
    return


class PDFHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Process every pdf in the watch folder.
        for filename in os.listdir('./pdfs'):
            if filename.endswith('.pdf'):
                wait_for_file_to_finish_copy('pdfs/' + filename)
                process_files(filename, include_shipping_list, rotate_labels, printer_name)
            else:
                continue


if __name__ == '__main__':
    print("Starting pdf2zebra...")
    # Load the config file
    print("Loading settings...")
    config = configparser.ConfigParser()
    config.read('settings.ini')
    include_shipping_list = config["SHIPPING LISTS"].getboolean('Process')
    rotate_labels = config["PRINTER"].getboolean('Rotate')
    printer_name = config["PRINTER"]['Printer Name']

    # Open the log file
    print("Open logging file...")
    logging.basicConfig(filename='info.log', filemode='a', format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create the output folder if it doesn't exists
    print("Creating necessary folders...")
    os.makedirs('archive', exist_ok=True)
    os.makedirs('archive/labels', exist_ok=True)
    os.makedirs('archive/lists', exist_ok=True)
    os.makedirs('archive/originals', exist_ok=True)
    os.makedirs('archive/modified_labels', exist_ok=True)
    os.makedirs('pdfs', exist_ok=True)

    print("Creating event handler...")
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler=event_handler, path='./pdfs', recursive=True)
    print("Starting file observer on PDFs folder...")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

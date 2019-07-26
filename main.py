from lib.label_helper import *
import os
import webbrowser
import platform
import configparser
import logging

if __name__ == '__main__':

    # Load the config file
    config = configparser.ConfigParser()
    config.read('settings.ini')
    include_correo_argentino = config["CORREO ARGENTINO LIST"].getboolean('Thermal')
    rotate_labels = config["PRINTER"].getboolean('Rotate')

    # Open the log file
    logging.basicConfig(filename='log.log', filemode='a', format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create the output folder if it doesn't exists
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/labels', exist_ok=True)
    os.makedirs('output/lists', exist_ok=True)

    # Create the temporary work folder. (WE DONT NEED THIS FOR NOW)
    # os.makedirs('tmp', exist_ok=True)
    # Create the new output file for the labels
    output = PyPDF2.PdfFileWriter()

    # Check if pdfs folder contains no pdf files.
    empty_folder = True
    for pdf_file in os.listdir('./pdfs'):
        if pdf_file.endswith(".pdf"):
            empty_folder = False
    if empty_folder:
        # os.rmdir("tmp")
        exit()
        logging.info("No pdf file found!")

    # Get which OS it's running on for the correct browser path.
    running_os = platform.system()
    if running_os == "Linux":
        chrome_path = '/usr/bin/google-chrome %s'
    if running_os == "Windows":
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    if running_os == "Darwin":
        chrome_path = "open -a /Applications/Google\ Chrome.app %s"

    # Create an individual pdf for every file in the "pdfs" folder.
    for pdf_file in os.listdir('./pdfs'):
        # Ignore hidden files in UNIX systems. (I'm looking at you macOS)
        if pdf_file.startswith(".") is True:
            continue
        # Ignore non-PDF files.
        if not pdf_file.endswith(".pdf"):
            continue
        with open('pdfs/{0}'.format(pdf_file), 'rb') as file:
            logging.info("Processing %s", pdf_file)
            # Open the pdf document.
            pdf = PyPDF2.PdfFileReader(file)
            # Get amount of pages.
            amount_of_pages = pdf.getNumPages()
            # If we want to separate the Correo Argentino labels, we save an index.
            if not include_correo_argentino:
                correo_argentino_index = []
            for index in range(amount_of_pages):
                #  Check type of page.
                page_type = delivery_type(pdf.pages[index])
                if page_type["type"] == "Loginter":
                    # Create a page for every sticker.
                    # Copy the ith page to  first_ticket.
                    first_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    # Crop the first ticket of the page.
                    first_ticket.cropBox.lowerLeft = (22, 750)
                    first_ticket.cropBox.upperRight = (202, 465)
                    if rotate_labels:
                        first_ticket = first_ticket.rotateClockwise(90)
                    output.addPage(first_ticket)

                    # Repeat for every ticket of the page.
                    if page_type["amount"] > 1:
                        second_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        second_ticket.cropBox.lowerLeft = (208, 750)
                        second_ticket.cropBox.upperRight = (388, 465)
                        if rotate_labels:
                            second_ticket = second_ticket.rotateClockwise(90)
                        output.addPage(second_ticket)

                    if page_type["amount"] > 2:
                        third_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        third_ticket.cropBox.lowerLeft = (394, 750)
                        third_ticket.cropBox.upperRight = (574, 465)
                        if rotate_labels:
                            third_ticket = third_ticket.rotateClockwise(90)
                        output.addPage(third_ticket)

                    if page_type["amount"] > 3:
                        fourth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        fourth_ticket.cropBox.lowerLeft = (22, 390)
                        fourth_ticket.cropBox.upperRight = (202, 105)
                        if rotate_labels:
                            fourth_ticket = fourth_ticket.rotateClockwise(90)
                        output.addPage(fourth_ticket)

                    if page_type["amount"] > 4:
                        fifth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        fifth_ticket.cropBox.lowerLeft = (208, 390)
                        fifth_ticket.cropBox.upperRight = (388, 105)
                        if rotate_labels:
                            fifth_ticket = fifth_ticket.rotateClockwise(90)
                        output.addPage(fifth_ticket)

                    if page_type["amount"] > 5:
                        sixth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        sixth_ticket.cropBox.lowerLeft = (394, 390)
                        sixth_ticket.cropBox.upperRight = (574, 105)
                        if rotate_labels:
                            sixth_ticket = sixth_ticket.rotateClockwise(90)
                        output.addPage(sixth_ticket)

                if page_type["type"] == "Flex":
                    first_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    first_ticket.cropBox.lowerLeft = (45, 90)
                    first_ticket.cropBox.upperRight = (270, 500)
                    if rotate_labels:
                        first_ticket = first_ticket.rotateClockwise(90)
                    output.addPage(first_ticket)
                    if page_type["amount"] > 1:
                        second_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        second_ticket.cropBox.lowerLeft = (320, 90)
                        second_ticket.cropBox.upperRight = (545, 500)
                        if rotate_labels:
                            second_ticket = second_ticket.rotateClockwise(90)
                        output.addPage(second_ticket)
                    if page_type["amount"] > 2:
                        third_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        third_ticket.cropBox.lowerLeft = (590, 90)
                        third_ticket.cropBox.upperRight = (815, 500)
                        if rotate_labels:
                            third_ticket = third_ticket.rotateClockwise(90)
                        output.addPage(third_ticket)

                if page_type["type"] == "Correo Argentino List" or page_type["type"] == "Correo Argentino":
                    if include_correo_argentino:
                        output.addPage(PyPDF2.PdfFileReader(file).getPage(index))
                    else:
                        correo_argentino_index.append(index)
            output_labels_exists = False
            # Write the processed pdf file.
            if output.getNumPages() > 0:
                output_labels_exists = True
                output_filename = 'output/labels/{0}.pdf'.format(datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
                with open(output_filename, 'wb') as output_file:
                    output.write(output_file)
                    logging.info("Saved the new labels in %s", output_filename)
            correo_argentino_filename = None
            if not include_correo_argentino:
                if len(correo_argentino_index) > 0:
                    correo_argentino_filename = save_correo_argentino_pages(PyPDF2.PdfFileReader(file),
                                                                            correo_argentino_index)
                    logging.info("Saved the new Correo Argentino pages in %s", correo_argentino_filename)
            file.close()
            # Delete the original pdf.
            os.unlink('pdfs/{0}'.format(pdf_file))

    # Delete the temporary folder.
    # os.rmdir('tmp')
    output_filename_path = os.getcwd()
    # Open the the final pdf in a browser to be printed.
    if output_labels_exists:
        webbrowser.get(chrome_path).open('file:///' + output_filename_path + '/' + output_filename)
    if correo_argentino_filename:
        webbrowser.get(chrome_path).open('file:///' + output_filename_path + '/' + correo_argentino_filename)

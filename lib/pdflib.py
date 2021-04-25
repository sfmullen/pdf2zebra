import logging
import os
import platform

from .labellib import *


def process_files(pdf_file: str, include_shipping_list: bool, rotate_labels: bool, printer_name: str):
    print("Opening {0}".format(pdf_file))
    logging.info("Processing %s", pdf_file)

    # Create the new output file
    output = PdfFileWriter()

    # Open the file
    with open('pdfs/{0}'.format(pdf_file), 'rb') as file:
        print("Processing {0}".format(pdf_file))
        logging.info("Processing %s", pdf_file)
        # Open the pdf document.
        pdf_reader = PdfFileReader(file)
        # Get amount of pages.
        amount_of_pages = pdf_reader.getNumPages()
        print("Detected {0} pages".format(amount_of_pages))
        logging.info("Detected %i pages", amount_of_pages)
        # If we want to separate the shipping lists, we save an index.
        shipping_list_index = []
        for index in range(amount_of_pages):
            #  Check type of page.
            label_type = delivery_type(pdf_reader.pages[index])
            if label_type['type'] != 'Shipping List':
                print("Page {0} has {1} labels".format(index, label_type["amount"]))
                logging.info("page %i has %i %s labels", index, label_type["amount"], label_type["type"])
                separate_labels(file=file, page_number=index, label_type=label_type['type'],
                                amount=label_type['amount'], rotate_labels=rotate_labels, output=output)
            else:
                print("Page {0} has a Shipping List".format(index))
                logging.info("page %i has a shipping label", index)
                shipping_list_index.append(index)

        # Write the processed pdf file.
        if output.getNumPages() > 0:
            output_filename = 'archive/labels/{0}.pdf'.format(
                datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
            with open(output_filename, 'wb') as output_file:
                output.write(output_file)
                logging.info("Saved the new labels in %s", output_filename)
                print("Saving the new labels in {0}".format(output_filename))
                if platform.system() == 'Windows' and 'SumatraPDF.exe' in os.listdir('./'):
                    printer = printer_name
                    args = "-print-to \"{0}\" \"{1}\"".format(printer, output_filename)
                    logging.info("Sending %s to printer %s", pdf_file, printer)
                    print("Sending {0} to printer {1}".format(pdf_file, printer))
                    os.system('SumatraPDF.exe ' + args)

        if include_shipping_list and len(shipping_list_index) > 0:
            shipping_list_filename = save_shipping_list_pages(PdfFileReader(file),
                                                              shipping_list_index)
            print("Saved the new shipping list in {0}".format(shipping_list_filename))
            logging.info("Saved the new shipping list pages in %s", shipping_list_filename)
        file.close()

        # Archive the original pdf.
        print("Archiving the original pdf {0}".format(pdf_file))
        logging.info("Archiving the original pdf %s", pdf_file)
        os.rename('pdfs/{0}'.format(pdf_file), 'archive/originals/{0}.pdf'.format(
            datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S")))

        print("\33[92m{0} successfully processed! \033[0m".format(pdf_file))
        logging.info("%s succesfully processed!", pdf_file)
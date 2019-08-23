from .labellib import *
import os
import platform
import logging


def process_files(pdf_file: str, include_shipping_list: bool, rotate_labels: bool):
    print("Opening {0}".format(pdf_file))

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
        # If we want to separate the shipping lists, we save an index.
        if include_shipping_list:
            shipping_list_index = []
        for index in range(amount_of_pages):
            #  Check type of page.
            label_type = delivery_type(pdf_reader.pages[index])
            if label_type['type'] != 'Shipping List':
                print("page {0} has {1} {2} labels".format(index, label_type["amount"], label_type["type"]))
                separate_labels(page=pdf_reader.getPage(index), label_type=label_type['type'],
                                amount=label_type['amount'], rotate_labels=rotate_labels, output=output)
            else:
                print("page {0} has a shipping list".format(index))
                shipping_list_index.append(index)

        # Write the processed pdf file.
        if output.getNumPages() > 0:
            output_filename = 'archive/labels/{0}.pdf'.format(
                datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
            with open(output_filename, 'wb') as output_file:
                output.write(output_file)
                logging.info("Saved the new labels in %s", output_filename)
                if platform.system() == 'Windows' and 'SumatraPDF.exe' in os.listdir('./'):
                    printer = 'SET-YOUR-THERMAL-PRINTER-NAME-HERE'
                    args = "-print-to \"{0}\" \"{1}\"".format(printer, pdf_file)
                    print("Sending {0} to printer {1}".format(pdf_file, printer))
                    os.system('SumatraPDF.exe ' + args)

        if include_shipping_list and len(shipping_list_index) > 0:
            shipping_list_filename = save_shipping_list_pages(PdfFileReader(file),
                                                              shipping_list_index)
            logging.info("Saved the new shipping list pages in %s", shipping_list_filename)
        file.close()

        # Archive the original pdf.
        print("Archiving the original pdf {0}".format(pdf_file))
        os.rename('pdfs/{0}'.format(pdf_file), 'archive/originals/{0}'.format(
            datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S")))

        print("\33[92m {0} successfully processed! \033[0m".format(pdf_file))

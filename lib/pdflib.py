from .labellib import *
import os
import logging


def process_files(include_shipping_list: bool, rotate_labels: bool):
    # Process every pdf in the watch folder.
    for pdf_file in os.listdir('./pdfs'):
        print("Opening {0}".format(pdf_file))
        if not pdf_file.endswith(".pdf"):
            print("{0} is not a pdf file. Skipping.".format(pdf_file))
            continue
        # Create the new output file
        output = PyPDF2.PdfFileWriter()
        with open('pdfs/{0}'.format(pdf_file), 'rb') as file:
            print("Processing {0}".format(pdf_file))
            logging.info("Processing %s", pdf_file)
            # Open the pdf document.
            pdf = PyPDF2.PdfFileReader(file)
            # Get amount of pages.
            amount_of_pages = pdf.getNumPages()
            # If we want to separate the shipping lists, we save an index.
            if include_shipping_list:
                shipping_list_index = []
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
                    # For later implementation of real ZPL labels.
                    # text = first_ticket.extractText()
                    # a = re.findall(r'\d{11}', text)
                    # print(a)
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

                if page_type["type"] == "Shipping List" and include_shipping_list:
                    shipping_list_index.append(index)

                if page_type["type"] == "Mail Shipping":
                    first_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    first_ticket.cropBox.lowerLeft = (0, 787)
                    first_ticket.cropBox.upperRight = (283, 460)
                    if rotate_labels:
                        first_ticket = first_ticket.rotateClockwise(90)
                    output.addPage(first_ticket)

                    # Repeat for every ticket of the page.
                    if page_type["amount"] > 1:
                        second_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        second_ticket.cropBox.lowerLeft = (310, 787)
                        second_ticket.cropBox.upperRight = (593, 460)
                        if rotate_labels:
                            second_ticket = second_ticket.rotateClockwise(90)
                        output.addPage(second_ticket)

                    if page_type["amount"] > 2:
                        third_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        third_ticket.cropBox.lowerLeft = (0, 372)
                        third_ticket.cropBox.upperRight = (283, 45)
                        if rotate_labels:
                            third_ticket = third_ticket.rotateClockwise(90)
                        output.addPage(third_ticket)

                    if page_type["amount"] > 3:
                        fourth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                        fourth_ticket.cropBox.lowerLeft = (310, 372)
                        fourth_ticket.cropBox.upperRight = (593, 45)
                        if rotate_labels:
                            fourth_ticket = fourth_ticket.rotateClockwise(90)
                        output.addPage(fourth_ticket)

            # Write the processed pdf file.
            if output.getNumPages() > 0:
                output_filename = 'archive/labels/{0}.pdf'.format(
                    datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
                with open(output_filename, 'wb') as output_file:
                    output.write(output_file)
                    logging.info("Saved the new labels in %s", output_filename)

            if include_shipping_list and len(shipping_list_index) > 0:
                shipping_list_filename = save_shipping_list_pages(PyPDF2.PdfFileReader(file),
                                                                  shipping_list_index)
                logging.info("Saved the new shipping list pages in %s", shipping_list_filename)
            file.close()

            # Archive the original pdf.
            os.rename('pdfs/{0}'.format(pdf_file), 'archive/originals/{0}'.format(
                datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S")))

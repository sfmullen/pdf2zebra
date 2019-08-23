from PyPDF2 import pdf, PdfFileWriter, PdfFileReader
import re
import datetime


def delivery_type(page: pdf.PageObject) -> dict:
    result = dict()
    page_text = page.extractText()
    if re.search("Mercado Envíos Flex", page_text) is not None:
        result["type"] = "Flex"
        result["amount"] = len((re.findall("Mercado Envíos Flex", page_text)))
        return result
    elif re.search("Información para el armado del paquete", page_text) is not None:
        result["type"] = "Loginter"
        result["amount"] = len((re.findall("Información para el armado del paquete", page_text)))
        return result
    elif '/XObject' in page['/Resources'] and page_text == '':
        result["type"] = "Mail Shipping"
        amount_of_images = page['/Resources']
        result["amount"] = len(amount_of_images['/XObject'])
        return result
    elif is_it_blank_page(page):
        result["type"] = "Empty Page"
        result["amount"] = 0
        return result
    result["type"] = "Shipping List"
    result["amount"] = 1
    return result


def save_shipping_list_pages(file: PdfFileReader, index: list) -> str:
    output = PdfFileWriter()
    for i in range(len(index)):
        output.addPage(file.getPage(index[i]))
    output_list_filename = 'archive/lists/{0}.pdf'.format(
        datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
    with open(output_list_filename, 'wb') as output_file:
        output.write(output_file)
    return output_list_filename


def is_it_blank_page(page: pdf.PageObject) -> bool:
    if page.extractText() == '' and '/XObject' not in page['/Resources']:
        return True
    return False


def separate_labels(page: pdf.PageObject, label_type: str, amount: int, rotate_labels: bool,
                    output: PdfFileWriter) -> None:
    if label_type == "Loginter":
        # Create a page for every sticker.
        # Copy the ith page to  first_ticket.
        first_ticket = page
        # Crop the first ticket of the page.
        first_ticket.cropBox.lowerLeft = (22, 750)
        first_ticket.cropBox.upperRight = (202, 465)
        if rotate_labels:
            first_ticket = first_ticket.rotateClockwise(90)
        output.addPage(first_ticket)
        # Repeat for every ticket of the page.
        if amount > 1:
            second_ticket = page
            second_ticket.cropBox.lowerLeft = (208, 750)
            second_ticket.cropBox.upperRight = (388, 465)
            if rotate_labels:
                second_ticket = second_ticket.rotateClockwise(90)
            output.addPage(second_ticket)

        if amount > 2:
            third_ticket = page
            third_ticket.cropBox.lowerLeft = (394, 750)
            third_ticket.cropBox.upperRight = (574, 465)
            if rotate_labels:
                third_ticket = third_ticket.rotateClockwise(90)
            output.addPage(third_ticket)

        if amount > 3:
            fourth_ticket = page
            fourth_ticket.cropBox.lowerLeft = (22, 390)
            fourth_ticket.cropBox.upperRight = (202, 105)
            if rotate_labels:
                fourth_ticket = fourth_ticket.rotateClockwise(90)
            output.addPage(fourth_ticket)

        if amount > 4:
            fifth_ticket = page
            fifth_ticket.cropBox.lowerLeft = (208, 390)
            fifth_ticket.cropBox.upperRight = (388, 105)
            if rotate_labels:
                fifth_ticket = fifth_ticket.rotateClockwise(90)
            output.addPage(fifth_ticket)

        if amount > 5:
            sixth_ticket = page
            sixth_ticket.cropBox.lowerLeft = (394, 390)
            sixth_ticket.cropBox.upperRight = (574, 105)
            if rotate_labels:
                sixth_ticket = sixth_ticket.rotateClockwise(90)
            output.addPage(sixth_ticket)

    if label_type == "Flex":
        first_ticket = page
        # For later implementation of real ZPL labels.
        # text = first_ticket.extractText()
        # a = re.findall(r'\d{11}', text)
        # print(a)
        first_ticket.cropBox.lowerLeft = (45, 90)
        first_ticket.cropBox.upperRight = (270, 500)
        if rotate_labels:
            first_ticket = first_ticket.rotateClockwise(90)
        output.addPage(first_ticket)
        if amount > 1:
            second_ticket = page
            second_ticket.cropBox.lowerLeft = (320, 90)
            second_ticket.cropBox.upperRight = (545, 500)
            if rotate_labels:
                second_ticket = second_ticket.rotateClockwise(90)
            output.addPage(second_ticket)
        if amount > 2:
            third_ticket = page
            third_ticket.cropBox.lowerLeft = (590, 90)
            third_ticket.cropBox.upperRight = (815, 500)
            if rotate_labels:
                third_ticket = third_ticket.rotateClockwise(90)
            output.addPage(third_ticket)

    if label_type == "Mail Shipping":
        first_ticket = page
        first_ticket.cropBox.lowerLeft = (0, 787)
        first_ticket.cropBox.upperRight = (283, 460)
        if rotate_labels:
            first_ticket = first_ticket.rotateClockwise(90)
        output.addPage(first_ticket)

        # Repeat for every ticket of the page.
        if amount > 1:
            second_ticket = page
            second_ticket.cropBox.lowerLeft = (310, 787)
            second_ticket.cropBox.upperRight = (593, 460)
            if rotate_labels:
                second_ticket = second_ticket.rotateClockwise(90)
            output.addPage(second_ticket)

        if amount > 2:
            third_ticket = page
            third_ticket.cropBox.lowerLeft = (0, 372)
            third_ticket.cropBox.upperRight = (283, 45)
            if rotate_labels:
                third_ticket = third_ticket.rotateClockwise(90)
            output.addPage(third_ticket)

        if amount > 3:
            fourth_ticket = page
            fourth_ticket.cropBox.lowerLeft = (310, 372)
            fourth_ticket.cropBox.upperRight = (593, 45)
            if rotate_labels:
                fourth_ticket = fourth_ticket.rotateClockwise(90)
            output.addPage(fourth_ticket)

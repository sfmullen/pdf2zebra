import datetime
import io
import re
import time

from PyPDF2 import pdf, PdfFileWriter, PdfFileReader
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph
from tabula import read_pdf


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


def save_shipping_list_pages(file: PdfFileReader, page_number: list) -> str:
    output = PdfFileWriter()
    for i in range(len(page_number)):
        output.addPage(file.getPage(page_number[i]))
    output_list_filename = 'archive/lists/{0}.pdf'.format(
        datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
    with open(output_list_filename, 'wb') as output_file:
        output.write(output_file)
    return output_list_filename


def is_it_blank_page(page: pdf.PageObject) -> bool:
    if page.extractText() == '' and '/XObject' not in page['/Resources']:
        return True
    return False


def separate_labels(file: object, page_number: int, label_type: str, amount: int, rotate_labels: bool,
                    output: PdfFileWriter) -> None:
    if label_type == "Loginter":
        # Create a page for every sticker.
        # Copy the ith page to first_ticket.
        first_ticket = PdfFileReader(file).getPage(page_number)
        # Crop the first ticket of the page.
        first_ticket.cropBox.lowerLeft = (22, 750)
        first_ticket.cropBox.upperRight = (202, 465)
        if rotate_labels:
            first_ticket = first_ticket.rotateClockwise(90)
        output.addPage(first_ticket)
        # Repeat for every ticket of the page.
        if amount > 1:
            second_ticket = PdfFileReader(file).getPage(page_number)
            second_ticket.cropBox.lowerLeft = (208, 750)
            second_ticket.cropBox.upperRight = (388, 465)
            if rotate_labels:
                second_ticket = second_ticket.rotateClockwise(90)
            output.addPage(second_ticket)

        if amount > 2:
            third_ticket = PdfFileReader(file).getPage(page_number)
            third_ticket.cropBox.lowerLeft = (394, 750)
            third_ticket.cropBox.upperRight = (574, 465)
            if rotate_labels:
                third_ticket = third_ticket.rotateClockwise(90)
            output.addPage(third_ticket)

        if amount > 3:
            fourth_ticket = PdfFileReader(file).getPage(page_number)
            fourth_ticket.cropBox.lowerLeft = (22, 390)
            fourth_ticket.cropBox.upperRight = (202, 105)
            if rotate_labels:
                fourth_ticket = fourth_ticket.rotateClockwise(90)
            output.addPage(fourth_ticket)

        if amount > 4:
            fifth_ticket = PdfFileReader(file).getPage(page_number)
            fifth_ticket.cropBox.lowerLeft = (208, 390)
            fifth_ticket.cropBox.upperRight = (388, 105)
            if rotate_labels:
                fifth_ticket = fifth_ticket.rotateClockwise(90)
            output.addPage(fifth_ticket)

        if amount > 5:
            sixth_ticket = PdfFileReader(file).getPage(page_number)
            sixth_ticket.cropBox.lowerLeft = (394, 390)
            sixth_ticket.cropBox.upperRight = (574, 105)
            if rotate_labels:
                sixth_ticket = sixth_ticket.rotateClockwise(90)
            output.addPage(sixth_ticket)

    if label_type == "Flex":
        first_ticket = PdfFileReader(file).getPage(page_number)
        first_ticket.cropBox.lowerLeft = (45, 90)
        first_ticket.cropBox.upperRight = (270, 500)
        if rotate_labels:
            first_ticket = first_ticket.rotateClockwise(90)
        output.addPage(first_ticket)
        if amount > 1:
            second_ticket = PdfFileReader(file).getPage(page_number)
            second_ticket.cropBox.lowerLeft = (320, 90)
            second_ticket.cropBox.upperRight = (545, 500)
            if rotate_labels:
                second_ticket = second_ticket.rotateClockwise(90)
            output.addPage(second_ticket)
        if amount > 2:
            third_ticket = PdfFileReader(file).getPage(page_number)
            third_ticket.cropBox.lowerLeft = (590, 90)
            third_ticket.cropBox.upperRight = (815, 500)
            if rotate_labels:
                third_ticket = third_ticket.rotateClockwise(90)
            output.addPage(third_ticket)

    if label_type == "Mail Shipping":
        first_ticket = PdfFileReader(file).getPage(page_number)
        first_ticket.cropBox.lowerLeft = (0, 787)
        first_ticket.cropBox.upperRight = (283, 460)
        if rotate_labels:
            first_ticket = first_ticket.rotateClockwise(90)
        output.addPage(first_ticket)

        # Repeat for every ticket of the page.
        if amount > 1:
            second_ticket = PdfFileReader(file).getPage(page_number)
            second_ticket.cropBox.lowerLeft = (310, 787)
            second_ticket.cropBox.upperRight = (593, 460)
            if rotate_labels:
                second_ticket = second_ticket.rotateClockwise(90)
            output.addPage(second_ticket)

        if amount > 2:
            third_ticket = PdfFileReader(file).getPage(page_number)
            third_ticket.cropBox.lowerLeft = (0, 372)
            third_ticket.cropBox.upperRight = (283, 45)
            if rotate_labels:
                third_ticket = third_ticket.rotateClockwise(90)
            output.addPage(third_ticket)

        if amount > 3:
            fourth_ticket = PdfFileReader(file).getPage(page_number)
            fourth_ticket.cropBox.lowerLeft = (310, 372)
            fourth_ticket.cropBox.upperRight = (593, 45)
            if rotate_labels:
                fourth_ticket = fourth_ticket.rotateClockwise(90)
            output.addPage(fourth_ticket)


def get_shipment_id_from_label(table):
    pattern = '\d{11}'  #
    if table['extraction_method'] != '':
        for data in table['data']:
            for value in data:
                if re.findall(pattern, value['text']):
                    return re.findall(pattern, value['text'])[0]


def search_shipment_ids(file: str) -> list:
    df2 = read_pdf(file, pages="all", area=(0, 0, 100, 100), relative_area=True, output_format="json",
                   stream=True)
    result = []
    for table in df2:
        id = get_shipment_id_from_label(table)
        if id:
            result.append(id)
        else:
            result.append("None")

    return result


def modify_labels(cropped_labels):
    with open(cropped_labels, 'rb') as file:
        reader_pdf = PdfFileReader(file)
        output = PdfFileWriter()
        start_time = time.time()
        shipments_ids = search_shipment_ids(cropped_labels)
        for index in range(reader_pdf.getNumPages()):
            if delivery_type(reader_pdf.pages[index])['type'] == 'Flex':
                x = reader_pdf.getPage(index).cropBox
                packet = io.BytesIO()
                # create a new PDF with Reportlab
                can = canvas.Canvas(packet, pagesize=(x[2] - x[0], x[3] - x[1]))
                can.setFillColorRGB(1, 1, 1)
                can.rect(x[0], x[1], x[2] - x[0], (x[3] - x[1]) / 4, fill=1)
                can.setStrokeColorRGB(0.78, 0.78, 0.78)
                can.rect(x[0] + 3, x[1] + 3, (x[2] - x[0]) - 6, ((x[3] - x[1]) / 4) - 6, fill=0)

                style = ParagraphStyle('title', fontSize=8, leading=8)
                title = Paragraph(
                    "<b>{{ MERCADOLIBRE PUBLICATION TITLE }}</b>",
                    style)
                title_data = [[title]]
                title_table = (Table(title_data, colWidths=(x[2] - x[0] - 10)))
                title_table.setStyle([("VALIGN", (0, 0), (0, 0), "BOTTOM")])
                title_table.wrapOn(can, x[2] - x[0], (x[3] - x[1]) / 4)
                title_table.drawOn(can, x[0] + 5, ((x[3] - x[1]) / 3) + 30)

                text_style = ParagraphStyle('title', fontSize=9, leading=8)
                sku = Paragraph(
                    "<b>SKU: {{ PRODUCT SKU }}</b>",
                    text_style)
                quantity = Paragraph(
                    "<b>QUANTITY: {{ QUANTITY }}</b>",
                    text_style)
                color = Paragraph(
                    "<b>COLOR: {{ PRODUCT COLOR }}</b>",
                    text_style)
                size = Paragraph(
                    "<b>SIZE: {{ PRODUCT SIZE }}</b>",
                    text_style)

                data = [[sku], [color], [quantity], [size]]
                table = Table(data, colWidths=(x[2] - x[0] - 10))
                table.setStyle([("VALIGN", (0, 0), (0, 0), "TOP")])
                table.wrapOn(can, x[2] - x[0], (x[3] - x[1]) / 5)
                table.drawOn(can, x[0] + 5, x[1] + 15)

                qr_code = qr.QrCodeWidget(shipments_ids[index])
                bounds = qr_code.getBounds()
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                d = Drawing(45, 45, transform=[70. / width, 0, 0, 70. / height, 0, 0])
                d.add(qr_code)
                renderPDF.draw(d, can, x[2] - 70, x[1] + 10)

                can.save()

                # move to the beginning of the StringIO buffer
                packet.seek(0)
                new_pdf = PdfFileReader(packet)
                # add the "watermark" (which is the new pdf) on the existing page
                page = reader_pdf.getPage(index)
                page.mergePage(new_pdf.getPage(0))
                output.addPage(reader_pdf.getPage(index))

            if delivery_type(reader_pdf.pages[index])['type'] == 'Loginter':
                x = reader_pdf.getPage(index).cropBox
                packet = io.BytesIO()
                # create a new PDF with Reportlab
                can = canvas.Canvas(packet, pagesize=(x[2] - x[0], x[1] - x[3]))
                can.setFillColorRGB(1, 1, 1)
                can.rect(x[0], x[1] - 90, x[2] - x[0], x[1] - x[3], fill=1)
                can.setStrokeColorRGB(0.78, 0.78, 0.78)
                can.rect(x[0] + 3, x[1] - 87, x[2] - x[0] - 6, ((x[1] - x[3]) / 3.4), fill=0)

                style = ParagraphStyle('title', fontSize=6, leading=8)
                title = Paragraph(
                    "<b>{{ MERCADOLIBRE PUBLICATION TITLE }}</b>",
                    style)
                title_data = [[title]]
                title_table = (Table(title_data, colWidths=(x[2] - x[0] - 10)))
                title_table.setStyle([("VALIGN", (0, 0), (0, 0), "BOTTOM")])
                title_table.wrapOn(can, x[2] - x[0], (x[3] - x[1]) / 4)
                title_table.drawOn(can, x[0] + 2, x[1] - 25)

                text_style = ParagraphStyle('title', fontSize=7, leading=8)
                sku = Paragraph(
                    "<b>SKU: {{ PRODUCT SKU }}</b>",
                    text_style)
                quantity = Paragraph(
                    "<b>QUANTITY: {{ QUANTITY }}</b>",
                    text_style)
                color = Paragraph(
                    "<b>COLOR: {{ PRODUCT COLOR }}</b>",
                    text_style)
                size = Paragraph(
                    "<b>SIZE: {{ PRODUCT SIZE }}</b>",
                    text_style)

                data = [[sku], [color], [quantity], [size]]
                table = Table(data, colWidths=(x[2] - x[0] - 10))
                table.setStyle([("VALIGN", (0, 0), (0, 0), "TOP")])
                table.wrapOn(can, x[2] - x[0], (x[3] - x[1]) / 5)
                table.drawOn(can, x[0] + 2, x[1] - 80)

                qr_code = qr.QrCodeWidget(shipments_ids[index])
                bounds = qr_code.getBounds()
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                d = Drawing(45, 45, transform=[60. / width, 0, 0, 60. / height, 0, 0])
                d.add(qr_code)
                renderPDF.draw(d, can, x[2] - 60, x[1] - 80)

                can.save()

                # move to the beginning of the StringIO buffer
                packet.seek(0)
                new_pdf = PdfFileReader(packet)
                # add the "watermark" (which is the new pdf) on the existing page
                page = reader_pdf.getPage(index)
                page.mergePage(new_pdf.getPage(0))
                output.addPage(reader_pdf.getPage(index))
            else:
                output.addPage(reader_pdf.getPage(index))
        # finally, write "output" to a real file
        output_filename = 'archive/modified_labels/{0}.pdf'.format(
            datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
        outputStream = open(output_filename, "wb")
        output.write(outputStream)
        outputStream.close()
        print("--- %s seconds ---" % (time.time() - start_time))

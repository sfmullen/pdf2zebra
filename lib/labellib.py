import datetime
import io
import re
import time
import tabula

from PyPDF2 import pdf, PdfFileWriter, PdfFileReader
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph


def delivery_type(page: pdf.PageObject) -> dict:
    result = dict()
    page_text = page.extractText()
    if re.search("Tracking", page_text) is not None:
        result["type"] = "Label"
        result["amount"] = len((re.findall("Tracking", page_text)))
        return result
    elif is_it_blank_page(page):
        result["type"] = "Empty Page"
        result["amount"] = 0
        return result
    else:
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
    # Create a page for every sticker.
    # Copy the ith page to first_ticket.
    first_ticket = PdfFileReader(file).getPage(page_number)
    # Crop the first ticket of the page.
    first_ticket.cropBox.lowerLeft = (31, 567)  # First number is left margin, second one is the top.
    first_ticket.cropBox.upperRight = (295, 19)  # First one is right margin, second ome is the bottom.
    if rotate_labels:
        first_ticket = first_ticket.rotateClockwise(90)
    output.addPage(first_ticket)
    # Repeat for every ticket of the page.
    if amount > 1:
        second_ticket = PdfFileReader(file).getPage(page_number)
        second_ticket.cropBox.lowerLeft = (296, 567)
        second_ticket.cropBox.upperRight = (560, 19)
        if rotate_labels:
            second_ticket = second_ticket.rotateClockwise(90)
        output.addPage(second_ticket)

    if amount > 2:
        third_ticket = PdfFileReader(file).getPage(page_number)
        third_ticket.cropBox.lowerLeft = (561, 567)
        third_ticket.cropBox.upperRight = (825, 19)
        if rotate_labels:
            third_ticket = third_ticket.rotateClockwise(90)
        output.addPage(third_ticket)


def get_shipment_id_from_label(table):
    pattern = '\d{11}'  #
    if table['extraction_method'] != '':
        for data in table['data']:
            for value in data:
                if re.findall(pattern, value['text']):
                    return re.findall(pattern, value['text'])[0]


def search_shipment_ids(file: str) -> list:
    df2 = tabula.read_pdf(file, pages="all", area=(0, 0, 100, 100), relative_area=True, output_format="json",
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

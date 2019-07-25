import PyPDF2
import re
import datetime


def delivery_type(page: PyPDF2.pdf.PageObject) -> dict:
    result = dict()
    page_text = page.extractText()
    if re.search("Mercado Envíos Flex", page_text) is not None:
        result["type"] = "Flex"
        result["amount"] = len((re.findall("Mercado Envíos Flex", page_text)))
        return result
    if re.search("IdentificaciónProductosDespacha", page_text) is not None:
        result["type"] = "Correo Argentino List"
        result["amount"] = 1
        return result
    if re.search("Información para el armado del paquete", page_text) is not None:
        result["type"] = "Loginter"
        result["amount"] = len((re.findall("Información para el armado del paquete", page_text)))
        return result
    result["type"] = "Correo Argentino"
    result["amount"] = 4
    return result


def save_correo_argentino_pages(file: PyPDF2.pdf.PdfFileReader, index: list) -> str:
    output = PyPDF2.PdfFileWriter()
    for i in range(len(index)):
        output.addPage(file.getPage(index[i]))
    output_list_filename = 'output/lists/{0}.pdf'.format(datetime.datetime.now().strftime("%d-%m-%y--%H:%M:%S"))
    with open(output_list_filename, 'wb') as output_file:
        output.write(output_file)
    return output_list_filename

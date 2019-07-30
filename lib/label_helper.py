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
    elif re.search("IdentificaciónProductosDespacha", page_text) is not None or re.search(
            "Nº SEGUIMIENTOPRODUCTO", page_text) is not None or re.search("Identificador Producto",
                                                                          page_text) is not None:
        result["type"] = "Shipping List"
        result["amount"] = 1
        return result
    elif re.search("Información para el armado del paquete", page_text) is not None:
        result["type"] = "Loginter"
        result["amount"] = len((re.findall("Información para el armado del paquete", page_text)))
        return result
    elif is_it_blank_page(page):
        result["type"] = "Empty Page"
        result["amount"] = 0
        return result
    result["type"] = "Correo Argentino"
    amount_of_images = page['/Resources']
    result["amount"] = len(amount_of_images['/XObject'])
    return result


def save_shipping_list_pages(file: PyPDF2.pdf.PdfFileReader, index: list) -> str:
    output = PyPDF2.PdfFileWriter()
    for i in range(len(index)):
        output.addPage(file.getPage(index[i]))
    output_list_filename = 'output/lists/{0}.pdf'.format(datetime.datetime.now().strftime("%d-%m-%y--%H_%M_%S"))
    with open(output_list_filename, 'wb') as output_file:
        output.write(output_file)
    return output_list_filename


def is_it_blank_page(page: PyPDF2.pdf.PageObject) -> bool:
    if page.extractText() == '' and '/XObject' not in page['/Resources']:
        return True
    return False

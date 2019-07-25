import PyPDF2
import os
import webbrowser
import datetime
import platform
import re


# from pdf2image import convert_from_path
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from reportlab.lib.units import mm
# from PIL import Image


def delivery_type(page: PyPDF2.pdf.PageObject):
    result = dict()
    page_text = page.extractText()
    if re.search("Mercado Envíos Flex", page_text) is not None:
        result["type"] = "Flex"
        result["amount"] = len((re.findall("Mercado Envíos Flex", page_text)))
        return result
    if re.search("IdentificaciónProductosDespacha", page_text) is not None:
        result["type"] = "Flex list"
        result["amount"] = 1
        return result
    if re.search("Información para el armado del paquete", page_text) is not None:
        result["type"] = "Loginter"
        result["amount"] = len((re.findall("Información para el armado del paquete", page_text)))
        return result
    result["type"] = "Correo Argentino"
    result["amount"] = 4
    return result


#
# def get_starting_page(pdf_reader_file: PyPDF2.pdf.PdfFileReader):
#     result = 0
#     for page in pdf_reader_file.pages:
#         # Then, avoid every list pages.
#         for word in page.extractText().split():
#             if word == "pegar":
#                 return result
#         result += 1
#     return result
#
#
# def is_it_blank_page(pdf_page: PyPDF2.pdf.PageObject):
#     if pdf_page.extractText() != '':
#         return True
#     return False
#
#
# def save_list_pages(input_file: PyPDF2.pdf.PdfFileReader, end: int, output_list_file: PyPDF2.PdfFileMerger):
#     page_range = PyPDF2.PageRange("0:" + str(end))
#     output_list_file.append(input_file, pages=page_range)


# Create the output folder if it doesn't exists.
os.makedirs('output', exist_ok=True)
os.makedirs('output/labels', exist_ok=True)
os.makedirs('output/lists', exist_ok=True)

# Create the temporary work folder.
os.makedirs('tmp', exist_ok=True)
# Create the new output file for the labels
output = PyPDF2.PdfFileWriter()
# Create the new output file for the lists.
list_pages_output = PyPDF2.PdfFileMerger()
# Boolean for opening the file at the end.
list_pages_exists = False

# Check if pdfs folder contains no pdf files.
empty_folder = True
for pdf_file in os.listdir('./pdfs'):
    if pdf_file.endswith(".pdf"):
        empty_folder = False
if empty_folder:
    os.rmdir("tmp")
    exit()

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
        # Open the pdf document.
        pdf = PyPDF2.PdfFileReader(file)
        # Get amount of pages.
        amount_of_pages = pdf.getNumPages()
        #  Check type of document.
        for index in range(amount_of_pages):
            page_type = delivery_type(pdf.pages[index])
            if page_type["type"] == "Loginter":
                # Create a page for every sticker.
                # Copy the ith page to  first_ticket.
                first_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                # Crop the first ticket of the page.
                first_ticket.cropBox.lowerLeft = (22, 750)
                first_ticket.cropBox.upperRight = (202, 465)
                output.addPage(first_ticket)

                # Repeat for every ticket of the page.
                if page_type["amount"] > 1:
                    second_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    second_ticket.cropBox.lowerLeft = (208, 750)
                    second_ticket.cropBox.upperRight = (388, 465)
                    output.addPage(second_ticket)

                if page_type["amount"] > 2:
                    third_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    third_ticket.cropBox.lowerLeft = (394, 750)
                    third_ticket.cropBox.upperRight = (574, 465)
                    output.addPage(third_ticket)

                if page_type["amount"] > 3:
                    fourth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    fourth_ticket.cropBox.lowerLeft = (22, 390)
                    fourth_ticket.cropBox.upperRight = (202, 105)
                    output.addPage(fourth_ticket)

                if page_type["amount"] > 4:
                    fifth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    fifth_ticket.cropBox.lowerLeft = (208, 390)
                    fifth_ticket.cropBox.upperRight = (388, 105)
                    output.addPage(fifth_ticket)

                if page_type["amount"] > 5:
                    sixth_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    sixth_ticket.cropBox.lowerLeft = (394, 390)
                    sixth_ticket.cropBox.upperRight = (574, 105)
                    output.addPage(sixth_ticket)

            if page_type["type"] == "Flex":
                first_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                first_ticket.cropBox.lowerLeft = (45, 90)
                first_ticket.cropBox.upperRight = (270, 500)
                output.addPage(first_ticket)
                if page_type["amount"] > 1:
                    second_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    second_ticket.cropBox.lowerLeft = (320, 90)
                    second_ticket.cropBox.upperRight = (545, 500)
                    output.addPage(second_ticket)
                if page_type["amount"] > 2:
                    third_ticket = PyPDF2.PdfFileReader(file).getPage(index)
                    third_ticket.cropBox.lowerLeft = (590, 90)
                    third_ticket.cropBox.upperRight = (815, 500)
                    output.addPage(third_ticket)

            # if page_type["type"] == "Flex list":
            #     output.addPage(PyPDF2.PdfFileReader(file).getPage(index))

        # Write the processed pdf file.
        output_filename = 'output/labels/{0}.pdf'.format(datetime.datetime.now().strftime("%d-%m-%y--%H:%M:%S"))
        with open(output_filename, 'wb') as output_file:
            output.write(output_file)
        file.close()
        # Delete the original pdf.
        os.unlink('pdfs/{0}'.format(pdf_file))

# Convert every page of the output file to a image.
# convert_from_path('tmp/output-0.pdf', 72, output_folder='tmp', fmt='png', use_cropbox=True)

# Delete the pdf created.
# os.unlink('tmp/output-0.pdf')
#
# # Create a new pdf for every image (without the empty tickets).
# for files in os.listdir('./tmp'):
#     # Create the pdf with the images, with correct format for a 100x75mm page.
#     pagesize = (100 * mm, 75 * mm)
#     c = canvas.Canvas('./tmp/{0}.pdf'.format(files), pagesize=pagesize)
#     # Open the image.
#     image = Image.open('tmp/{0}'.format(files))
#     # Rotate the image.
#     image = image.rotate(90, expand=True)
#     # Check if image is empty
#     if image.getextrema() != ((255, 255), (255, 255), (255, 255)):
#         # If it is not, paste it on the pdf.
#         c.drawImage(ImageReader(image), 0, 0, width=100 * mm, height=75 * mm, preserveAspectRatio=True)
#         # Save the pdf.
#         c.save()
#     # Delete the image.
#     image.close()
#     del c
#     os.unlink('tmp/{0}'.format(files))
#
# # Create the merger pdf.
# merger = PyPDF2.PdfFileMerger()
# # Append every pdf created before.
# for pdfs in sorted(os.listdir('./tmp')):
#     with open('tmp/{0}'.format(pdfs), 'rb') as merge_pdf:
#         pdf = PyPDF2.PdfFileReader(merge_pdf)
#         merger.append(pdf)
#         # Delete the used pdf.
#     os.unlink('tmp/{0}'.format(pdfs))
# # Write the merger to a file.
# output_filename = 'output/labels/output_{0}.pdf'.format(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
# with open(output_filename, 'wb') as fout:
#     merger.write(fout)
# Delete the temporary folder.
os.rmdir('tmp')
output_filename_path = os.getcwd()
# Open the the final pdf in a browser to be printed.
webbrowser.get(chrome_path).open('file:///' + output_filename_path + '/' + output_filename)
# if list_pages_exists:
#     output_list_filename = 'output/lists/output_list_pages_{0}.pdf'.format(
#         datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
#     with open(output_list_filename, 'wb') as output_file:
#         list_pages_output.write(output_file)
#     webbrowser.get(chrome_path).open('file:///' + output_filename_path + '/' + output_list_filename)

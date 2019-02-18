import PyPDF2
import os
import webbrowser
import datetime
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from PIL import Image


def is_it_flex(pdf_reader_file: PyPDF2.pdf.PdfFileReader):
    if pdf_reader_file.pages[0].extractText().split()[0] == "Identificador":
        return False
    return True


def get_starting_page(pdf_reader_file: PyPDF2.pdf.PdfFileReader):
    result = 0
    for page in pdf_reader_file.pages:
        # Then, avoid every list pages.
        for word in page.extractText().split():
            if word == "pegar":
                return result
        result += 1
    return result


def is_it_blank_page(pdf_page: PyPDF2.pdf.PageObject):
    if pdf_page.extractText() != '':
        return True
    return False


def save_list_pages(pdf_reader_file: PyPDF2.pdf.PdfFileReader, end: int):
    output_list_pages = PyPDF2.PdfFileWriter()
    for x in range(0, end):
        output_list_pages.addPage(pdf_reader_file.getPage(x))
    output_list_filename = 'output/lists/output_list_pages_{0}.pdf'.format(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
    with open(output_list_filename, 'wb') as output_file:
        output_list_pages.write(output_file)
    return output_list_filename


# Create the output folder if it doesn't exists.
os.makedirs('output', exist_ok=True)
os.makedirs('output/labels', exist_ok=True)
os.makedirs('output/lists', exist_ok=True)

# Create the temporary work folder.
os.makedirs('tmp', exist_ok=True)

# Create the new output file
output = PyPDF2.PdfFileWriter()

# Boolean for opening the file at the end.
list_pages_exists = False

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
        if not is_it_flex(pdf):
            # Calculate where to start cropping the file
            starting_page = get_starting_page(pdf)
            # Save the product list pages if they exists.
            if starting_page != 0:
                # Extract the list pages.
                list_filename = save_list_pages(pdf, starting_page)
                # Change the boolean to open this file at the end.
                list_pages_exists = True
            # Create a page for every sticker.
            for i in range(starting_page, amount_of_pages):
                # We don't process a page if it's empty.
                if pdf.pages[i].extractText() is not '':
                    # Copy the ith page to  first_ticket.
                    first_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                    # Crop the first ticket of the page.
                    first_ticket.cropBox.lowerLeft = (20, 760)
                    first_ticket.cropBox.upperRight = (205, 450)

                    # Repeat for every ticket of the page.
                    second_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                    second_ticket.cropBox.lowerLeft = (205, 760)
                    second_ticket.cropBox.upperRight = (390, 450)

                    third_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                    third_ticket.cropBox.lowerLeft = (390, 760)
                    third_ticket.cropBox.upperRight = (575, 450)

                    fourth_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                    fourth_ticket.cropBox.lowerLeft = (20, 400)
                    fourth_ticket.cropBox.upperRight = (205, 90)

                    fifth_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                    fifth_ticket.cropBox.lowerLeft = (205, 400)
                    fifth_ticket.cropBox.upperRight = (390, 90)

                    sixth_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                    sixth_ticket.cropBox.lowerLeft = (390, 400)
                    sixth_ticket.cropBox.upperRight = (575, 90)

                    # Add every ticket to the output file.
                    output.addPage(first_ticket)
                    output.addPage(second_ticket)
                    output.addPage(third_ticket)
                    output.addPage(fourth_ticket)
                    output.addPage(fifth_ticket)
                    output.addPage(sixth_ticket)
        else:
            for i in range(0, amount_of_pages):
                first_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                first_ticket.cropBox.lowerLeft = (40, 90)
                first_ticket.cropBox.upperRight = (270, 550)

                second_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                second_ticket.cropBox.lowerLeft = (315, 90)
                second_ticket.cropBox.upperRight = (545, 550)

                third_ticket = PyPDF2.PdfFileReader(file).getPage(i)
                third_ticket.cropBox.lowerLeft = (585, 90)
                third_ticket.cropBox.upperRight = (815, 550)

                output.addPage(first_ticket)
                output.addPage(second_ticket)
                output.addPage(third_ticket)

        # Write the processed pdf file to it's output-0.
        with open('tmp/output-0.pdf', 'wb') as fo:
            output.write(fo)
        # Delete the original pdf.
        file.close()
        os.unlink('pdfs/{0}'.format(pdf_file))

# Convert every page of the output file to a image.
convert_from_path('tmp/output-0.pdf', 203, output_folder='tmp', fmt='jpeg', use_cropbox=True)

# Delete the pdf created.
os.unlink('tmp/output-0.pdf')

# Create a new pdf for every image (without the empty tickets).
for files in os.listdir('./tmp'):
    # Create the pdf with the images, with correct format for a 100x150mm page.
    c = canvas.Canvas('./tmp/{0}.pdf'.format(files), pagesize=(283.01, 424.52))
    # Open the image.
    image = Image.open('tmp/{0}'.format(files))
    # Check if image is empty
    if image.getextrema() != ((255, 255), (255, 255), (255, 255)):
        # If it is not, paste it on the pdf.
        c.drawImage('tmp/{0}'.format(files), 0, 3, 280, 420, preserveAspectRatio=True, showBoundary=True)
        # Save the pdf.
        c.save()
    # Delete the image.
    image.close()
    del c
    os.unlink('tmp/{0}'.format(files))

# Create the merger pdf.
merger = PyPDF2.PdfFileMerger()
# Append every pdf created before.
for pdfs in sorted(os.listdir('./tmp')):
    with open('tmp/{0}'.format(pdfs), 'rb') as merge_pdf:
        pdf = PyPDF2.PdfFileReader(merge_pdf)
        merger.append(pdf)
        # Delete the used pdf.
    os.unlink('tmp/{0}'.format(pdfs))
# Write the merger to a file.
output_filename = 'output/labels/output_{0}.pdf'.format(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
with open(output_filename, 'wb') as fout:
    merger.write(fout)
# Delete the temporary folder.
os.rmdir('tmp')
output_filename_path = os.getcwd()
# Open the the final pdf in a browser to be printed.
webbrowser.open('file:///' + output_filename_path + '/' + output_filename)
if list_pages_exists:
    webbrowser.open('file:///' + output_filename_path + '/' + list_filename)

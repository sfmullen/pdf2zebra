# pdf2zebra
A Python Script to convert a PDF file containing MercadoLibre shipping labels to a compatible format for the Zebra Thermal Printer.

### Requirements

Python3

PyPDF2: ``pip install PyPDF2``

### Usage:

Simply copy the pdf containing the shipping labels inside the **pdfs/** folder, and execute the script ``python3 main.py``

#### Settings:

For now, it is possible to change two settings: Rotate and Thermal, inside **settings.ini**. Under [CORREO ARGENTINO LIST], **Thermal** controls if the Correo Argentino labels should be included in the output file within the Loginter and Flex labels. If not, a separate PDF file will be created instead.

**Rotate** changes the rotation of the labels. If changed to **yes**, then the resulting labels will be rotated clockwise 90 degrees. This is useful if you don't want to change the default printing orientation of the printer settings.

#### Output:

The resulting PDF files should be automatically opened inside Google Chrome. If you want to change the browser, or if it is not installed in the default location, you have to change the path in Line 42 inside **main.py**

#### Troubleshooting:

If the label text is blurry/fuzzy, try to print the PDF from Adobe Reader or Microsoft Edge. Alternatively, you can change the code where the document is opened automatically, to be opened with the default PDF reader. Simply change `webbrowser.get(chrome_path).open('file:///' + output_filename_path + '/' + output_filename)` to `os.startfile(output_filename_path + '/' + output_filename)`

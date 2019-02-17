from setuptools import setup

setup(
    name='AjaxGold_PDF_to_Zebra',
    version='0.1',
    url='github.com/MacMullen/pdf_to_zebra',
    license='',
    author='Simon Faillace Mullen (MacMullen)',
    author_email='macmullen@github.com',
    description='A script to convert VirtualServer automated pdfs to a compatible format to print using Zebra printers.',
    install_requires=['reportlab', 'PyPDF2', 'pdf2image', 'Pillow']
)

<p align="center"><img src="https://raw.githubusercontent.com/MacMullen/github-resources/master/pdf2zebra/banner.png"/></p>

A Python3 Script to convert a PDF file containing MercadoLibre shipping labels to a compatible format for the Zebra Thermal Printer.

#### Installation

Install the packages listed in the requirements file.

```
pip install -r requirements.txt
```

#### Usage:
Simply start the program via the command line:
```
python3 main.py
```
Wait for it to create the necessary folder structure in the root folder (where **main.py** was executed), and start processing your files by copying/moving them to the **pdfs** folder.

Output files are saved in the **archive** folder. Shipping labels are saved in the **labels** folder, shipping lists in the **lists** folder and the original files are moved to **originals**.

##### Settings:
Inside **settings.ini** you can find the following settings that change the output result.

**Process** under the SHIPPING LISTS section, controls if the shipping lists are processed or not. If you choose to, they will be saved on separate file, saved in the **lists** folder.

**Rotate** changes the rotation of the labels. If changed to **yes**, then the resulting labels will be rotated clockwise 90 degrees. This is useful if you don't want to change the default printing orientation of the printer settings.

**Printer Name**, is the name of the printer which it will send the labels to print to after being processed. It should be exactly as it is shown by Windows. (e.g "Microsoft XPS Document Writer")

#### Automation:

After being processed, the output file/s are opened in the default PDF viewer. If you are on Windows, you can choose to send them to the printer directly. Download the <a href="https://www.sumatrapdfreader.org/download-free-pdf-viewer.html" target="_blank">portable version of SumatraPDF</a> and copy the **SumatraPDF** executable to the root directory of pdf2zebra. Afterwards, write the name of the thermal printer as shown by Windows, inside the **settings.ini**, under the PRINTER section.

#### Credits

Zebra icon made by <a href="https://www.flaticon.com/authors/flat-icons" title="Flat Icons">Flat Icons</a> from <a href="https://www.flaticon.com/"             title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/"             title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a>

PDF file icon made by <a href="https://www.flaticon.com/authors/smashicons" title="Smashicons">Smashicons</a> from <a href="https://www.flaticon.com/"             title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/"             title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a>

watchdog package made by https://github.com/gorakhargosh/watchdog

PyPDF2 pacakge made by https://github.com/mstamy2/PyPDF2

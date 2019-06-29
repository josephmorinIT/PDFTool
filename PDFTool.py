# =========================== Import Section ===========================
import os
import re
import glob
import fitz
import argparse
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

# -------------------------------------------------> displayBanner
def displayBanner():
# Simple function to display a displayBanner
# Can be disabled if you prefer boring console !

    os.system('clear')
    print("""
  _____  _____  ______ _______          _
 |  __ \|  __ \|  ____|__   __|        | |
 | |__) | |  | | |__     | | ___   ___ | |
 |  ___/| |  | |  __|    | |/ _ \ / _ \| |
 | |    | |__| | |       | | (_) | (_) | |
 |_|    |_____/|_|       |_|\___/ \___/|_|


    """)
    return

# -------------------------------------------------> checkPdf
def checkPDF(file):
# A little function to check if PDF file is Invalid
# Based only on the capacity of PyPDF2 to correctly open the file passed in argument
# Added check extension first
    try:
        # Get extension and basename of given file in argument
        fileExtension = os.path.splitext(file)[1]
        baseName = os.path.basename(file)
        # Simple extension check
        if fileExtension != '.pdf':
            return 'extensionNONOK'
        else:
            # Open pdf for testing correct reading
            with open(file,'rb') as stream:
                # Test the reading capacity
                openPdf = PdfFileReader(stream)
                return 'pdfOK'
    # Except reading error
    except Exception as error:
        return False

# -------------------------------------------------> PDF merger function
def mergerTool(src, dst):
# Simple function to merge pdf files together

    try:
        # Get all PDF files in source path
        allPDF = glob.glob(f"{src}/*.pdf")
        # If pdfFiles array is empty (no PDF detected), return an error message
        if not allPDF:
            print("[!] Not PDF files detected in source directory")
            print(f"[!] Check your source path : {src}")
            return
        # Else if pdfFiles array got only one element (one PDF find)
        elif len(allPDF) == 1:
            print("[!] Cannot merge one PDF file to one PDF...")
            print("[!] Use your mind and add more PDF files")
            return

        # Initialize the merger
        pdfMerger = PdfFileMerger()
        # Loop to get all PDF files and add
        for pdf in allPDF:
            # Get PDF basename (because fullname in each loop can be too much)
            pdfBaseName = os.path.basename(pdf)
            if checkPDF(pdf) == 'pdfOK':
                print(f"[+] Adding [{pdfBaseName}] for merging")
                pdfMerger.append(pdf)

        # Finally write the final PDF to output.pdf file in destination folder
        with open(f"{destination}",'wb') as finalPDF:
            pdfMerger.write(finalPDF)

    # Get exception
    except Exception as error:
        print("\n[!] An error occured during merging :")
        print(f"{error}")

    return


# -------------------------------------------------> getInfo
def getInfo(file,output):
# Simple function to get info about a PDF file
# The method getDocumentInfo does'nt give all informations
# So, with a dictionnary, we can fix it an we can be sure to get all info !

    try:
        # Open file given in argument in RB mode
        with open(file,'rb') as stream:
            # Read file with PdfFileReader
            readPdf = PdfFileReader(stream)
            # Get all info about the document
            allInfo = str(readPdf.getDocumentInfo())
            # Get the number of page...can be usefull
            nbPage = readPdf.getNumPages()

        # Initialization of an empty dictionnary
        infoArray = {}
        # Process to a loop with multi split
        # This first split get the title of information and the value (Author and the given name)
        for info in allInfo.split(','):
            # This second split give the title of the information (Author, Title...)
            reference = info.split(':')[0]
            # With a regex, we extract only text (exclude [], /, quotes...)
            key = str(re.findall('\w+', reference)[0])
            # Finally, replace the second split by nothing, to get the opposit
            value = info.replace(reference,"")
            # Add condition if the value is empty (equal to : '' due to the extraction method...)
            if value == r": ''" or not value:
                value = '?'
            # Add key and value in the dictionnary
            infoArray[key] = value

        # Add a best output with an header
        header = f"Informations about {os.path.basename(file)}"
        # Repeat a char to have a separator
        topSeparator = '=' * len(header)
        # Define a footer section
        footer = f"Total number of pages in document : {nbPage}"
        # Repeat a char to have a separator in case of multi files
        bottomSeparator = '-' * len(footer)

        # Default behaviour, display directly in console
        if output == 'console':

            # Print header and separator
            print(header)
            print(topSeparator)
            # Finally display the content of the dictionnary (keys and values)
            for key in infoArray.keys():
                print(f"{key} {infoArray[key]}")
            # Print the footer and the bottom separator (with 2 new lines)
            print(footer)
            print(f"{bottomSeparator}\n\n")

        # Else if the command line indicate the output is in a log file
        elif output != 'console':
            # With statement to open a file, in append mode (in case of multi PDF file)
            with open(output,'a') as stream:
                # Write header and top separator
                stream.write(f"{header}\n")
                stream.write(f"{topSeparator}\n")
                # Loop on the dictionnary to get keys and values
                for key in infoArray.keys():
                    stream.write(f"{key} {infoArray[key]}\n")
                # Finally write the footer and the bottom separator
                stream.write(f"{footer}\n")
                stream.write(f"{bottomSeparator}\n\n")

    # Catch a possible error...
    except Exception as error:
        print(f"[!] An error occured during get information : ")
        print(f"{error}")
        return

    return

# -------------------------------------------------> splitFile
def splitFile(file,outSplit,page):
# Simple function to extract a specific page of a PDF file
    try:

        # Open input file in reading mode
        with open(f"{file}", 'rb') as streamIn:

            # Initialize reader and writer
            pdfReader = PdfFileReader(streamIn)
            pdfWriter = PdfFileWriter()
            # Read needed page (-1 because number begin at 0...like an index...)
            pdfWriter.addPage(pdfReader.getPage(page-1))
            # Define a name for outfile, based of the page number
            nameOut = f"Page_{page}.pdf"

            # Finally write the output file in the output folder
            with open(f"{outSplit}/{nameOut}", 'wb') as streamOut:
                pdfWriter.write(streamOut)

    # Except a possible error...
    except Exception as error:
        print(f"An error occured when splitting {os.path.basename(file)} :")
        print("{error}")

    return


# -------------------------------------------------> extractImg
def extractImg(file,output):
# Function to extract images from a PDF file
# All images from PDF will be extracted

    # Open pdf file with fitz module
    pdf = fitz.open(filePDF)
    # Loop with the max number of page
    for i in range(len(pdf)):
        # Get image in the page
        for img in pdf.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(pdf, xref)
            if pix.n < 5:       # this is GRAY or RGB
                if os.path.isfile(f"{outputDir}/Image{i}.png"):
                    print(f"[!] The file Image{i}.png yet exist in {outputDir}")
                else:
                    pix.writePNG(f"{outputDir}/Image{i}.png")
                    print(f"[+] Write Image{i}.png")
            else:               # CMYK: convert to RGB first
                if os.path.isfile(f"{outputDir}/Image{i}.png"):
                    print(f"[!] The file Image{i}.png yet exist in {outputDir}")
                else:
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.writePNG(f"{outputDir}/Image{i}.png")
                    print(f"[+] Write Image{i}.png")
                    pix1 = None
            pix = None

    return


# -------------------------------------------------> extractText
def extractText(file,out):
# Function to extract all text from a PDF file
# The result can't work very well
# Depend of the PDF construction

    # Get the baseName (without the extension)
    baseName = (os.path.basename(file)).split('.')[0]

    # Open the PDF file with fitz
    pdf = fitz.open(file)
    # Loop in all page with a range
    for num in range(len(pdf)):
        # Load the page n° num
        page = pdf.loadPage(num)
        # Get text of this page
        text = page.getText()
        # Open the output file, in append mode
        with open(f"{out}/{baseName}.txt", 'a') as output:
            # Define a header to know from where the text is extract
            header = f"========================================== From page {num + 1} ==========================================\n"
            # Write header first
            output.write(header)
            # Finally write the text of the page in the ouput file
            output.write(text)

    return



# -------------------------------------------------> checkInputFile
def checkInputFile(file):
# Simple function to check if an input file exist
# Used in all functionality of the script

    if not os.path.isfile(file):
        print(f"[!] The file {file} does'nt exist")
        print(f"[!] Check your path")
        return False
    elif os.path.isfile(file):
        return True

# -------------------------------------------------> checkOutputFolder
def checkOutputFolder(path):
# Simple function to check if an output folder (in argument) exist
# Used to check an output directory before processing

    if not os.path.isdir(path):
        print(f"[!] The directory {path} does'nt exist")
        print(f"[!] Check your path")
        return False
    elif os.path.isdir(path):
        return True



# ==============================================================
# ======================== Main section ========================
# ==============================================================

# Ideas from :
# - https://indianpythonista.wordpress.com/2017/01/10/working-with-pdf-files-in-python/
# - https://www.geeksforgeeks.org/working-with-pdf-files-in-python/
# - http://www.blog.pythonlibrary.org/2018/04/10/extracting-pdf-metadata-and-text-with-python/
# - https://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python (post 15)
# - https://pymupdf.readthedocs.io/en/latest/tutorial/


# ================= Arg Parse section =================

# Initialization of the arguments parser
parser = argparse.ArgumentParser(
#usage=argparse.SUPPRESS,
formatter_class=argparse.RawDescriptionHelpFormatter,
description="""PDFTool is a simple tool to manage PDF files.\n
- PDFTool.py merge --help display help about merging
- PDFTool.py split --help display help about splitting
- PDFTool.py extract --help display help about extraction (text or images)
- PDFTool.py info --help display help about how to get info about a PDF

------------------------------------------------------------------------------
"""
)

# Initialize a subparser, with command destination
subParser = parser.add_subparsers(title="command",dest="command")

# Merge subparser
mergeParser = subParser.add_parser('merge',help='Merge PDF files together')
mergeParser.add_argument('--mergeIn',help='Source must be a folder',required=True)
mergeParser.add_argument('--mergeOut',help='Destination must be a file (PDF)',required=True)

# Split subparser
splitParser = subParser.add_parser('split',help='Split specific page of PDF file, or all')
splitParser.add_argument('--splitIn',help='Source file to split',required=True)
splitParser.add_argument('--splitOut', help='Destination folder',required=True)
splitParser.add_argument('--num',help='The number of page or "all"',required=True)

# Extraction subparser
extractParser = subParser.add_parser('extract',help='Extract text or images from a PDF file')
extractParser.add_argument('--extIn', help='Source file or folder for extraction',required=True)
extractParser.add_argument('--extType', help='Type of the extract',choices=['img','text'],required=True)
extractParser.add_argument('--extOut',help='Destination file or folder for extraction',required=True)

# Getting info subparser
infoParser = subParser.add_parser('info',help='Get info about a PDF document')
infoParser.add_argument('--infoIn',help='Source file or folder to get info',required=True)
infoParser.add_argument('--infoOut',help='Destination dump file (display in console by default)',default='console',required=True)

# Finally parse arguments
args = parser.parse_args()


# With a banner, it's a better ! ><))))°>
displayBanner()

## Define action with command detected

# Merge action
if args.command == 'merge':
    print('Merge !')
# Split action
elif args.command == 'split':
    print('Split !')
# Extract action
elif args.command == 'extract':
    print('Extract !')
# Info action
elif args.command == 'info':
    print('Info !')



# Define somes variables
#source = r'/home/scratch/Downloads/sources'
#destination = r'/home/scratch/Downloads/destination/output.pdf'


#mergerTool(source,destination)
#checkPDF(file)


# ================ Test getInfo function ================
#getInfoSRCFOLDER = r'/home/scratch/Downloads/sources/'
#getInfoSINGLEFILE = r'/home/scratch/Downloads/sources/file.pdf'
#getInfoFILEOUTPUT = r'/home/scratch/Downloads/destination/output.txt'
#getInfoCONSOLEOUTPUT = 'console'

#if os.path.isdir(folder):
#    for file in glob.glob(f"{folder}/*.pdf"):
#        print(file)
#        getInfo(file, output)
#else:
#    getinfo(file,output)

# ================ Test splitFile function ================
#inputFile = r'/home/scratch/Downloads/sources/file.pdf'
#outputFolder = r'/home/scratch/Downloads/destination'
#page = 'all'
#page = 2

#if page == 'all':
#    readPdf = PdfFileReader(inputFile)
#    for page in range(1,readPdf.getNumPages() + 1):
#        splitFile(inputFile, outputFolder, page)
#else:
#    splitFile(inputFile,outputFolder,page)


# ================ Test extractImg function ================
#filePDF = r'/home/scratch/Downloads/sources/file.pdf'
#outputDir = r'/home/scratch/Downloads/destination'
#extractImg(filePDF,outputDir)

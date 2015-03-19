from StringIO import StringIO

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed


def pdf_text(pdf_file):
    """
    Extracts text from a PDF.
    """
    rsrcmgr = PDFResourceManager(caching=True)
    outp = StringIO()
    device = TextConverter(rsrcmgr, outp, codec='utf-8', laparams=LAParams())
    with open(pdf_file, 'rb') as f:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        try:
            for page in PDFPage.get_pages(f, set(), maxpages=0, caching=True, check_extractable=True):
                interpreter.process_page(page)
        except PDFTextExtractionNotAllowed:
            pass
    device.close()
    text = outp.getvalue()
    outp.close()
    return text.strip().decode('utf-8')

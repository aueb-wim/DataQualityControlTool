# qcexport.py
""" Module with helper functions for exporting the statistical reports
of the MIP local Quality Control Tool
"""
'''
import os.path
from pylatex import Document, Section, Foot, MiniPage, \
    LongTabu, LineBreak, NewPage, Tabularx, TextColor, simple_page_number
from pylatex.utils import NoEscape
'''

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from .config import LOGGER


######### Functions for exporting in pdf using LaTex #########

def fill_stat(doc, df):
    """Helper fucntion returns a LaTex Table from pandas df.

    Arguments:
    :param doc: pylatex document class
    :parma df: pandas dataframe
    """
    with doc.create(LongTabu('X[2l] X[r]',
                             row_height=1.5)) as data_table:
        data_table.add_hline()
        data = df.reset_index(level=0)
        data = data.values.tolist()
        totalrows = len(data)
        for i in range(totalrows):
            if (i % 2) == 0:
                data_table.add_row(data[i], color='lightgray')
            else:
                data_table.add_row(data[i])

'''
def latex2pdf(filepath, dstats, listvstats, exportpdf=False):
    """Exports dataset statistical report in tex and pdf.

    Arguments:
    :param filename: filepath of the pdf file to export
    :param dstats: pandas dataframe with dataset statistics
    :param vstats: pandas dataframe from qctab.VariableStats.vstats.
    """
    namefile = dstats.at['name_of_file', 0]
    geometry_options = {
        'head': '40pt',
        'margin': '0.5in',
        'bottom': '0.6in',
        'paper': 'a4paper',
        'includefoot': True
    }
    doc = Document(page_numbers=True, geometry_options=geometry_options)
    title = 'Statistical Report of {0} file'.format(namefile)
    doc.preamble.append(NoEscape(r'\usepackage{bookmark}'))
    with doc.create(Section(title)) as main_section:
        fill_stat(main_section, dstats)
    doc.append(NewPage())
    for vstats in listvstats:
        for variable in vstats.index:
            new_title = 'Statistical Report of variable "{0}"'.format(variable)
            with doc.create(Section(new_title)) as var_section:
                vstat = vstats.loc[variable].to_frame()
                fill_stat(var_section, vstat)
            doc.append(NewPage())

    if exportpdf:
        doc.generate_pdf(filepath)
    else:
        doc.generate_tex(filepath)
'''
############ Functions for exporting pdfs using weasyprint library ########


def html2pdf(filepath, dstats, listvstats):
    my_path = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(my_path, 'data')
    css_path = os.path.join(my_path, 'data', 'style.css')
    documents = []
    env = Environment(loader=FileSystemLoader(env_path))
    template = env.get_template('variable_report.html')
    dtemplate_vars = {'title': 'Report',
                      'df_title': 'Dataset Statistical Report',
                      'dataset_table': dstats.to_html()}
    html_out = template.render(dtemplate_vars)
    documents.append(HTML(string=html_out).render(stylesheets=[css_path]))

    for vstats in listvstats:
        for variable in vstats.index:
            vstat = vstats.loc[variable].to_frame()
            template_vars = {'title': 'Report',
                             'df_title': 'Statistical Report of variable "{0}"'.format(variable),
                             'dataset_table': vstat.to_html()}
            html_out = template.render(template_vars)
            weasyhtml = HTML(string=html_out)
            documents.append(weasyhtml.render(stylesheets=[css_path]))

    all_pages = [p for doc in documents for p in doc.pages]
    documents[0].copy(all_pages).write_pdf(target=filepath)

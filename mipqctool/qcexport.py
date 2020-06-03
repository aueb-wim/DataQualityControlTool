# -*- coding: utf-8 -*-
# qcexport.py
""" Module with helper functions for exporting the statistical reports
of the MIP local Quality Control Tool
"""

import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from .config import LOGGER

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

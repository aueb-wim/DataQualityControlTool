# qcexport.py

from pylatex import Document, PageStyle, Section, Foot, MiniPage, \
    LongTabu, LineBreak, NewPage, Tabularx, TextColor, simple_page_number
from pylatex.utils import bold, NoEscape

def fill_stat(doc, stat):
    with doc.create(LongTabu('X[2l] X[r]',
                             row_height=1.5)) as data_table:
        data_table.add_hline()
        data = stat.reset_index(level=0)
        data = data.values.tolist()
        totalrows = len(data)
        for i in range(totalrows):
            if (i % 2) == 0:
                data_table.add_row(data[i], color='lightgray')
            else:
                data_table.add_row(data[i])

def latexpdf(filepath, dname, dstats, vstats):
    geometry_options = {
        'head': '40pt',
        'margin': '0.5in',
        'bottom': '0.6in',
        'paper': 'a4paper',
        'includefoot': True
    }
    doc = Document(page_numbers=True, geometry_options=geometry_options)
    title = 'Statistical Report of {0} file'.format(dname)
    doc.preamble.append(NoEscape(r'\usepackage{bookmark}'))
    with doc.create(Section(title)) as main_section:
        fill_stat(main_section, dstats)
    doc.append(NewPage())
    for variable in vstats.index:
        new_title = 'Statistical Report of variable "{0}"'.format(variable)
        with doc.create(Section(new_title)) as var_section:
            vstat = vstats.loc[variable].to_frame()
            fill_stat(var_section, vstat)
        doc.append(NewPage())

    doc.generate_pdf(filepath)

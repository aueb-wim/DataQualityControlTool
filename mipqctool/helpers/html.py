# -*- coding: utf-8 -*-
# html.py

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from jinja2 import Template

from mipqctool.config import LOGGER


def tupples2table(pairs):
    """Returns an html table str
    Arguments:
    :param pairs: list of tupples, like dict.items()
    """
    html_text = """<table width="100%">
{% for pair in pairs %}
    <tr>
        <td>{{ pair[0] }}</td>
        <td>{{ pair[1] }}</td>
    </tr>
    {% endfor %}
</table>"""
    table_tpl = Template(html_text)
    return table_tpl.render(pairs=pairs)

def list2parag(values):
    """Returns a html paragraph with the list values"""
    html_text="""<p>{% for value in values %}{{ value }}, {% endfor %}</p>"""
    parag_tmp = Template(html_text)
    return parag_tmp.render(values=values)
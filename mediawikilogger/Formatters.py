from IPython import embed
import matplotlib
from numpy import ndarray
import string
from numpy import random
from matplotlib import figure
import pandas

def filelink(col):
    """
    Converts a list of strings into mediawiki filelinks.

    :param col: list of strings (usually filenames)
    :return: reformated col
    """
    return ["[[File:%s]]" % (e, ) for e in col]

def medialink(col):
    """
    Converts a list of strings into mediawiki medialinks.

    :param col: list of strings (usually filenames)
    :return: reformated col
    """
    return ["[[Media:%s]]" % (e, ) for e in col]


def id_generator(size=6, chars=list(string.ascii_uppercase + string.digits)):
    return ''.join(random.choice(chars) for x in range(size))



def code_formatter(code_dict):
    """
    Formats code for mediawiki.

    :param code_dict: Dictionary that should contain keys 'lang', 'code', and 'title'.
                      All values should be strings.
    """

    return """<div class="toccolours mw-collapsible mw-collapsed">
                    \n[[File:%(lang)s.png|40px]] '''%(title)s'''\n
                    <div class="mw-collapsible-content">\n
                        <source lang=\"%(lang)s\">\n%(code)s\n</source>\n
                    </div>\n</div>""" % code_dict

def dataframe_formatter(df, sortable=True, style=None, index=False, col_mapper=None):
    """
    Formats pandas dataframes for mediawiki.

    :param df: pandas dataframe
    :param sortable: should the resulting table be sortable or not?
    :param style: css style parameters for the table
    :param index: should the index be included or not?
    :param col_mapper: dictionary of functions to remap columns of the dataframe
    :return: formated dataframe string
    """
    df = df.copy()

    if col_mapper is not None:
        for col, f in col_mapper.items():
            df[col] = f(df[col])

    if style is None:
        style = "\"\""
    else:
        style = "style=\"%s;\"" % (';'.join(["%s:%s" % (str(k), str(v)) for k,v in style.iteritems()]), )

    format_dict = {
        'sortable': sortable*'sortable',
        'columns': index*" !! " +  " !! ".join([str(e) for e in df.columns]),
        'style': style
    }
    s = ["""{| class=\"wikitable %(sortable)s\" style=%(style)s \n|-\n! %(columns)s """ % format_dict]

    n = len(df.index.names)
    for idx, row in df.T.iteritems():
        if index:
            if n > 1:
                row = ("'''" +  ", ".join(idx) + "'''",) + tuple(row)
            else:
                row = ("'''" +  str(idx) + "'''",) + tuple(row)
        s.append( "|-\n| %s " % (" || ".join(map(str, row)),) )
    s.append("|}")
    return "\n".join(s)


def figure_formatter(fig, filename=None, width=800, format='png'):
    if filename is None:
        filename = id_generator(20) + '.' + format
    fig.savefig(filename)
    return "[[File:%s]]" % (filename, )



def gallery_formatter(figures, format='png'):
    if type(figures) == list:
        captions = len(figures)*['no caption given']
    else:
        figures, captions = zip(*figures.items())

    s = "<gallery>\n"
    for fig, cap in zip(figures,captions):
        if not isinstance(fig,str):
            filename = id_generator(20) + '.' + format
            fig.savefig(filename)
        else:
            filename = fig
        s += "File:%s|%s\n" % (filename,cap)

    s += "</gallery>\n"
    return s

format_factory = {
    figure.Figure: figure_formatter,
    pandas.core.frame.DataFrame: dataframe_formatter
}

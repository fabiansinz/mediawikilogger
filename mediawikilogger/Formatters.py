from numpy import ndarray


def code_formatter(code_dict):
    """
    Formats code.

    :param code_dict: Dictionary that should contain keys 'lang', 'code', and 'title'.
                      All values should be strings.
    """

    return """<div class="toccolours mw-collapsible mw-collapsed">
                    \n[[File:%(lang)s.png|40px]] '''%(title)s'''\n
                    <div class="mw-collapsible-content">\n
                        <source lang=\"%(lang)s\">\n%(code)s\n</source>\n
                    </div>\n</div>""" % code_dict


def dict_formatter(dict_dict):
    c = len(cols) + 1 - int(rows is None)
    s = """{| class=\"wikitable sortable\"\n|-\n! %s \n""" % \
        (" !! ".join(int(rows is not None) * [''] + [str(e) for e in cols]),)
    for k, row in enumerate(cont):
        if isinstance(row,list) or type(row) is ndarray:
            r = [str(c) for c in row]
        else:
            r = [str(row)]
        if rows is not None:
            r = [rows[k]] + r
        s += "|-\n| %s \n" % (" || ".join(r),)
    s += "|}"
    return s
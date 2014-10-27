import re
import sys
import inspect
import datetime
import string
import random
import os
import socket
from IPython import embed
import pandas as pd
import git
import importlib

from mediawikilogger.Formatters import code_formatter, format_factory, dataframe_formatter, gallery_formatter


class MediaWikiLogger:
    """
    MediaWikiLogger is a simple class that, when instantiated, extracts context information from a python script
    and outputs it in mediawiki format when printed or saved.

    Every line comment that starts with #@ will be included in the mediawiki text.

    Additionally, matplotlib figures, pandas dataframes, and lists of matplotlib figures can be added to the
    logger.
    """
    def __init__(self, categories=None):
        self.content = {}
        self.mods = {}
        self._parse_comments(sys.argv[0])
        self._parse_modules(sys.argv[0])
        self.start_time = datetime.datetime.now()
        self.categories = categories

        self.python_version = "python %i.%i.%i %s" % (sys.version_info.major, sys.version_info.minor,
                                                      sys.version_info.micro, sys.version_info.releaselevel)

        self.directory = os.path.realpath(inspect.getouterframes(inspect.currentframe())[-1][1])


    def _add_content(self, lineNo, cont, formatfunc=None):
        if formatfunc is None:
            formatfunc = lambda x: x

        if lineNo in self.content:
            raise KeyError("Line Number %i already exists!" % lineNo)
        else:
            tmp = formatfunc(cont)
            self.content[lineNo] = tmp
            return tmp

    def add_code(self, obj=None, file=None, title='no code title given', lang=None):
        """
        Adds the code of the file itself, a python function/module, or a file into the logging result.

        :param obj: Python function or module.
        :param file: Filename of a file containing code.
        :param title: Title for the code element on the mediawiki page.
        :param lang: programming language
        """
        if obj is not None:
            L = inspect.getsource(obj)
        elif file is not None: 
            with open(file) as fid:
                L = fid.read()
        else:
            with open(sys.argv[0]) as fid:
                L = ''.join([l for l in fid.readlines() if not l.lstrip().startswith("#@")])
            
        return self.add(code_formatter({'code':L, 'title':title, 'lang': 'python' if lang is None else lang}))

    def add_repo(self, name, direc):
        """
        Adds a git repository to the information.

        :param name: Name of the respository (can be freely chosen)
        :param direc: absolute path of the git directory
        """
        try:
            repo = git.Repo(direc)

            self.mods[name]['info'].append("branch " + repo.active_branch)
            self.mods[name]['info'].append("commit " + str(repo.commits(repo.active_branch)[0]))
            if repo.git.status().find("modified") >= 0:
                self.mods[name]['info'].append("modified files")
        except:
            pass

    def _parse_modules(self, f):
        with open(f, 'r') as fid:
            L = fid.readlines()
            mods = self.mods
            for l in L:
                if l.startswith("from") or l.startswith("import"):
                    hits =  re.findall("([a-zA-Z0-9_\.]+)+,?", l)
                    mymods = []
                    for i, h in enumerate(hits):
                        if h == 'as':
                            break
                        if h == 'import' and i > 0:
                            break
                        if h not in ['from', 'import']:
                            mymods.append(h)

                    for mymod in mymods:
                        name = mymod.split('.')[0]
                        if not mods.has_key(name):
                            mod = {}
                            mod['name'] = name
                            mod['info'] = []
                            mods[name] = mod

                            themod = importlib.import_module(name)
                            try:
                                directory = os.path.dirname(inspect.getfile(themod))
                                self.add_repo(name, directory)
                            except TypeError:
                                pass

                            if hasattr(themod, '__version__'):
                                mod['info'].append('v. ' + themod.__version__)
                            mods[name] = mod
            
    def add(self, element, **kwargs):
        """
        Adds an element to the logging result.

        :param element: new element in the logging results
        :param kwargs: if formatfunc is in the kwargs, the element is formated with
                        that function other kwargs are passed to this format function.
        """
        if 'formatfunc' in kwargs:
            formatfunc = kwargs.pop('formatfunc')
        elif type(element) == str:
            formatfunc = lambda x: x
        else:
            formatfunc = format_factory[type(element)]

        c = inspect.currentframe()
        return self._add_content(inspect.getouterframes(c)[-1][2], formatfunc(element, **kwargs))


    def add_gallery(self, gallery, **kwargs):
        """
        Adds a mediawiki gallery of figures.

        :param gallery: Either a list of figure handles, a dictionary with figure handles as keys and captions
                as values, or a dictionary with filenames of already saved figures as keys and captions as values.
        """
        self.add(gallery, formatfunc=gallery_formatter, **kwargs)

    def __add__(self, other):
        return self.add(other)

    def _parse_comments(self, f):
        curr_str = ""
        old_line = -5
        with open(f, 'r') as fid:
            for k, l in enumerate(fid.readlines()):
                l = l.lstrip()
                if l.startswith("#@"):
                    if old_line + 1 == k:
                        curr_str += " " + l[2:].strip()
                        old_line = k
                    else:
                        if len(curr_str) > 0:
                            self._add_content(old_line,  "\n" + curr_str + "\n")
                        curr_str = l[2:].strip()
                        old_line = k
            else:
                if len(curr_str) > 0:
                    self._add_content(old_line, "\n" + curr_str + "\n")

                        
    def __str__(self):
        info = pd.DataFrame(columns=["Parameter", "Settings"])
        now = datetime.datetime.now()
        counter = 0

        ret = ["[[Category:%s]]"  % (e,) for e in self.categories]

        info.loc[counter] = ['Running time', "%s - %s" % (str(self.start_time), str(now))]
        counter += 1


        info.loc[counter] = ['Running Directory', self.directory ]
        counter += 1

        info.loc[counter] = ['Host', socket.gethostname()]
        counter += 1

        info.loc[counter] = ['Python version', self.python_version]
        counter += 1

        infofunc = lambda  a: "(" + ", ".join(a) + ')' if len(a) > 0 else ''
        info.loc[counter] = ['Libraries',
                       "\n" + "\n".join(["* %s %s" % (e['name'], infofunc(e['info'])) for e in self.mods.values()])]
        counter += 1

        info.set_index("Parameter", inplace=True)
        ret.append("=Information=\n\n%s" % (dataframe_formatter(info, index=True), ))

        for _, c in sorted(self.content.items(), key=lambda e: e[0]):
            ret.append(c)

        return "\n".join(ret)


    def save(self, filename):
        """
        Saves the mediawiki page to a file.

        :param filename: filename  
        """
        with open(filename, 'w') as fid:
            fid.write(self.__str__())


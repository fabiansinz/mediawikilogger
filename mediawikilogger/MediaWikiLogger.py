import sys
import imp
import inspect
import datetime
import string
import random
import os
import socket

import matplotlib

import git
from mediawikilogger.Formatters import code_formatter, figure_formatter, format_factory


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))





def gallery_format(elem):
    figformat = elem[2]
    captions = elem[1]
    elem = elem[0]
    if captions is None:
        captions = len(elem)*['no caption']
    
    s = "<gallery>\n"
    for fig,cap in zip(elem,captions):
        if not isinstance(fig,str):
            filename = id_generator(20) + '.' + figformat
            fig.savefig(filename)
        else:
            filename = fig
        s += "File:%s|%s\n" % (filename,cap)
        
    s += "</gallery>\n"
    return s


class MediaWikiLogger:

    def __init__(self, categories=None):
        self.content = {}
        self.mods = {}
        self._parse_comments(sys.argv[0])
        self._parse_modules(sys.argv[0])
        self.startTime = datetime.datetime.now()
        self.categories = categories

        self.python_version = "python %i.%i.%i %s" % (sys.version_info.major, sys.version_info.minor,
                                                      sys.version_info.micro, sys.version_info.releaselevel)

        self.directory = os.path.realpath(inspect.getouterframes(inspect.currentframe())[-1][1])


    def add_content(self, lineNo, cont, formatfunc=None):
        if formatfunc is None:
            formatfunc = lambda x: x

        if lineNo in self.content:
            raise KeyError("Line Number %i already exists!" % lineNo)
        else:
            tmp = formatfunc(cont)
            self.content[lineNo] = tmp
            return tmp

    def add_code(self, obj=None, file=None, title='no code title given', lang=None):
        if obj is not None:
            L = inspect.getsource(obj)
        elif file is not None: 
            with open(file) as fid:
                L = fid.read()
        else:
            with open(sys.argv[0]) as fid:
                L = fid.readlines()
                L = '\n'.join([l for l in fid.readlines() if not l.lstrip().startswith("#@")])
            
        self.add(code_formatter({'code':L, 'description':title, 'lang': 'python' if lang is None else lang}))

    def add_repo(self, name, direc):
        """
        Adds a repository to the repository list of the Journal.
        """
        # check whether it is a git version
        try:
            repo = git.Repo(direc)
            self.mods[name]['info'].append("commit " + repo.head.commit.name_rev)
            self.mods[name]['info'].append("branch " + repo.git.branch().split()[1])
            if repo.git.status().find("modified") >= 0:
                self.mods[name]['info'].append("modified files")
        except:
            pass

    def _parse_modules(self, f):
        with open(f, 'r') as fid:
            L = fid.readlines()
            mods = self.mods
            for l in L:
                if l.lstrip().startswith("import") or (l.lstrip().startswith("from") and "import" in l):
                    name = l.split()[1].split('.')[0]
                    if not mods.has_key(name):
                        mod = {}
                        mod['name'] = name
                        mod['info'] = []
                        mods[name] = mod

                        info = imp.find_module(mod['name'])
                        
                        self.add_repo(name, info[1])

                        # get versions if possible
                        tmp = imp.load_module(mod['name'], *info)
                        
                        if hasattr(tmp, '__version__'):
                            mod['info'].append('v. ' + tmp.__version__)
                        tmp = None
                   

                        mods[name] = mod
            
    def add(self, element, **kwargs):
        c = inspect.currentframe()
        if type(element) != str:
            return self.add_content(inspect.getouterframes(c)[-1][2], format_factory[type(element)](element, **kwargs))
        else:
            return self.add_content(inspect.getouterframes(c)[-1][2], element)

    def _parse_comments(self, f):
        with open(f, 'r') as fid:
            for k, l in enumerate(fid.readlines()):
                l = l.lstrip()
                if l.startswith("#@"):
                    self.add_content(k, l[2:].strip())
                        

    # TODO rewrite str
    def __str__(self):
        now = datetime.datetime.now()
        infofunc = lambda  a: "(" + ", ".join(a) + ')' if len(a) > 0 else ''
        libs = "\n" + "\n".join(["* %s %s" % (e['name'], infofunc(e['info'])) for e in self.mods.values()])
        
        ret = """
{{experiment
| started = %02i/%02i/%04i
| finished = %02i/%02i/%04i
| directory = %s
| host = %s
| proglangs = %s
| libs = %s
}}

""" % (self.startTime.month, self.startTime.day, self.startTime.year, \
               now.month, now.day, now.year,  self.directory,socket.gethostname(), self.category,
               self.subcategory, self.python_version, libs, self.data)
        out = list(self.content)
        ret += "\n\n".join([e[2](e[1]) for e in out])
        ret = ret.replace("\\\n\n", " ")
        return ret
        
    def save(self, filename):
        """
        Saves the Journal to a text file filename.
        """
        with open(filename, 'w') as fid:
            fid.write(self.__str__())


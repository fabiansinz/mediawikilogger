import sys
sys.path.append('../')
from mediawikilogger import MediaWikiLogger
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

mwlog = MediaWikiLogger(['example', 'demonstration'])

#@ = Gallery with prespecified filenames =

gallery = {}
for i in range(3):
    fig, ax = plt.subplots()
    ax.plot(np.random.randn(10))
    fig.savefig('%02i.jpg' % (i, ))
    gallery['%02i.jpg' % (i,)] = '%ith image' % (i,)

mwlog.add_gallery(gallery)

#@ = Gallery with unspecified filenames =
gallery = {}
for i in range(3):
    fig, ax = plt.subplots()
    ax.plot(np.random.randn(10))
    gallery[fig] = '%ith image' % (i,)

mwlog.add_gallery(gallery)

#@ = Gallery with unspecified filenames and no titles =
gallery = []
for i in range(3):
    fig, ax = plt.subplots()
    ax.plot(np.random.randn(10))
    gallery.append(fig)
mwlog.add_gallery(gallery)


mwlog.save('gallery_example.mw')
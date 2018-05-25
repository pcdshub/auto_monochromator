from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from random import random
from functools import partial
from collections import deque
from pcdsdevices import beam_stats
from auto_monochromator.rapid_stats import RapidHist
import numpy as np
from tornado.ioloop import PeriodicCallback
import time

def modify_doc(doc,plot_data):
    
    #d = figure(x_range=(0, 100), y_range=(0, 100))
    #d = figure()
    
    #d = figure(x_range=(510, 550),y_range=(-50,500))
    d = figure(y_range=(-50,500))
    k = d.quad(
        top=[],
        bottom=[],
        left=[],
        right=[],
        fill_color="#036564",
        line_color="#033649"
    )
    ks = k.data_source
    class s:
        pass
    
    m = s()
    m.i = 0
    '''
    hist = RapidHist(
        # 1000 just seems to be the magic number for the accel_ev 
        maxlen=1000,
        bins = np.arange(6850,6950,.5)
    )
    '''

    def callback(k_obj, hist_data):
        k_obj.i += 1
        print(k_obj.i)
        nd = dict()
        nd['top'] = hist_data.hs
        nd['bottom'] = np.zeros(len(hist_data.hs))
        nd['left'] = hist_data.bins[:-1]
        nd['right'] = hist_data.bins[1:]
        ks.data = nd
    
    
    # add a button widget and configure with the call back
    # button = Button(label="Press Me")
    # button.on_click(callback)
    doc.add_periodic_callback(
        partial(callback,k_obj = m,hist_data=plot_data),
        100
    )
    # put the button and plot in a layout and add to the document
    doc.add_root(column(d))

def pull_data(ds, hist, out):
    print('recalc plot\t', len(ds),'\t', time.ctime(),end='\t')
    hist.push(ds)
    print(len(hist._data))
    ds.clear()
    out.hs, out.bins = hist.hist()

class Carrier:
    def __init__(self):
        self.hs = None
        self.bins = None

# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
def launch_server():

    inc_data_block = deque(maxlen=1000)
    stats = beam_stats.BeamStats()

    def append_to_data_block(*args,**kwargs):
        kwargs['inc_data_block'].append(kwargs['value'])
   


    # Apply one of these sections for each PV being watched:

    stats.accel_ev.subscribe(
        partial(append_to_data_block,inc_data_block=inc_data_block)
    )
    '''
    stats.mj.subscribe(
        partial(append_to_data_block,inc_data_block=inc_data_block)
    )
    '''


    hist = RapidHist(
        maxlen=1000,
        bins = np.arange(9450,9550,1),
        #bins = np.arange(-.1,.1,.005),
    )
    
    m = Carrier()

    server = Server(
        {
            '/': partial(modify_doc,plot_data=m),
        },
        allow_websocket_origin=["localhost:5006"],
        num_procs=1
   )
    server.start()


    print('Opening Bokeh application on http://localhost:5006/')
    #server.io_loop.PeriodicCallback(random_print,500).start()
    pcall = PeriodicCallback(
        partial(pull_data, ds=inc_data_block, hist=hist, out=m),
        100
    )
    pcall.start()
    print(type(server.io_loop))
    #server.io_loop.add_callback(server.show, "/")
    try:
        server.io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        server.io_loop.stop()

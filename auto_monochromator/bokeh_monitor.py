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
from auto_monochromator.rapid_stats import RapidHist, RapidTransmissionHist
from auto_monochromator.event_builder import basic_event_builder
import numpy as np
from tornado.ioloop import PeriodicCallback
import time
import pandas as pd

def modify_doc(doc,plot_data,y_range=(-50,500)):
    d = figure(y_range=y_range)
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
        500
    )
    # put the button and plot in a layout and add to the document
    doc.add_root(column(d))

def handle_data(ds, hist, out):
    """
    Pull Data from the data source (ds), clear the data source, push the data
    into the hist, and generate the hist.
    """
    print('recalc plot\t', len(ds),'\t', time.ctime(),end='\t')
    hist.push(ds)
    print(len(hist._data))
    ds.clear()
    out.hs, out.bins = hist.hist()

def handle_t_data(ds, dst, dsw, dswt, hist, out):
    """
    Pull Data from the data source (ds), clear the data source, push the data
    into the hist, and generate the hist.
    """
    print(len(ds),len(dst),len(dsw),len(dswt),sep='\t')
    data = pd.Series(ds,index=dst)
    weights = pd.Series(dsw,index=dswt)
    zipped = basic_event_builder(data=data,weights=weights)
    hist.push(zipped['data'],zipped['weights'])
    ds.clear()
    dst.clear()
    dsw.clear()
    dswt.clear()
    _, _, out.hs, out.bins = hist.hist()
    out.hs = out.hs * 1.0/sum(out.hs)

class Carrier:
    def __init__(self):
        self.hs = None
        self.bins = None

# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
def launch_server():

    stats = beam_stats.BeamStats()

    def append_to_data_block(*args,**kwargs):
        kwargs['inc_data_block'].append(kwargs['value'])
    
    def append_to_data_block_t(*args,**kwargs):
        kwargs['inc_value'].append(kwargs['value'])
        kwargs['inc_time'].append(kwargs['timestamp'])
   

    ###############################################################
    # Apply one of these sections for each graph being being made #
    ###############################################################
    
    # Acquire EPICS data and generate plot for Accelerator reported energy
    # Store inbound data in this deque
    accel_ev_data_block = deque(maxlen=1000)
    # Attach this method to the PV to aggregate data in the deque
    stats.accel_ev.subscribe(
        partial(append_to_data_block, inc_data_block=accel_ev_data_block)
    )
    # Define the histogram to be plotted
    accel_ev_hist = RapidHist(
        maxlen=1000,
        bins = np.arange(9450,9550,1),
    )
    # Create object for sending histogram data to draw method
    accel_ev_carry = Carrier()
    # Schedule the data-acquiring and regeneration of the histogram
    accel_ev_call = PeriodicCallback(
        partial(
            handle_data, 
            ds=accel_ev_data_block, 
            hist=accel_ev_hist,
            out=accel_ev_carry
        ),
        500
    )

    # Acquire EPICS data and generate plot for Transmission plots
    maxlen=1000
    # Store inbound data in this deque
    t_accel_db = deque(maxlen=maxlen)
    t_accel_db_time = deque(maxlen=maxlen)
    t_gmd_db = deque(maxlen=maxlen)
    t_gmd_db_time = deque(maxlen=maxlen)
    # Attach this method to the PV to aggregate data in the deque
    stats.accel_ev.subscribe(
        partial(append_to_data_block_t,inc_value=t_accel_db,inc_time=t_accel_db_time)
    )
    stats.xpp_ipm2.subscribe(
        partial(append_to_data_block_t,inc_value=t_gmd_db,inc_time=t_gmd_db_time)
    )
    # Define the histogram to be plotted
    t_hist = RapidTransmissionHist(
        maxlen=1000,
        bins = np.arange(9450,9550,1),
    )
    # Create object for sending histogram data to draw method
    t_carry = Carrier()
    # Schedule the data-acquiring and regeneration of the histogram
    t_call = PeriodicCallback(
        partial(
            handle_t_data,
            ds=t_accel_db,
            dst=t_accel_db_time,
            dsw=t_gmd_db, 
            dswt=t_gmd_db_time,
            hist=t_hist,
            out=t_carry),
        500
    )

    
    server = Server(
        {
            '/': partial(modify_doc,plot_data=accel_ev_carry),
            '/b': partial(modify_doc,plot_data=t_carry,y_range=(-.2,.2)),
        },
        allow_websocket_origin=["localhost:5006"],
        # num_procs must be 1 for tornado loops to work correctly 
        num_procs=1,
    )
    server.start()


    print('Opening Bokeh application on http://localhost:5006/')
    #server.io_loop.PeriodicCallback(random_print,500).start()
    
    accel_ev_call.start()
    t_call.start() 
    # Use the following command to automatically start a browser
    # server.io_loop.add_callback(server.show, "/")

    # Run indefinitely 
    try:
        server.io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        server.io_loop.stop()

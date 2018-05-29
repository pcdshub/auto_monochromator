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
import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def single_plot(doc,plot_data,y_range=(-50,500)):
    """
    Generate/update single page w/ single histogram 
    """
    # Each graph begins with a figure
    # fig = figure(y_range=y_range)
    fig = figure()
    # Add the histogram to this graph
    hist_plot = fig.quad(
        top=[],
        bottom=[],
        left=[],
        right=[],
        fill_color="#036564",
        line_color="#033649"
    )

    hist_data_source = hist_plot.data_source

    class stateful_data_container:
        pass
    
    counter = stateful_data_container()
    counter.i = 0

    def callback(count_obj, hist_data):
        count_obj.i += 1
        new_hist_data = dict()
        new_hist_data['top'] = hist_data.hs
        new_hist_data['bottom'] = np.zeros(len(hist_data.hs))
        new_hist_data['left'] = hist_data.bins[:-1]
        new_hist_data['right'] = hist_data.bins[1:]
        # Push the data to the plot 
        hist_data_source.data = new_hist_data
    
    doc.add_periodic_callback(
        partial(callback, count_obj=counter, hist_data=plot_data),
        500
    )

    # place the plot in the page
    # doc.add_root(column([fig],sizing_mode='stretch_both'))
    return fig


def single_plot_mgr(doc,plot_data,y_range=(-50,500)):
    fig = single_plot(doc,plot_data,y_range)
    doc.add_root(column([fig],sizing_mode='stretch_both'))


def double_plot_mgr(doc, inc_plot_data, ts_plot_data, y_range=(-50,500)):
    inc_fig = single_plot(doc, inc_plot_data,y_range)
    ts_fig = single_plot(doc,ts_plot_data,(-.2,.2))
    ts_fig.x_range = inc_fig.x_range
    doc.add_root(column([inc_fig,ts_fig],sizing_mode='stretch_both'))


def double_plot(doc,inc_plot, out_plot, y_range=(-50,500)):
    pass


class plot_package:
    def __init__(self, maxlen, bins, title='', y_range=None):
        pass 


def produce_single_hist(data_source, hist, out):
    """
    Pull Data from the data source (ds), clear the data source, push the data
    into the hist, and generate the hist.
    """
    logging.debug('produce_single_hist '+str(len(data_source)))
    hist.push(data_source)
    data_source.clear()
    out.hs, out.bins = hist.hist()

def produce_ts_hist(ds_inc, ds_inc_t, ds_out, ds_out_t, hist, out):
    """
    Pull Data from the data source (ds), clear the data source, push the data
    into the hist, and generate the hist.
    """
    logger.debug('produce_ts_hist {} {} {} {} {}'.format(time.ctime(),
                len(ds_inc), len(ds_inc_t), len(ds_out), len(ds_out_t)))
    data = pd.Series(ds_inc,index=ds_inc_t)
    weights = pd.Series(ds_out,index=ds_out_t)
    zipped = basic_event_builder(data=data,weights=weights)
    hist.push(zipped['data'],zipped['weights'])
    ds_inc.clear()
    ds_inc_t.clear()
    ds_out.clear()
    ds_out_t.clear()
    _, _, out.hs, out.bins = hist.hist()
    out.hs = out.hs * 1.0/sum(out.hs)

class Carrier:
    def __init__(self):
        self.hs = None
        self.bins = None
    
def append_to_data_block(*args,**kwargs):
    kwargs['inc_data_block'].append(kwargs['value'])

def append_to_data_block_t(*args,**kwargs):
    kwargs['inc_value'].append(kwargs['value'])
    kwargs['inc_time'].append(kwargs['timestamp'])

# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
def launch_server(maxlen=1000, bins=np.arange(9450,9550,1)):

    stats = beam_stats.BeamStats()

    ###############################################################
    # Apply one of these sections for each graph being being made #
    ###############################################################
    
    # Acquire EPICS data and generate plot for Accelerator reported energy
    # Store inbound data in this deque
    accel_ev_data_block = deque(maxlen=maxlen)
    # Attach this method to the PV to aggregate data in the deque
    stats.accel_ev.subscribe(
        partial(append_to_data_block, inc_data_block=accel_ev_data_block)
    )
    # Define the histogram to be plotted
    accel_ev_hist = RapidHist(
        maxlen=maxlen,
        bins = bins,
    )
    # Create object for sending histogram data to draw method
    accel_ev_carry = Carrier()
    # Schedule the data-acquiring and regeneration of the histogram
    accel_ev_call = PeriodicCallback(
        partial(
            produce_single_hist, 
            data_source=accel_ev_data_block, 
            hist=accel_ev_hist,
            out=accel_ev_carry
        ),
        500
    )

    # Acquire EPICS data and generate plot for Transmission plots
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
        maxlen=maxlen,
        bins = bins,
    )
    # Create object for sending histogram data to draw method
    t_carry = Carrier()
    # Schedule the data-acquiring and regeneration of the histogram
    t_call = PeriodicCallback(
        partial(
            produce_ts_hist,
            ds_inc=t_accel_db,
            ds_inc_t=t_accel_db_time,
            ds_out=t_gmd_db, 
            ds_out_t=t_gmd_db_time,
            hist=t_hist,
            out=t_carry),
        500
    )
    
    server = Server(
        {
            '/incident': partial(
                single_plot_mgr,
                plot_data=accel_ev_carry
            ),
            '/transmission': partial(
                single_plot_mgr,
                plot_data=t_carry,
                y_range=(-.2,.2)
            ),
            '/both': partial(
                double_plot_mgr,
                inc_plot_data=accel_ev_carry,
                ts_plot_data=t_carry,
            ),
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

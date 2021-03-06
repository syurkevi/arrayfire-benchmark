
# bokeh includes/configuration
import logging
logging.basicConfig(level=logging.DEBUG)
from bokeh.plotting import figure, curdoc
from bokeh.models import Plot, ColumnDataSource, HoverTool
from bokeh.properties import Instance
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.models.widgets import HBox, Select, VBoxForm, CheckboxGroup, CheckboxButtonGroup
from bokeh.models.widgets import DataTable, TableColumn

# Celero recordtable parser
import glob
import os
from celero_parser import *

# plotting
import numpy as np

class BenchmarkApp(HBox):
    """An example of a browser-based, interactive plot with slider controls."""

    extra_generated_classes = [["BenchmarkApp", "BenchmarkApp", "HBox"]]

    inputs = Instance(VBoxForm)

    # widgets
    benchmarks = Instance(Select)
    x_axis_options = Instance(Select)
    y_axis_options = Instance(Select)
    # TODO: Convert this to a MultiSelect once it is fixed
    # https://github.com/bokeh/bokeh/issues/2495
    device_names = Instance(CheckboxGroup)
    platform_names = Instance(CheckboxButtonGroup)
    # data displays, not enabled by default
    data_display0 = Instance(DataTable)
    data_display1 = Instance(DataTable)

    # plot and interaction
    plot = Instance(Plot)
    hover = Instance(HoverTool)
    # data
    source0 = Instance(ColumnDataSource)
    source1 = Instance(ColumnDataSource)
    source2 = Instance(ColumnDataSource)
    source3 = Instance(ColumnDataSource)
    source4 = Instance(ColumnDataSource)
    source5 = Instance(ColumnDataSource)
    source6 = Instance(ColumnDataSource)
    source7 = Instance(ColumnDataSource)
    source8 = Instance(ColumnDataSource)
    source9 = Instance(ColumnDataSource)

    def make_source(self):
        # set up the data source
        self.source0 = ColumnDataSource(data=dict())
        self.source1 = ColumnDataSource(data=dict())
        self.source2 = ColumnDataSource(data=dict())
        self.source3 = ColumnDataSource(data=dict())
        self.source4 = ColumnDataSource(data=dict())
        self.source5 = ColumnDataSource(data=dict())
        self.source6 = ColumnDataSource(data=dict())
        self.source7 = ColumnDataSource(data=dict())
        self.source8 = ColumnDataSource(data=dict())
        self.source9 = ColumnDataSource(data=dict())

    def make_inputs(self):
        columns = [
            TableColumn(field='x', title='x'),
            TableColumn(field='y', title='y'),
            TableColumn(field='device', title='device'),
            TableColumn(field='platform', title='platform')
        ]

#        obj.data_display0 = DataTable(source=obj.source2, columns=columns)
#        obj.data_display1 = DataTable(source=obj.source3, columns=columns)

        # setup user input
        self.x_axis_options = Select(title="X:", value='size', options=axis_options)
        self.y_axis_options = Select(title="Y:", value='throughput [1/sec]', options=axis_options)
        self.benchmarks = Select(title="Benchmark:", value=benchmark_names[0],
            options=benchmark_names)
        self.device_names = CheckboxGroup(labels=device_names, active=[0])
        self.platform_names = CheckboxButtonGroup(labels=platform_names, active=[0])

    @classmethod
    def create(cls):
        """One-time creation of app's objects.

        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        obj = cls()

        obj.make_source()
        obj.make_inputs()
        obj.make_plot()
        obj.update_data()
        obj.set_children()

        return obj

    def plot_data(self, source, linecolor, symbolfill):
        self.plot.line(   'x', 'y', source=source, line_color=linecolor,
            line_width=3, line_alpha=0.6)
        self.plot.scatter('x', 'y', source=source, fill_color=symbolfill, size=8)

    def make_plot(self):

        # configure the toolset
        toolset = ['wheel_zoom,save,box_zoom,resize,reset']
        self.hover = BenchmarkApp.make_hovertool()
        toolset.append(self.hover)

        title = self.benchmarks.value + " " + \
            "(" + self.y_axis_options.value + " vs." + self.x_axis_options.value + ")"

        self.plot = figure(title_text_font_size="12pt",
            plot_height=400,
            plot_width=400,
            tools=toolset,
            title=title,
        )
        # remove the logo
        self.plot.logo = None

        # Generate a figure container
        # Plot the line by the x,y values in the source property
        self.plot_data(self.source0, "#F0A3FF", "white")
        self.plot_data(self.source1, "#0075DC", "white")
        self.plot_data(self.source2, "#993F00", "white")
        self.plot_data(self.source3, "#4C005C", "white")
        self.plot_data(self.source4, "#191919", "white")
        self.plot_data(self.source5, "#005C31", "white")
        self.plot_data(self.source6, "#2BCE48", "white")
        self.plot_data(self.source7, "#FFCC99", "white")
        self.plot_data(self.source8, "#808080", "white")
        self.plot_data(self.source9, "#94FFB5", "white")

        # set the x/y axis labels
#        plot.xaxis.axis_label = self.x_axis_options.value
#        plot.yaxis.axis_label = self.y_axis_options.value



    def set_children(self):
        self.inputs = VBoxForm(
            children=[self.benchmarks, self.device_names, self.platform_names,
                self.x_axis_options, self.y_axis_options,
#                self.data_display0, self.data_display1
            ]
        )

        self.children.append(self.inputs)
        self.children.append(self.plot)


    @classmethod
    def make_hovertool(self):
        hover = HoverTool(
            tooltips = [
                ("Device", "@device"),
                ("Backend", "@platform"),
                ("(x,y)", "(@x,@y)")
            ]
        )
        return hover

    def setup_events(self):
        """Attaches the on_change event to the value property of the widget.

        The callback is set to the input_change method of this app.
        """
        super(BenchmarkApp, self).setup_events()
        if not self.benchmarks:
            return

        # Event registration for everything except checkboxes
        self.benchmarks.on_change('value', self, 'benchmark_changed')
        self.x_axis_options.on_change('value', self, 'input_change')
        self.y_axis_options.on_change('value', self, 'input_change')

        # Event registration for checkboxes
        self.device_names.on_click(self.checkbox_handler)
        self.platform_names.on_click(self.checkbox_handler)

    def checkbox_handler(self, active):

        self.update_data()

    def benchmark_changed(self, obj, attrname, old, new):

        self.update_data()
        self.make_plot()
        curdoc().add(self)

    def input_change(self, obj, attrname, old, new):
        """Executes whenever the input form changes.

        It is responsible for updating the plot, or anything else you want.

        Args:
            obj : the object that changed
            attrname : the attr that changed
            old : old value of attr
            new : new value of attr
        """
        self.update_data()
        self.make_plot()
        curdoc().add(self)


    def getXY(self, celero_result, axis_filter):
        """Returns the X or Y value as specified by axis_filter"""

        # TODO: Remove the baseline measurement from the timing results
        if axis_filter == 'size':
            return celero_result['data_sizes']
        if axis_filter == 'log10(size)':
            return np.log10(celero_result['data_sizes'])
        if axis_filter == 'log2(size)':
            return np.log2(celero_result['data_sizes'])
        elif axis_filter == 'time [ms]':
            return celero_result['times'] * 1E-3
        elif axis_filter == 'throughput [1/sec]':
            return 1.0 / (celero_result['times'] * 1E-6)

    @classmethod
    def make_field_ids(self, id_number):
        """Creates a unique set of named fields for the y, device, and platform"""
        i = str(id_number)
        y_id = 'y' + i
        device_id = 'device' + i
        platform_id = 'platform' + i

        return [y_id, device_id, platform_id]


    def update_data(self):
        """Called each time that any watched property changes.

        This updates the sin wave data with the most recent values of the
        sliders. This is stored as two numpy arrays in a dict into the app's
        data source property.
        """

        # extract the user's input
        benchmark = self.benchmarks.value
        devices = list(device_names[i] for i in self.device_names.active)
        platforms = list(platform_names[i] for i in self.platform_names.active)
        x_axis_label = self.x_axis_options.value
        y_axis_label = self.y_axis_options.value


        # extract only the results which match this group
        filtered_results = filter(lambda x: x['benchmark_name'] == benchmark, celero_results)
        # remove the baseline measurements from the plots
        filtered_results = filter(lambda x: x['benchmark_name'] != "Baseline", filtered_results)

        # select the desired devices
        filtered_results = filter(lambda x: x['extra_data']['AF_DEVICE'] in devices, filtered_results)
        filtered_results = filter(lambda x: x['extra_data']['AF_PLATFORM'] in platforms, filtered_results)

        # extract the data
        sources = dict()
        result_number = 0
        for result in filtered_results:
            # ensure we don't plot too many results
            if result_number > MAX_PLOTS:
                break

            y_id, device_id, platform_id = self.make_field_ids(result_number)

            # Extract the results from the benchmark
            platform = result['extra_data']['AF_PLATFORM']
            device = result['extra_data']['AF_DEVICE']

            x = self.getXY(result, x_axis_label)
            y = self.getXY(result, y_axis_label)

            # store the benchmark results in the self.source object
            # NOTE: we replicate the device and platform data here so that
            # it works correctly with the mouseover/hover
            sources['x'] = x
            sources[y_id] = y
            sources[device_id] = [device] * len(x)
            sources[platform_id] = [platform] * len(x)

            # increment the counter
            result_number += 1

        # assign the data
        self.assign_source(sources, self.source0, 0)
        self.assign_source(sources, self.source1, 1)
        self.assign_source(sources, self.source2, 2)
        self.assign_source(sources, self.source3, 3)
        self.assign_source(sources, self.source4, 4)
        self.assign_source(sources, self.source5, 5)
        self.assign_source(sources, self.source6, 6)
        self.assign_source(sources, self.source7, 7)
        self.assign_source(sources, self.source8, 8)
        self.assign_source(sources, self.source9, 9)

    def assign_source(self, src, dest, index):
        """Assigns the data from src to the dictionary in dest if the
        corresponding data exists in src."""
        y_id, device_id, platform_id = self.make_field_ids(index)

        dest.data = dict()
        if y_id in src:
            dest.data['x'] = src['x']
            dest.data['y'] = src[y_id]
            dest.data['device'] = src[device_id]
            dest.data['platform'] = src[platform_id]
            dest._dirty = True

def import_directory(directory):
    """
    Creates a list of all .csv files in a directory, imports them using
    read_celero_recordTable, and returns the result.
    """

    csv_files = glob.glob(directory + "/*.csv")

    results = list()

    for filename in csv_files:
        results.extend(read_celero_recordTable(filename))

    return results

# maximum number of plots, currently limited by source[0,1,2,3] variables
MAX_PLOTS = 4
# define x/y axis possibilities
# NOTE: If you change an option here, change it in getXY above too
axis_options = ['size', 'log10(size)', 'log2(size)', 'time [ms]', 'throughput [1/sec]']

# Parse the data directory
data_dir = "/home/bkloppenborg/workspace/arrayfire_benchmark/results"
celero_results = import_directory(data_dir)

# Get a list of all of the benchmarks
benchmark_names = list_recordTable_benchmarks(celero_results)
benchmark_names = filter(lambda x: x != "Baseline", benchmark_names)

platform_names = list_recordTable_attribute(celero_results, 'AF_PLATFORM')
device_names = list_recordTable_attribute(celero_results, 'AF_DEVICE')

#ma
@bokeh_app.route("/bokeh/benchmarks/")
@object_page("benchmark")
def make_benchmarks():
    app = BenchmarkApp.create()
    return app

import json
import pdb
import math
import sys
import time
import warnings
from functools import lru_cache
from pathlib import Path
import pudb

from PySide6 import QtWidgets
import pandas as pd
import numpy as np
import PySide6
import pyqtgraph as pg
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QFileDialog

from price_action import OHLCPriceAction, BinancePriceAction
import DrawingState
from qraph_tools import timedelta_from_freq, secs_in_freq, reformat_pa_data, CandlesticksItem, \
	QQFieldItem, QQTargetItem, Trendline, LineSystem, QQRRItem, QQGraphicsLineItem, QQDrawing
# from qraphui import Ui_MainWindow
from qraphui2 import Ui_MainWindow
import importlib
qraph_tools = importlib.import_module("qraph_tools")
import pudb

class Qraph(QtWidgets.QMainWindow):
	def __init__(self, parent=None, sharex=True, live_updates=False):
		self.last_save_url = None #for saving charts
		self.assure_life()
		super(Qraph, self).__init__(parent=parent)
		self.set_style()
		self.freqs = ['1min', '5min', '15min', '1h', '4h', '1d', '1w', '1m', '1y']
		self.sharex = sharex
		self.live_updates = live_updates

		self.load_user_interface()

		self.vertical_plot_container = pg.GraphicsLayoutWidget()
		self.ui.chart_placeholder.addWidget(self.vertical_plot_container)

		self.active_drawing = None
		self.drawing_state = DrawingState.IDLE
		self.plot_areas = [] # instances of horizontally spanning plots
		self.plot_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum) #TODO: think this is wrong

		plot_area = self.create_plot_area()
		self.setup_buttons()
		self.setup_metadata()
		self.reset_available_freqs()

	def keyPressEvent(self, event):
		if event.key() == 16777223:
			key = 'delete'
		elif event.key() == 83:
			key = 's'
		elif event.key() == 84:
			key = 't'
		elif event.key() == 82:
			key = 'r'
		elif event.key() == 16777216:
			key = 'escape'
		else:
			key = None

		if key == 'delete':
			if self.active_drawing:
				for plot_area in self.plot_areas:
					if self.active_drawing in plot_area.items:
						plot_area.removeItem(self.active_drawing)
				self.unset_active_drawing()
		elif key == 's':
			self.ui.channel_system.setChecked(True)
		elif key == 't':
			self.ui.trend_line.setChecked(True)
		elif key == 'escape':
			self.unset_active_drawing()
			for button in self.ta_buttons:
				button.setChecked(False)
			self.drawing_state = DrawingState.IDLE
		elif key == 'r':
			self.ui.rr_tool.setChecked(True)

	def set_active_drawing(self, drawing):
		if self.active_drawing:
			self.active_drawing.stop_appearing_active()
		self.active_drawing = drawing

		if not isinstance(drawing, QQRRItem):
			self.ui.color_button.setColor(self.active_drawing.pen.color())
			self.ui.thickness_spinner.setValue(self.active_drawing.pen.width())
		self.ui.drawing_freq.setText(self.active_drawing.freq)
		self.ui.drawing_metadata.setText(self.active_drawing.metadata)
		# NOTE: THE ORDER OF OPERATIONS IN THIS FUNCTION IS IMPORTANT
		self.active_drawing.appear_active()

	def unset_active_drawing(self):
		if self.active_drawing:
			self.active_drawing.stop_appearing_active()
			self.active_drawing = None

	def set_style(self):
		pg.setConfigOption('background', 'w')
		pg.setConfigOption('foreground', 'k')

	def assure_life(self):
		#not sure why this is necessary, but it is, otherwise it completely dies. also see: show(), which uses the app
		if not QtWidgets.QApplication.instance():
			self.app = QtWidgets.QApplication(sys.argv)
		else:
			self.app = QtWidgets.QApplication.instance()
			self.app.exit()
			self.app.shutdown()
			del(self.app) #might seem overkill, but depending on qt implementation (pyside vs pyqt5 or sth), this is most robust

			self.app = QtWidgets.QApplication(sys.argv)

	def show(self, zoom_data=None):
		#overrides the superfunction, so it has the sys exit thing, and execs the app; also kind of unclear.
		if zoom_data:
			self.zoom(zoom_data)
		super().show()
		sys.exit(self.app.exec())
		#TODO: dont give the error when it closes.

	def add_scatter(self, data, plot_area_index=None, color1=(0, 0, 100), color2=(0, 0, 200), symbol='t1'):
		plot_area = self.derive_plot_area(plot_area_index)
		xs, ys = self.format_data_for_line(data)

		connections = np.zeros(len(xs)).astype(int)
		warnings.simplefilter(action='ignore', category=FutureWarning) #TODO: good idea or not? doing single line doesnt work
		p = plot_area.plot(xs, ys, symbolPen=color1, symbolBrush=color2, symbol=symbol, connect=connections)

		p.setZValue(100)

	def zoom(self, data):
		raise NotImplementedError()
#		TODO: rewrite
		"""
		# intelligently zooms to a particular set of data.
		# most of the code attempts to infer wtf data is to decide how to zoom to it.
		:param data: tuple of times or list of objects to zoom to
		:return: nada
		"""
		plot_area = self.plot_areas[0]
		viewbox = plot_area.getViewBox()
		if isinstance(data, tuple):
			if isinstance(data[0], np.datetime64) or isinstance(data[0], str):
				x_range = [np.datetime64(data[0])/np.timedelta64(1, 's'), np.datetime64(data[1])/np.timedelta64(1, 's')]
				viewbox.setRange(xRange=x_range)
			elif isinstance(data[0], list):
				viewbox.setRange(xRange=data[0], yRange=data[1])
			else:
				raise ValueError(data)
		elif isinstance(data, list):
			# 1) plot the list
			# 2) zoom to resulting plot object
			# 3) delete the plot object
			plots = self.add_plots(data, plot_area)
			viewbox.autoRange(items=plots)
			for plot in plots:
				plot_area.removeItem(plot)
			#disableAutoRange(axis=None) might b needed afterwards if I delete the things
		else:
			plots = self.add_plot(data, plot_area)
			# TODO: clean this up, this is a super dirty way to go about this.
			if plots[0] is None:
				# trying to zoom to something that's already present (add plot wont return anything).
				plots = [data]
				viewbox.autoRange(items=plots)
			else:
				viewbox.autoRange(items=plots)
				for plot in plots:
					plot_area.removeItem(plot)
		# trigger resampling, since this zooming does not trigger viewbox events
		interval = viewbox.viewRange()[0] # the x interval
		# for plot in plot_area.items:
		#	  if hasattr(plot, 'resample_to_interval'):
		#		  plot.resample_to_interval(interval)
		self.react_to_brand_new_viewbox_interval(interval, plot_area)

	def format_data_for_line(self, data):
		# TODO: remove. including too much comfort functionality dilutes
		# attention.
		if isinstance(data, dict):
			# must be a date: time
			# or x: y
			xs = list(data.keys())
			ys = list(data.values())
			total_data = pd.DataFrame({'y': ys}, index=xs)
			total_data.index.name = 'x'
			total_data = total_data.to_records()
			xs, ys = total_data.x, total_data.y
		elif isinstance(data, pd.DataFrame):
			if data.x:
				return data.x.values, data.y.values
			elif data.time:
				return data.time.values, data.y.values
			elif data.Time:
				return data.Time.values, data.y.values
			else:
				raise ValueError('DataFrame or Series plotted poorly')
		elif isinstance(data, pd.Series):
			xs, ys = data.index.values, data.values
		elif isinstance(data, np.recarray):
			if data.x:
				xs, ys = data.x, data.y
			elif data.time:
				xs, ys = data.time, data.y
			elif data.Time:
				xs, ys = data.time, data.y
			else:
				xs, ys = data[:,0], data[:,1]
		elif isinstance(data, np.ndarray):
			#TODO: if 1d, if 2d
			xs, ys = data[:,0], data[:,1]
		else:
			raise ValueError(f"unexpected data type for line: {type(data)}")

		if isinstance(xs[0], np.datetime64):
			xs = xs.astype('datetime64[ns]').astype('int') / 1e9
		return xs, ys

	def add_line(self, data, plot_area_index=None, color='b', width=2):
		plot_area = self.derive_plot_area(plot_area_index)
		xs, ys = self.format_data_for_line(data)
		return [plot_area.plot(x = xs, y = ys, pen=pg.mkPen(color = color, width = width))]

	def add_text_item(self, text, anchor, plot_area_index=None):
		plot_area = self.derive_plot_area(plot_area_index)
		print("WARNING: TEXT ITEMS DONT TRANSFORM TO LOG SCALE PROPERLY")
		t = pg.TextItem(text, color='b', anchor=(0, 0))
		t.setPos(anchor[0], anchor[1])
		plot_area.addItem(t)

	def add_hline(self, pos, plot_area_index=None, label=None):
		raise NotImplementedError()
		plot_area = self.derive_plot_area(plot_area_index)
		hline = pg.InfiniteLine(pos=pos, movable=True, label=label, angle=0)
		plot_area.addItem(hline)

	def add_vline(self, pos, plot_area_index=None, label=None):
		raise NotImplementedError()
		plot_area = self.derive_plot_area(plot_area_index)
		vline = pg.InfiniteLine(pos=pos, movable=True, label=label, angle=90)
		plot_area.addItem(vline)

	def setup_metadata(self):
		self.ui.connection_state.setText("")
		self.ui.label_4.setText("")

	def setup_buttons(self):
		# Resampling
		self.ui.resample_1min.clicked.connect(lambda: self.resample_button_click('1min'))
		self.ui.resample_5min.clicked.connect(lambda: self.resample_button_click('5min'))
		self.ui.resample_15min.clicked.connect(lambda: self.resample_button_click('15min'))
		self.ui.resample_1h.clicked.connect(lambda: self.resample_button_click('1h'))
		self.ui.resample_4h.clicked.connect(lambda: self.resample_button_click('4h'))
		self.ui.resample_1d.clicked.connect(lambda: self.resample_button_click('1d'))
		self.ui.resample_1w.clicked.connect(lambda: self.resample_button_click('1w'))
		self.ui.resample_1m.clicked.connect(lambda: self.resample_button_click('1m'))
		self.ui.resample_1y.clicked.connect(lambda: self.resample_button_click('1y'))

		# TA tools
		self.ui.channel_system.clicked.connect(self.handle_line_system_button_click)
		self.ui.group.setDisabled(True)
		self.ui.box.setDisabled(True)
		self.ta_buttons = [self.ui.channel_system,
						   self.ui.group,
						   self.ui.box,
						   self.ui.trend_line,
						   self.ui.horizontal_line,
						   self.ui.vertical_line,
						   self.ui.rr_tool]
		self.ui.horizontal_line.setDisabled(True)
		self.ui.vertical_line.setDisabled(True)

		# Trading (all disabled for now)
		self.ui.market_order.setDisabled(True)
		self.ui.limit_bracket_order.setDisabled(True)
		self.ui.stop_bracket_order.setDisabled(True)
		self.ui.feather_order.setDisabled(True)
		self.ui.exit_all_order.setDisabled(True)

		# Saving
		self.ui.save.triggered.connect(self.save)
		self.ui.save_as.triggered.connect(self.save_as)
		self.ui.load.triggered.connect(self.load)

		# TA Tool properties (TODO: also other drawing properties?)
		color_button = pg.ColorButton()
		self.ui.ta_object_properties.addWidget(color_button)
		self.ui.color_button = color_button
		color_button.sigColorChanged.connect(self.set_color)

		self.ui.thickness_spinner.valueChanged.connect(self.set_width)

		self.ui.drawing_freq.editingFinished.connect(self.set_drawing_freq)

		self.ui.drawing_metadata.editingFinished.connect(self.set_drawing_metadata)
		self.ui.checkBox_3.setDisabled(True) #'hide all'

		# Lower bar with buttons
		self.ui.left_button.setDisabled(True)
		self.ui.right_button.setDisabled(True)
# 		self.ui.left_button.clicked.connect(self.handle_left_button_click)
# 		self.ui.right_button.clicked.connect(self.handle_right_button_click)
		# TODO: fix zoom() so ^^ works
		self.ui.go_to_date.setDisabled(True)

	def handle_left_button_click(self):
		self.handle_side_button_click('left')
	def handle_right_button_click(self):
		self.handle_side_button_click('right')

	def handle_side_button_click(self, direction):
		assert direction in ['left', 'right']
		relevant_drawings = []
		selection_string = self.ui.drawing_metadata.text()
		for plot_area in self.plot_areas:
			for item in plot_area.items:
				if isinstance(item, QQDrawing):
					if selection_string in item.metadata:
						relevant_drawings.append(item)
		viewbox = self.plot_areas[0].getViewBox()
		current_x_range = viewbox.viewRange()[0]  # [[xmin, xmax], [ymin, ymax]]
		current_x_pos = (current_x_range[0] + current_x_range[1])/2

		min_distance = np.inf
		closest_drawing_index = 0
		for index, drawing in enumerate(relevant_drawings):
			pos = drawing.best_x_position
			if abs(pos - current_x_pos) < min_distance:
				min_distance = abs(pos - current_x_pos)
				closest_drawing_index = index

		if direction == 'right':
			if closest_drawing_index == len(relevant_drawings) - 1:
				self.zoom(relevant_drawings[0])
			else:
				self.zoom(relevant_drawings[closest_drawing_index + 1])
		else:
			# if closest_drawing_index == 0:
			#	  closest_drawing_index = len(relevant_drawings) - 1
			self.zoom(relevant_drawings[closest_drawing_index - 1])

	def set_drawing_freq(self):
		if self.active_drawing:
			self.active_drawing.freq = self.ui.drawing_freq.text()

	def set_drawing_metadata(self):
		if self.active_drawing:
			self.active_drawing.metadata = self.ui.drawing_metadata.text()

	def test_color(self, color_button):
		if not self.active_drawing:
			return
		color = color_button.color()
		self.active_drawing.test_color(color)

	def set_color(self, color_button):
		if not self.active_drawing:
			return
		color = color_button.color()
		self.active_drawing.set_color(color)

	def set_width(self, width):
		if not self.active_drawing:
			return
		self.active_drawing.set_width(width)

	def save(self):
		if self.last_save_url:
			saveable_info = json.dumps(self.save_object())
			Path(self.last_save_url).write_text(saveable_info)
		else:
			self.save_as()

	@property
	def default_chart_name(self):
		name = ''
		assert len(self.plot_areas) == 1, "genning default name doesnt work with multiple charts"
		for area in self.plot_areas:
			for item in area.items:
				if isinstance(item, CandlesticksItem):
					name += item.initial_pa.label.replace('1min', '').replace('1m', '')
					name += item.initial_pa.resolution
		name += str(math.floor(time.time()/60)) #minutes since epoch, bc there's no way I need seconds and thats just too long
		return name

	def save_as(self):
		url = QFileDialog.getSaveFileUrl(self, "Choose name/loc to save", self.default_chart_name, "Json Files (*.json)")
		url = url[0].path()
		if not 'json' in url:
			url = url + '.json'
		self.last_save_url = url
		saveable_info = json.dumps(self.save_object())
		Path(url).write_text(saveable_info)

	def load(self):
		url = QFileDialog.getOpenFileUrl(self, "Choose chart to load", "chart", "Json Files (*.json)")
		url = url[0].path()
		self.load_url(url)

	def load_url(self, url):
		save_object_text = Path(url).read_text()
		save_object = json.loads(save_object_text)
		self.delete_all_current_charts() # TODO: prompt if you really wanna lose all that juicy stuff
		charts = self.charts_from_save_object(save_object)
		plot_area = self.create_plot_area()
		for chart in charts:
			plot_area.addItem(chart)
# 		self.add_plots(charts, plot_area)
		self.last_save_url = url
		self.reset_available_freqs()
		if 'viewbox_range' in save_object.keys():
			self.zoom(tuple(save_object['viewbox_range']))

	def delete_all_current_charts(self):
		# just deletes everything
		for plot_area in self.plot_areas:
			for chart in plot_area.items:
				if hasattr(chart, 'pre_exit_sequence'):
					# closes candlestick updating threads
					chart.pre_exit_sequence()
			plot_area.scene().sigMouseClicked.disconnect() #lambda event: self.react_to_mouse_click(event, plot_area))
			self.vertical_plot_container.removeItem(plot_area)
			plot_area.parent = None
			del plot_area
		self.plot_areas = []
		self.drawing_state = DrawingState.IDLE # avoids bad intermediate states
		#	  #TODO: remove all rows from the layout

	def handle_line_system_button_click(self, pressed_in):
		if not pressed_in:
			self.drawing_state = DrawingState.IDLE
			self.get_drawing("active_line_system").name = None

	def resample_button_click(self, freq):
		#TODO: cancel resampling to bad resolutions
		print(f'manually resampling to {freq}')
		self.ui.auto_resample.setChecked(False)
		self.resample_plots(freq)
		self.hide_irrelevant_drawings(freq)

	def hide_irrelevant_drawings(self, freq):
		for area in self.plot_areas:
			for drawing in area.items:
				if hasattr(drawing, 'hide_wrong_tfs'):
					drawing.hide_wrong_tfs(freq)

	def react_to_viewbox_change(self, viewbox, interval, plot_area):
		auto_resample = self.ui.auto_resample.isChecked()
		self.last_interval = interval # Used for manual resampling purposes (for cutting) TODO: probably can remove and just use the current viewbox?
		# CUT THE SIDES FOR PERFORMANCE REASONS:
		for plot in plot_area.items:
			if hasattr(plot, 'maybe_cut_to_interval'):
				plot.maybe_cut_to_interval(interval)
		# RESAMPLE:
		if auto_resample:
			for plot in plot_area.items:
				if hasattr(plot, 'resample_to_interval'):
					plot.resample_to_interval(interval)
				if hasattr(plot, 'hide_wrong_tfs'):
					plot.hide_wrong_tfs(self.current_freq())
			self.update_current_freq()

	def react_to_brand_new_viewbox_interval(self, interval, plot_area):
		print('reacting to new viewbox interval')
		"""
		Use only when a sudden interval change occurs (contrast with react_to_viewbox_change, which occurs during
		continuous changes). Yes, it really is necessary.
		"""
		# CUT THE SIDES FOR PERFORMANCE REASONS:
		for plot in plot_area.items:
			if hasattr(plot, 'maybe_cut_to_interval'):
				plot.maybe_cut_to_interval(interval)
		# RESAMPLE:
		for plot in plot_area.items:
			if hasattr(plot, 'resample_to_interval_abrupt'):
				plot.resample_to_interval_abrupt(interval)
				plot.generatePicture()
				plot.update() #todo: not sure putting this and generatePicture here makes much sense.
			if hasattr(plot, 'hide_wrong_tfs'):
				plot.hide_wrong_tfs(self.current_freq())
		self.update_current_freq()

	def update_current_freq(self):
		# TODO: a major performance enchancement would be having items call this from themselves.
		# TODO: this is dirty
		for plot_area in self.plot_areas:
			for item in plot_area.items:
				if isinstance(item, CandlesticksItem):
					freq = item.freq
					if freq in self.freqs:
						getattr(self.ui, 'resample_'+freq).setChecked(True)
						self.ui.custom_resample.setText(freq)
						return

	def resample_plots(self, freq):
		for plot_area in self.plot_areas:
			self.resample_plot(freq, plot_area)

	def resample_plot(self, freq, plot_area):
		# loop through all plotted things inside the plot_area.
		# if has a price_action, resample that shit.
		# if has a line chart, resample that too I guess (not to be implemented yet)
		for item in plot_area.items:
			if isinstance(item, CandlesticksItem):
				item.resample(freq, self.last_interval)

	def load_user_interface(self):
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

	def create_plot_area(self):
		plot = self.vertical_plot_container.addPlot()
		plot.setSizePolicy(self.plot_size_policy)
		plot.setAxisItems({'bottom': pg.DateAxisItem()}) # makes unix secs look like proper times
		plot.setLogMode(False, True)
		plot.scene().sigMouseClicked.connect(lambda event: self.react_to_mouse_click(event, plot))
		plot.sigXRangeChanged.connect(lambda viewbox, interval: self.react_to_viewbox_change(viewbox, interval, plot))

		self.plot_areas.append(plot)

		return plot #backwards compat for now
	
	def derive_plot_area(self, plot_area_index=None):
		if plot_area_index == None:
			return self.plot_areas[0]
		else:
			return self.plot_areas[plot_area_index]

	def add_candlestick_chart(self, pa, plot_area_index=None):
		plot_area = self.derive_plot_area(plot_area_index)
		if isinstance(pa, CandlesticksItem):
			majority_chart = pa
		else:
			assert isinstance(pa, BinancePriceAction)
			copied_pa = pa.copy()#BinancePriceAction(pa.data_source, pa.resolution, pa.label) # necessary for live and non-live to work simultaneously #.iloc[-2:])
			copied_pa.label = pa.label
			copied_pa.resolution = pa.resolution
			majority_chart = CandlesticksItem(copied_pa, regularly_update=False)

		plot_area.addItem(majority_chart, clipToView=True)# ???
		majority_chart.setZValue(90)

		self.ui.instrument.setItemText(0, pa.label) #TODO: switchable
		self.reset_available_freqs()

		if self.live_updates:
			pa = majority_chart.initial_pa
			copied_pa = pa.copy()
			copied_pa.data = copied_pa.data[-2:] 
			updating_part = CandlesticksItem(copied_pa, regularly_update=True)
			plot_area.addItem(updating_part, clipToView=True)# ???
			updating_part.setZValue(90)
			return [majority_chart, updating_part]
		else:
			return [majority_chart]



	def react_to_mouse_click(self, event, plot_area):
		event_scene_position = event.scenePos()
		real_pos = plot_area.getViewBox().mapSceneToView(event_scene_position)

		if self.ui.vertical_line.isChecked():
			self.add_vline(real_pos, plot_area)
			self.ui.vertical_line.setChecked(False)

		if self.ui.horizontal_line.isChecked():
			self.add_hline(real_pos, plot_area)
			self.ui.horizontal_line.setChecked(False)
			print('not fully implemented ta tool - log scale breaks')

		if self.ui.trend_line.isChecked():
			self.handle_drawing_trend_line(real_pos, plot_area)

		if self.ui.channel_system.isChecked():
			self.handle_drawing_line_system(real_pos, plot_area)

		if self.ui.box.isChecked():
			self.handle_drawing_box(real_pos, plot_area)
			print('not fully implemented ta tool')

		if self.ui.rr_tool.isChecked():
			self.handle_adding_rr_tool(real_pos, plot_area)

		if self.ui.group.isChecked():
			print('not implemented ta tool')
			pass

		self.update_active_drawing(event.scenePos(), plot_area)

	def update_active_drawing(self, position, plot_area):
		# position should be scenePos AFAIK
		activated_drawings = [i.qqparent for i in plot_area.scene().items(position) if hasattr(i, 'qqparent')
							  and isinstance(i.qqparent, QQDrawing) and isinstance(i, QQTargetItem)]
		if len(activated_drawings) == 0:
			self.unset_active_drawing()
		elif len(activated_drawings) > 0:
			self.set_active_drawing(activated_drawings[0])

	def save_object(self):
		# TODO: also save the zoom
		# TODO: don't save half-drawn points
		obj = {}
		assert len(self.plot_areas) == 1, "saving more than 1 plot will (almost certainly) break"
		for plot_area in self.plot_areas:
			for plot_item in plot_area.items:
				if isinstance(plot_item, CandlesticksItem):
					if plot_item.regularly_update:
						continue # dont save the updating part of a chart
				if hasattr(plot_item, 'save_object'):
					if plot_item.__class__.__name__ not in obj:
						obj[plot_item.__class__.__name__] = []
					obj[plot_item.__class__.__name__].append(plot_item.save_object())
				else:
					print(f'trying to save an unsaveble chart element {plot_item}, skipping, but expect weird behavior')
		viewbox = self.plot_areas[0].getViewBox()
		obj['viewbox_range'] = viewbox.viewRange() # [[xmin, xmax], [ymin, ymax]]
		return obj

	@staticmethod
	def gen_from_save_object(save_object):
		print('THIS FUNCTION IS BROKEN')
		charts = Qraph.charts_from_save_object(save_object)
		graph = Qraph(charts)
		return graph

	@staticmethod
	def charts_from_save_object(save_object):
		charts = []
		for object_class_name, save_objects in save_object.items():
			if object_class_name == 'viewbox_range':
				continue #not an object class, the only metadata that is currently carried.
			object_class = getattr(qraph_tools, object_class_name)
			for o in save_objects:
				charts.append(object_class.gen_from_save_object(o))
		return charts

	def handle_adding_rr_tool(self, last_click_position, plot_area):
		if self.drawing_state == DrawingState.IDLE:
			point = QQTargetItem(last_click_position, name="first_RR_drawing_point", freq=self.current_freq())
			plot_area.addItem(point)
			self.drawing_state = DrawingState.DRAWING_RR_1
		elif self.drawing_state == DrawingState.DRAWING_RR_1:
			point = QQTargetItem(last_click_position, name="second_RR_drawing_point", freq=self.current_freq())
			plot_area.addItem(point)
			self.drawing_state = DrawingState.DRAWING_RR_2
		elif self.drawing_state == DrawingState.DRAWING_RR_2:
			p1 = self.get_drawing("first_RR_drawing_point")
			p2 = self.get_drawing("second_RR_drawing_point")
			plot_area.removeItem(p1)
			plot_area.removeItem(p2)
			rr_tool = QQRRItem(p1.pos(), p2.pos(), last_click_position, freq=self.current_freq())
			plot_area.addItem(rr_tool)
			self.set_active_drawing(rr_tool)
			self.drawing_state = DrawingState.IDLE
			self.ui.rr_tool.setChecked(False)


	def handle_drawing_box(self, last_click_position, plot_area):
		print('drawing boxes is not really implemented properly atm')
		if self.drawing_state == DrawingState.IDLE:
			point = QQTargetItem(last_click_position, name="first_box_drawing_point")
			plot_area.addItem(point)
			self.drawing_state = DrawingState.DRAWING_BOX
		elif self.drawing_state == DrawingState.DRAWING_BOX:
			point = self.get_drawing("first_box_drawing_point")
			plot_area.removeItem(point)
			roi = pg.ROI(point.pos(), (abs(point.x - last_click_position.x()), abs(point.y - last_click_position.y())), removable=True, pen=pg.mkPen('g', width=2), handlePen=pg.mkPen('b', width=2))
			roi.addScaleHandle((0,0), (1,1))
			roi.addScaleHandle((1,1), (0,0))
			plot_area.addItem(roi)
			self.ui.box.setChecked(False)
			self.drawing_state = DrawingState.IDLE
		else:
			raise ValueError(self.drawing_state)

	def handle_drawing_line_system(self, last_click_position, plot_area):
		if self.active_drawing and isinstance(self.active_drawing, LineSystem):
			sys = self.active_drawing# = rr_tool
			sys.add_parallel(last_click_position)
			self.drawing_state = DrawingState.IDLE ##might seem weird but necessary
		elif self.drawing_state == DrawingState.IDLE:
			if self.has_drawing("first_trendline_drawing_point"):
				plot_area.removeItem(self.get_drawing("first_trendline_drawing_point"))
			point = QQTargetItem(last_click_position, name="first_trendline_drawing_point", freq=self.current_freq())
			plot_area.addItem(point)
			self.drawing_state = DrawingState.DRAWING_TRENDLINE
		elif self.drawing_state == DrawingState.DRAWING_TRENDLINE:
			point = self.get_drawing("first_trendline_drawing_point")
			plot_area.removeItem(point)

			constructed_trendline = Trendline(point.pos(), last_click_position, color=self.ui.color_button.color(),
											  width=self.ui.thickness_spinner.value(), freq=self.current_freq())

			sys = LineSystem(constructed_trendline, name="active_line_system", freq=self.current_freq())
			plot_area.addItem(sys)
			self.set_active_drawing(sys)

			self.drawing_state = DrawingState.IDLE
		else:
			raise ValueError(self.drawing_state)

	def get_drawing(self, name):
		search_space = sum([plot.items for plot in self.plot_areas], [])
		matches = [i for i in search_space if hasattr(i, 'name') and i.name == name]
		assert len(matches) == 1, f"no matches or too many matches: {len(matches)}"
		return matches[0]

	def has_drawing(self, name):
		search_space = sum([plot.items for plot in self.plot_areas], [])
		matches = [i for i in search_space if hasattr(i, 'name') and i.name == name]
		return len(matches)>0

	def handle_drawing_trend_line(self, last_click_position, plot_area):
		# TODO: drawing states might be useless - can be derived using the
		# points that currently exist (does it have the first trendline drawing
		# point?) and the press of the button. This would also solve a few
		# other issues.
		if self.drawing_state == DrawingState.IDLE:
			if self.has_drawing("first_trendline_drawing_point"):
				plot_area.removeItem(self.get_drawing("first_trendline_drawing_point"))
			point = QQTargetItem(last_click_position, name="first_trendline_drawing_point", freq=self.current_freq())
			plot_area.addItem(point)
			self.drawing_state = DrawingState.DRAWING_TRENDLINE

		elif self.drawing_state == DrawingState.DRAWING_TRENDLINE:
			point = self.get_drawing("first_trendline_drawing_point")
			plot_area.removeItem(point)

			constructed_trendline = Trendline(point.pos(), last_click_position, color=self.ui.color_button.color(),
											  width=self.ui.thickness_spinner.value(), freq=self.current_freq())
			plot_area.addItem(constructed_trendline)
			self.set_active_drawing(constructed_trendline)
			self.ui.trend_line.setChecked(False)
			self.drawing_state = DrawingState.IDLE
		else:
			raise ValueError(self.drawing_state)

	def reset_available_freqs(self):
		smallest_available_freq = None
		for plot_area in self.plot_areas:
			for item in plot_area.items:
				if hasattr(item, 'freqs'):
					if not smallest_available_freq:
						smallest_available_freq = item.freqs[0]
					else:
						if secs_in_freq(smallest_available_freq) > secs_in_freq(item.freqs[0]):
							smallest_available_freq = item.freqs
		if not smallest_available_freq:
			return
		self.change_freqs_from_smallest_available_freq(smallest_available_freq)
		for freq in self.freqs:
			self.ui.__dict__[f'resample_{freq}'].setEnabled(True)

	def current_freq(self):
		assert len(self.plot_areas) == 1, "only single plot area current freq supported rn"
		for area in self.plot_areas:
			for item in area.items:
				if isinstance(item, CandlesticksItem):
					return item.freq

	def change_freqs_from_smallest_available_freq(self, smallest_available_freq):
		if smallest_available_freq in self.freqs:
			self.freqs = self.freqs[self.freqs.index(smallest_available_freq):]
		else:
			for index, freq in enumerate(self.freqs):
				if secs_in_freq(smallest_available_freq) > secs_in_freq(freq):
					self.freqs = self.freqs[index:]

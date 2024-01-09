import math
import time
import warnings
from functools import lru_cache
import pdb
import pudb

import PySide6
import numpy as np
from PySide6 import QtWidgets
import pyqtgraph as pg
from PySide6.QtCore import QLineF
from PySide6.QtWidgets import QGraphicsLineItem
from pyqtgraph import QtCore, QtGui, TargetItem, Point, UIGraphicsItem, GraphicsObject
import pandas as pd
from price_action import OHLCPriceAction, BinancePriceAction
import importlib
price_action = importlib.import_module("price_action")
import _thread

# TODO: systematic log mode handling (perhaps newer pyqthgraph would help)

class QQDrawing:
	"""
	Custom drawing super-class, mostly for detection
	"""
	def __init__(self, metadata=None):
		self.metadata = metadata
		# TODO: add the freq thing here probably.

	def appear_active(self):
		raise NotImplementedError
	def stop_appearing_active(self):
		raise NotImplementedError

	def hide_wrong_tfs(self, freq):
		if freq == self.freq:
			if self.isVisible():
				return
			else:
				self.show() #TODO: check if this check
				return
		# TODO: potential performance optimization: store secs in current freq
		if secs_in_freq(freq) > secs_in_freq(self.freq):
			self.hide()
		else:
			self.show()

	@property
	def best_x_position(self):
		raise NotImplementedError

class CandlesticksItem(pg.GraphicsObject):
	def __init__(self, price_action, style='price_action', regularly_update=False):
		pg.GraphicsObject.__init__(self)
		self.ltf_increment_treshold = 50 #num candles
		self.htf_increment_treshold = 800 #num candles
		self.freqs = ['1min', '5min', '15min', '1h', '4h', '1d', '1w', '1m', '1y']
		self.regularly_update = regularly_update
		self.cached_resamples = {} 
		# ^^ because it's impossible to clear the cache for a single instance
		# of a class and I suspect lru_cache blocks parallel calculation of
		# cached values for distinct instances of the same class

		self.initial_pa = price_action
		self.freq = self.initial_pa.resolution
		self.uncut_data, self.uncut_log_data = self._memoized_resample(self.freq) #inefficient to do this here.
		self.absolute_start = self.initial_pa.data.index[0].value/ 10**9
		self.absolute_end = self.initial_pa.data.index[-1].value/ 10**9 # used for performance enchancement during cutting

		self.reset_available_freqs(self.initial_pa)

		self.log_mode = [False, False]
		# TODO: should the reduced window be set here? look for clues in PlotDataItem.

		if self.regularly_update:
			self.updater_thread = _thread.start_new_thread(self.regularly_update_chart, ())

		_thread.start_new_thread(self.reduce_future_lag, ())


		self.set_style(style)
		self.initial_resample() #< gen data here
		self.generatePicture()

	def regularly_update_chart(self):
		while self.regularly_update:
			print('regularly updating!')
			self.get_newest_candles()
			time.sleep(60)

	def get_newest_candles(self):
		self.initial_pa.update()

		self.cached_resamples = {} #clear the cache
		if self.regularly_update: # redues the probability of it throwing a C++ error in the case of a race condition
			_thread.start_new_thread(self.reduce_future_lag, ())
   		# HERE: there is no pa DATA sometimes after the first resample
   		# if len(self.pa.data) > 2:
   		#	  self.resample(self.pa.resolution, (self.pa.data.index[0].value/ 10**9, self.pa.data.index[-1].value/ 10**9))

	def reset_available_freqs(self, pa):
		#TODO: initial pa?
		if not (pa.resolution in self.freqs):
			self.add_freq_in_proper_place(pa.resolution)
		self.freqs = self.freqs[self.freqs.index(pa.resolution):]

	def add_freq_in_proper_place(self, custom_freq):
		print(f'adding {custom_freq}')
		for index, freq in enumerate(self.freqs):
			left_freq = secs_in_freq(freq)
			right_freq = secs_in_freq(self.freqs[index+1]) if index < (len(self.freqs)-1) else np.inf
			if left_freq < secs_in_freq(custom_freq) < right_freq:
				self.freqs.insert(index+1, custom_freq)
				return
		raise ValueError(custom_freq)

	def initial_resample(self):
		# so there's an adequate amount of candles when it first spawn
		start = self.initial_pa[0].time.astype(int)/ 10**9
		end = self.initial_pa[-1].time.astype(int)/ 10**9
		self.resample_to_interval_abrupt((start, end))

		self.data = self.uncut_data
		self.log_data = self.uncut_log_data

		self.current_start = self.data[0][0]
		self.current_end = self.log_data[-1][0]

	def resample_to_interval_abrupt(self, interval):
		"""
		(I think) needlessly complicated, TODO: simplify
		finds the right freq for the current interval.
		uses some assumptions that might fail.
		"""
		start = interval[0]
		end = interval[1]
		interval_size = int(end - start) #seconds
		candle_size = secs_in_freq(self.freq)

		if candle_size * self.htf_increment_treshold < interval_size:
			# over 800 current candles fit inside range, need to sample to HTF
			num_resamplings = 1
			while (candle_size * self.htf_increment_treshold) < interval_size/(5**num_resamplings):
				num_resamplings = num_resamplings + 1
			freqs = self.freqs
			if freqs.index(self.freq)+1+num_resamplings > len(freqs):
				raise Exception('Are we looking at over 800 years of data?')
			newfreq = freqs[freqs.index(self.freq) + num_resamplings]
			print(f'Abruptly incrementing to higher tf from {self.freq} to {newfreq}')
			# self.ui.__dict__[f'resample_{newfreq}'].setChecked(True)
			# self.pa = self._memoized_resample(newfreq)
			self._resample(newfreq)

		elif candle_size * self.ltf_increment_treshold > interval_size:
			# 50 current candles can't fit inside range, need to sample to LTF
			num_resamplings = 1
			while (candle_size * self.ltf_increment_treshold) > interval_size*(5**num_resamplings):
				num_resamplings = num_resamplings + 1
			freqs = self.freqs
			if freqs.index(self.freq)-num_resamplings < 0:
				num_resamplings = freqs.index(self.freq)
				# raise Exception('wtf are we looking at, resampling would give gay chart here')
			newfreq = freqs[freqs.index(self.freq) - num_resamplings]
			print(f'Abruptly incrementing to lower tf from {self.freq} to {newfreq}')
			# self.ui.__dict__[f'resample_{newfreq}'].setChecked(True)
			# self.pa = self._memoized_resample(newfreq)
			self._resample(newfreq)

	def reduce_future_lag(self):
		print(f'pa label: {self.initial_pa.label}')
		# resamples PA in every (reasonable) possible way in advance, thus
		# saving it to memory
		for freq in self.freqs:
			self._memoized_resample(freq)

	def _resample(self, freq):
		if freq == self.freq:
			return
		self.uncut_data, self.uncut_log_data = self._memoized_resample(freq)
		self.data, self.log_data = self.uncut_data, self.uncut_log_data
		# for performance enchancement for cutting:
		if len(self.uncut_data) != 0:
			current_start = self.uncut_data[0][0]
			current_end = self.uncut_data[-1][0]
			self.current_start = current_start - secs_in_freq(self.freq) # because resampling breaks the boundaries
			self.current_end = current_end + secs_in_freq(self.freq) # because resampling breaks the boundaries

		self.freq = freq

	def resample(self, freq, last_interval):
		# called only from outside
		self._resample(freq)
		self._cut_to_interval(last_interval)
		self.generatePicture()
		self.update()

	def resample_to_interval(self, interval):
		interval_size = int(interval[1] - interval[0]) # seconds
		candle_size = secs_in_freq(self.freq)
		# TODO: not LTF and HTF increment PA, but just find the proper freq and
		#  do that one (would make .show(zoomlevel) work better
		if not self.freq == self.freqs[0]: # if a lower resolution is not available, can't increment down.
			if candle_size * self.ltf_increment_treshold > interval_size:
				# 500 candles don't fit, resample so the candles are ltf
				self._ltf_increment_pa()
				self._cut_to_interval(interval)
				self.generatePicture()
				return

		if candle_size * self.htf_increment_treshold < interval_size:
			# over 800 candles fit, resample so candles are htf
			self._htf_increment_pa()
			self._cut_to_interval(interval)
			self.generatePicture()

	def _htf_increment_pa(self):
		current_freq = self.freq
		freqs = self.freqs
		if freqs.index(current_freq)+2 > len(freqs):
			return
		newfreq = freqs[freqs.index(current_freq) + 1]
		self._resample(newfreq)


	def _ltf_increment_pa(self):
		#TODO: include exotic freqs so it doesnt choke, same for HTF
		current_freq = self.freq
		freqs = self.freqs
		if freqs.index(current_freq) - 1 < 0:
			return
		newfreq = freqs[freqs.index(current_freq) - 1]
		self._resample(newfreq)

	def _cut(self, start, end):
		#TODO: everything can be faster by using a lighter pa object representation
		start = np.datetime64(int(start), 's').astype('<M8[m]')
		end = np.datetime64(int(end), 's').astype('<M8[m]')
		candle_size = secs_in_freq(self.freq)

		if not start < self.initial_pa[0].time:
			start = start - np.timedelta64(self.htf_increment_treshold * candle_size, 's')
		if not end > self.initial_pa[-1].time:
			end = end + np.timedelta64(self.htf_increment_treshold * candle_size, 's')

		if start < self.initial_pa[0].time: #vajadzīgs, jo indeksējot ar pd.Timestamp, nevar pāršaut indeksus.
			start = self.initial_pa[0].time.astype(int)/ 10**9
		if end > self.initial_pa[-1].time or (end.astype('datetime64[Y]').astype(int) + 1970 > 2030): #TODO: FIX THIS BLSHIT
			end = self.initial_pa[-1].time.astype(int)/ 10**9

		start = start.astype('datetime64[s]').astype('int')
		end = end.astype('datetime64[s]').astype('int')


		self.data = self.uncut_data[(start<self.uncut_data[:,0])&(self.uncut_data[:,0]<end)]
		self.log_data = self.uncut_log_data[(start<self.uncut_log_data[:,0])&(self.uncut_log_data[:,0]<end)]

		# for performance enchancement for cutting:
		if len(self.data) != 0:
			current_start = self.data[0][0]
			current_end = self.data[-1][0]
			self.current_start = current_start - secs_in_freq(self.freq) #because resampling breaks the boundaries
			self.current_end = current_end + secs_in_freq(self.freq) # because resampling breaks the boundaries

	def _cut_to_interval(self, interval):
		start, end = interval[0], interval[1]
		self._cut(start, end)

	def maybe_cut_to_interval(self, interval):
		# if: overflown view into more candles, recut
		start, end = interval[0], interval[1]
		# TODO: ADA 4h for some reason behaves erratically for this interval near the end
		if self.current_start > self.absolute_start or self.current_end < self.absolute_end:
			if start < self.absolute_start:
				start = self.absolute_start
			if end > self.absolute_end:
				end = self.absolute_end
			if start < self.current_start or end > self.current_end:
				self._cut_to_interval(interval)
				self.generatePicture()


	def _memoized_resample(self, freq):
		# return data and log data:
		if freq not in self.cached_resamples.keys():
			if freq == self.initial_pa.resolution:
				pa = self.initial_pa
			else:
				pa = self.initial_pa.resample(freq, cut_partial_candles=False)
			data = reformat_pa_data(pa) ## data must have fields: time, open, high, low, close
			log_data = self.generate_log_data(data)

			self.cached_resamples[freq] = (data, log_data)
		return self.cached_resamples[freq]


	def set_style(self, style):
		self.style = style
		if style == 'price_action':
			self.wick_pen = pg.mkPen('k')
			self.up_candle_brush = pg.mkBrush('w')
			self.down_candle_brush = pg.mkBrush('k')
		else:
			self.wick_pen = pg.mkPen('k')
			self.up_candle_brush = pg.mkBrush('g')
			self.down_candle_brush = pg.mkBrush('r')

	def generate_log_data(self, data):
		# adapted from PlotDataItem applyLogMapping
		if len(data) == 0:
			return data
		log_data = data.copy()
		log_data[0] = data[0]
		with warnings.catch_warnings():
			warnings.simplefilter("ignore", RuntimeWarning)
			log_data[:,1] = np.log10(data[:,1])
			log_data[:,2] = np.log10(data[:,2])
			log_data[:,3] = np.log10(data[:,3])
			log_data[:,4]= np.log10(data[:,4])
		return log_data

	def generatePicture(self):
		# "pre-computing a QPicture object allows paint() to run much more quickly,
		# rather than re-drawing the shapes every time."
		self.picture = QtGui.QPicture()
		p = QtGui.QPainter(self.picture)
		p.setPen(self.wick_pen)
		data = self.data if not self.log_mode[1] else self.log_data
		w = secs_in_freq(self.freq)/3#(width)
		for (time, open, high, low, close) in data:
			p.drawLine(QtCore.QPointF(time, low), QtCore.QPointF(time, high))
			if open > close:
				p.setBrush(self.down_candle_brush)
			else:
				p.setBrush(self.up_candle_brush)
			p.drawRect(QtCore.QRectF(time-w, open, w*2, close-open))
		p.end()
		#TODO: if no wicks at all, it draws a weird vertical line that's infinite (in log scale); get rid of that.
	def paint(self, p, *args):
		p.drawPicture(0, 0, self.picture)

	def boundingRect(self):
		# "boundingRect _must_ indicate the entire area that will be drawn on
		# or else we will get artifacts and possibly crashing.
		# (in this case, QPicture does all the work of computing the bouning rect for us)"
		return QtCore.QRectF(self.picture.boundingRect())

	def setLogMode(self, x, y):
		"""
		When log mode is enabled for the respective axis by setting ``xState`` or
		``yState`` to `True, a mapping according to ``mapped = np.log10( value )``
		is applied to the data. For negative or zero values, this results in a
		`NaN` value.

		based on the addItem source; must be implemented to work properly.
		stolen from pg PlotDataItem
		"""
		if self.log_mode == [x, y]:
			return
		if x == True:
			raise NotImplementedError
		self.log_mode = [x, y]
		self.generatePicture()

	def save_object(self):
		return {'style': self.style,
				'pa_class': self.initial_pa.__class__.__name__,
				'pa_data': self.initial_pa.save_object()}

	@staticmethod
	def gen_from_save_object(o):
		pa_class = getattr(price_action, o['pa_class'])
		pa = pa_class.gen_from_save_object(o['pa_data'])
		return CandlesticksItem(pa, o['style'])

class QQFieldItem(pg.GraphicsObject):
	def __init__(self, data, brush = pg.mkBrush('r')):
		pg.GraphicsObject.__init__(self)
		self.brush = brush
		self.data = data  ## data must have fields: startx, starty, endx, endy
		self.log_data = self.generate_log_data(data)
		self.log_mode = [False, False]
		self.generatePicture()
		# TODO: should the reduced window be set here? look for clues in PlotDataItem.

	def generate_log_data(self, data):
		#adapted from PlotDataItem applyLogMapping
		log_data = data.copy()
		# 'startx', 'starty', 'endx', 'endy'
		with warnings.catch_warnings():
			warnings.simplefilter("ignore", RuntimeWarning)
			log_data[:,1] = np.log10(data[:,1])
			log_data[:,3] = np.log10(data[:,3])
		return log_data

	def generatePicture(self):
		# just couldn't figure out how to draw this in reality.
		self.picture = QtGui.QPicture()
		p = QtGui.QPainter(self.picture)
		p.setPen(pg.mkPen('w'))
		data = self.data if not self.log_mode[1] else self.log_data

		for (startx, starty, endx, endy) in data:
			p.setBrush(self.brush)
			p.setPen(QtCore.Qt.NoPen) #pg.mkPen((0,0,0,0)))
			left, top = startx, max(starty, endy)
			width, height = endx - startx, abs(starty - endy)
			bottom = min(starty, endy)
			# documentation claims that 2nd coordinate is top, but it's bottom apparently.
			# also weird how the current cancdlestick implementation uses open there?
			p.drawRect(QtCore.QRectF(left, bottom, width, height))
		p.end()

	def setLogMode(self, x, y):
		if self.log_mode == [x, y]:
			return
		if x == True:
			raise NotImplementedError
		self.log_mode = [x, y]
		self.generatePicture()

	def boundingRect(self):
		return QtCore.QRectF(self.picture.boundingRect())

	def paint(self, p, *args):
		p.drawPicture(0, 0, self.picture)

class QQRRItem(pg.GraphicsObject, QQDrawing):
	def __init__(self, pos1, pos2, pos3, freq='1Y'):
		pg.GraphicsObject.__init__(self)
		QQDrawing.__init__(self)
		self.sl_brush = pg.mkBrush((255, 0, 0, 120))
		self.tp_brush = pg.mkBrush((0, 125, 125, 120))
		if isinstance(pos1, QQTargetItem):
			self.p1 = pos1
		else:
			self.p1 = QQTargetItem(pos1)
		if isinstance(pos3, QQTargetItem):
			self.p3 = pos3
		else:
			self.p3 = QQTargetItem(pos3)
		if isinstance(pos2, QQTargetItem):
			self.p2 = pos2
		else:
			self.p2 = QQTargetItem(pos2)
		self.p1.setParentItem(self)
		self.p2.setParentItem(self)
		self.p3.setParentItem(self)
		self.p1.setZValue(100)
		self.p2.setZValue(100)
		self.p3.setZValue(100)

		self.current_state = (self.p1.pos(), self.p2.pos(), self.p3.pos())

		end = max(pos2.x(), pos3.x())
		self.sl_field = QQFieldItem(np.array([[pos1.x(), pos1.y(), end, pos2.y()]]), self.sl_brush)
		self.tp_field = QQFieldItem(np.array([[pos1.x(), pos1.y(), end,  pos3.y()]]), self.tp_brush)
		self.sl_field.setParentItem(self)
		self.tp_field.setParentItem(self)
		self.freshly_set = True
		self.freq = freq

		self.label_counter = 0

	@property
	def best_x_position(self):
		return (self.p1.x + self.p2.x + self.p3.x)/3

	def label(self, p2x, p2y):
		return f'simR/R: {self.sim_rr(p2x, p2y)}'

	def appear_active(self):
		self.sl_field.brush = pg.mkBrush((255, 0, 0, 255))
		self.tp_field.brush = pg.mkBrush((0, 125, 125, 255))
		self.sl_field.generatePicture()
		self.tp_field.generatePicture()
		self.sl_field.update()
		self.tp_field.update()

		self.p2.setLabel(self.label(self.p2.x, self.p2.y))

	def stop_appearing_active(self):
		self.sl_field.brush = self.sl_brush
		self.tp_field.brush = self.tp_brush
		self.sl_field.generatePicture()
		self.tp_field.generatePicture()
		self.sl_field.update()
		self.tp_field.update()

		self.p2.setLabel(None)

	def sim_rr(self, p2x, p2y):
		sim_risk = abs(self.p1.y - p2y)
		sim_return = abs(self.p1.y - self.p3.y)
		return sim_return/sim_risk

	def paint(self, p, *args):
		if self.current_state != (self.p1.pos(), self.p2.pos(), self.p3.pos()):
			end = max(self.p2.x, self.p3.x)
			tp_data = np.array([[self.p1.x, self.p1.y, end,  self.p3.y]]) ## data must have fields: startx, starty, endx, endy
			sl_data = np.array([[self.p1.x, self.p1.y, end, self.p2.y]])

			self.tp_field.data = tp_data
			self.tp_field.log_data = self.tp_field.generate_log_data(tp_data)
			self.tp_field.generatePicture()
			self.tp_field.update()

			self.sl_field.data = sl_data
			self.sl_field.log_data = self.sl_field.generate_log_data(sl_data)
			self.sl_field.generatePicture()
			self.sl_field.update()
			self.current_state = (self.p1.pos(), self.p2.pos(), self.p3.pos())

	def boundingRect(self):
		return self.childrenBoundingRect()

	def setLogMode(self, x, y):
		self.p1.setLogMode(x, y)
		self.p2.setLogMode(x, y)
		self.p3.setLogMode(x, y)
		if self.freshly_set:
			#the fields need this bc they dont internally have it
			# (bc here they're initially drawn using actual screen coordinates.)
			self.freshly_set = False
			return
		self.sl_field.setLogMode(x, y)
		self.tp_field.setLogMode(x, y)

	def save_object(self):
		testies = {
			'pos1': self.p1.save_object(),
			'pos2': self.p2.save_object(),
			'pos3': self.p3.save_object(),
			'freq': self.freq,
			'metadata': self.metadata
		}
		return testies

	@staticmethod
	def gen_from_save_object(o):
		p1 = Point(o['pos1']['x'], o['pos1']['y'])
		p2 = Point(o['pos2']['x'], o['pos2']['y'])
		p3 = Point(o['pos3']['x'], o['pos3']['y'])
		item = QQRRItem(p1, p2, p3, freq=o['freq'])
		if 'metadata' in o.keys():
			item.metadata = o['metadata']
		return item

def reformat_pa_data(pa):
# 	pa.data.index.astype(int)/ 10**9  # < does this have no effect
	pa = pa.data.reset_index()
	pa.time = pa.time.astype(int)/ 10**9
	pa = pa[['time', 'open', 'high', 'low', 'close']]
	pa = pa.values
	return pa

def timedelta_from_freq(freq):
	freq = pd.tseries.frequencies.to_offset(freq)
	common_dt = pd.to_datetime("2016-07-31")
	return common_dt + freq - common_dt

def secs_in_freq(freq):
	timedelta = timedelta_from_freq(freq)
	return int(timedelta/pd.Timedelta('1s'))

class QQInteractiveFieldItem(pg.GraphicsObject):
	# NOT finished IMPLEMENTing bc not that important
	def __init__(self, start, end, brush):
		raise NotImplementedError

class QQTargetItem(TargetItem, QQDrawing):
	def __init__(self, *args, **kwargs):
		self.log_mode = [False, False]
		if 'freq' in kwargs:
			self.freq = kwargs['freq']
			del kwargs['freq']
		else:
			self.freq = '1Y'
		if 'name' in kwargs:
			self.name = kwargs['name']
			del kwargs['name']
		else:
			self.name = None
		if 'linked_target_item' in kwargs:
			self.linked_target_item = kwargs['linked_target_item']
			del kwargs['linked_target_item']
		else:
			self.linked_target_item = None
		# TODO: seems like a dirty way to handle this ^^
		super().__init__(*args, **kwargs, pen=pg.mkPen(color='b', width=2), symbol='o')
		QQDrawing.__init__(self)
		self.freshly_set = True
		self.qqparent = None
		self.setZValue(200)

	@property
	def best_x_position(self):
		return self.x

	def mouseDragEvent(self, ev):
		"""
		ripped off from the superclass, added modifier, not my fault its that hard to read.
		"""
		if not self.movable or ev.button() != QtCore.Qt.MouseButton.LeftButton:
			return

		if ev.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier and \
			self.linked_target_item: # if shift is held and have linked item
			snap_y = True
		else:
			snap_y = False

		if ev.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and \
			self.linked_target_item:
			drag_both = True
			position_delta = self.pos() - self.linked_target_item.pos()
		else:
			drag_both = False

		ev.accept()
		if ev.isStart():
			self.symbolOffset = self.pos() - self.mapToView(ev.buttonDownPos())
			self.moving = True

		if not self.moving:
			return

		if snap_y:
			snapped_position = (self.symbolOffset + self.mapToView(ev.pos()))
			snapped_position.setY(self.linked_target_item.y)
			self.setPos(snapped_position)
		else:
			self.setPos(self.symbolOffset + self.mapToView(ev.pos()))

		if drag_both:
			self.linked_target_item.setPos(self.pos() - position_delta)


		if ev.isFinish():
			self.moving = False
			self.sigPositionChangeFinished.emit(self)

	def setParentItem(self, parent):
		# adds the qqparent.
		# the qqparent is used by me in python bc the regular parent
		# is not normally accessible for some reason (probably sth w cpp)
		self.qqparent = parent
		super().setParentItem(parent)
		if hasattr(parent, 'freq'):
			self.freq = parent.freq
		# todo: add this for qqdrawings in general perhaps.

	def save_object(self):
		return {'x': self.x, 'y': self.y, 'name': self.name, 'freq': self.freq, 'metadata': self.metadata}

	@staticmethod
	def gen_from_save_object(o):
		item = QQTargetItem(Point(o['x'], o['y']), name=o['name'], freq=o['freq'])
		if 'metadata' in o.keys():
			item.metadata = o['metadata']
		return item

	@property
	def x(self):
		return self.pos().x()

	@property
	def y(self):
		return self.pos().y()

	def setLogMode(self, x, y):
		if self.freshly_set:
			# when a TargetItem is placed, it gets an immediate setLogMode call with the present state.
			self.log_mode = [x, y]
			self.freshly_set = False
			return

		if self.log_mode == [x, y]:
			# no changes
			return
		if x is True:
			raise NotImplementedError
		self.log_mode = [x, y]

		# modify the position
		if self.log_mode[1]:
			self._vs_pos = Point(
				self._pos.x(),
				np.log10(self._pos.y())
			)
		else:
			self._vs_pos = Point(
				self._pos.x(),
				10**self._pos.y()
			)
		self.viewTransformChanged()
		super().setPos(self._vs_pos)

class QQGraphicsLineItem(QGraphicsLineItem):
	def __init__(self, *args, name=None, **kwargs):
		self.log_mode = [False, False]
		self.name = name
		super().__init__(*args, **kwargs)
		self.freshly_set = True

	def save_object(self):
		# I tihnk this literally never gets called or used. - remove?
		l = self.line()
		return {
			'pen': self.pen(),
			'x1': l.x1(),
			'x2': l.x2(),
			'y1': l.y1(),
			'y2': l.y2(),
			'name': self.name
		}

	@staticmethod
	def gen_from_save_object(o):
		# I think this literally never gets called or used - remove?
		return QQGraphicsLineItem(o['x1'], o['y1'],o['x2'], o['y2'], name=o['name'], pen = o['pen'])

	def setLogMode(self, x, y):
		if self.freshly_set:
			# when first drawn, setlogmode is called with the present state.
			self.log_mode = [x, y]
			self.freshly_set = False
			return
		if self.log_mode == [x, y]:
			# no change
			return
		if x is True:
			raise NotImplementedError
		self.log_mode = [x, y]

		# modify the position
		line = self.line()
		if self.log_mode[1]:
			newy1 = np.log10(line.y1())
			newy2 = np.log10(line.y2())
		else:
			newy1 = 10**(line.y1())
			newy2 = 10**(line.y2())
		new_line = QLineF(line.x1(), newy1, line.x2(), newy2)
		self.setLine(new_line)

class Trendline(pg.GraphicsObject, QQDrawing): #or graphicsobject? or neiter? not sure
	def __init__(self, start:Point, end:Point, name=None, color='b', width=2, freq='1Y'):
		pg.GraphicsObject.__init__(self)
		QQDrawing.__init__(self)
		self.pen = pg.mkPen(color, width=width)
		self.name = name

		self.start = QQTargetItem(start)
		self.end = QQTargetItem(end, linked_target_item=self.start)
		self.start.linked_target_item = self.end
		self.start.setParentItem(self)
		self.end.setParentItem(self)

		self.line = QQGraphicsLineItem(self.gen_line(), self)
		self.line.setPen(self.pen)

		self.appearing_active = False

		self.freq = freq

	@property
	def best_x_position(self):
		return (self.start.x + self.end.x)/2

	def appear_active(self):
		active_pen = pg.mkPen('r', width=4, style=QtCore.Qt.DashLine)
		self.line.setPen(active_pen)
		self.appearing_active = True

	def stop_appearing_active(self):
		if self.appearing_active:
			self.set_color(self.pen.color())
			self.line.setPen(self.pen)
		self.appearing_active = False

	def set_color(self, color):
		self.pen.setColor(color)
		self.line.setPen(self.pen)

	def set_width(self, width):
		self.pen.setWidth(width)
		self.line.setPen(self.pen)

	def save_object(self):
		color = (self.pen.color().red(), self.pen.color().green(), self.pen.color().blue(), self.pen.color().alpha())
		return {
			'startx': self.start.x,
			'starty': self.start.y,
			'endx': self.end.x,
			'endy': self.end.y,
			'name': self.name,
			'color': color,
			'width': self.pen.width(),
			'freq': self.freq,
			'metadata': self.metadata
		}

	@staticmethod
	def gen_from_save_object(o):
		line = Trendline(Point(o['startx'], o['starty']), Point(o['endx'], o['endy']), o['name'], color=o['color'], width=o['width'], freq=o['freq'])
		if 'metadata' in o.keys():
			line.metadata = o['metadata']
		return line

	@property
	def angle(self):
		# gives the 'objective' lower angle, used for the channel system
		# drawing.
		width = abs(self.end.x - self.start.x)
		height = abs(self.end.y - self.start.y)
		return math.atan(height/width)

	@property
	def uptrending(self):
		return self.start.y < self.end.y

	def gen_line(self):
		start = PySide6.QtCore.QPointF(*self.start.pos())
		end = PySide6.QtCore.QPointF(*self.end.pos())
		self.prev_line = PySide6.QtCore.QLineF(start, end)
		return self.prev_line

	def boundingRect(self):
		return self.line.boundingRect()

	def paint(self, p, *_):
		#TODO: minor performance enchancement by not really doing this every time?
		self.line.setLine(self.gen_line())

	def setLogMode(self, x, y):
		self.start.setLogMode(x, y)
		self.end.setLogMode(x, y)
		self.line.setLogMode(x, y)

class LineSystem(pg.GraphicsObject, QQDrawing):
	def __init__(self, trendline:Trendline, name=None, freq='1Y'):
		pg.GraphicsObject.__init__(self)
		QQDrawing.__init__(self)
		self.name = name
		self.trendline = trendline
		self.trendline.setParentItem(self)
		self.trendline.start.setParentItem(self)
		self.trendline.end.setParentItem(self)
		self.appearing_active = self.trendline.appearing_active

		self.pen = self.trendline.pen
		self.parallels = []

		self.freq = freq
	def set_color(self, color):
		self.trendline.set_color(color)
		for parallel in self.parallels:
			parallel.set_color(color)

	@property
	def best_x_position(self):
		return self.trendline.best_x_position

	def appear_active(self):
		self.trendline.appear_active()
		for parallel in self.parallels:
			parallel.appear_active()
		self.appearing_active = self.trendline.appearing_active

	def stop_appearing_active(self):
		self.trendline.stop_appearing_active()
		for parallel in self.parallels:
			parallel.stop_appearing_active()
		self.appearing_active = self.trendline.appearing_active


	def set_width(self, width):
		self.trendline.set_width(width)
		for parallel in self.parallels:
			parallel.set_width(width)

	def save_object(self):
		trendline_save_object = self.trendline.save_object()
		return {
			'trendline': trendline_save_object,
			'name': self.name,
			'parallels': [p._save_object() for p in self.parallels],
			'freq': self.freq,
			'metadata': self.metadata
		}

	@staticmethod
	def gen_from_save_object(o):
		trendline = Trendline.gen_from_save_object(o['trendline'])
		sys = LineSystem(trendline, o['name'], freq=o['freq'])
		if 'metadata' in o.keys():
			sys.metadata = o['metadata']
		for p in o['parallels']:
			parallel = sys.add_parallel(Point(p['x'], p['y']), initially_set_log_mode=False)
			if 'metadata' in p.keys():
				parallel.metadata = p['metadata']
		return sys

	def add_parallel(self, position, initially_set_log_mode=True):
		parallel = Parallel(position, self, initially_set_log_mode=initially_set_log_mode)
		self.parallels.append(parallel)
		return parallel

	def boundingRect(self):
		return self.trendline.boundingRect()
		# return self.childrenBoundingRect() #TODO: shouldnt this b better?

	def paint(self, p, *_):
		pass

	def setLogMode(self, x, y):
		self.trendline.setLogMode(x, y)
		for parallel in self.parallels:
			parallel.setLogMode(x, y)

class Parallel(pg.GraphicsObject, QQDrawing):
	"""
	only usable w channel system
	"""
	def appear_active(self):
		self.pen = self.qqparent.trendline.line.pen()
		self.parallel.setPen(self.pen)

	@property
	def best_x_position(self):
		return self.qqparent.best_x_position

	def stop_appearing_active(self):
		self.pen = self.qqparent.trendline.line.pen()
		self.parallel.setPen(self.pen)

	def set_color(self, color):
		self.pen.setColor(color)
		self.parallel.setPen(self.pen)

	def set_width(self, width):
		self.pen.setWidth(width)
		self.parallel.setPen(self.pen)

	def __init__(self, position, parent, name=None, initially_set_log_mode=True, freq='1Y'):
		pg.GraphicsObject.__init__(self)
		QQDrawing.__init__(self)
		self.name = None
		self.point = None
		self.parallel = None
		self.qqparent = parent
		self.pen = self.qqparent.pen
		self.add_point(position)

		self.setParentItem(parent)
		self.freq = freq

		if initially_set_log_mode:
			self.setLogMode(self.qqparent.trendline.start.log_mode[0], self.qqparent.trendline.start.log_mode[1])
		# ^^ because adding a parallel to a system does not call setLogMode,
		# since it is only called when log mode is changed or when it is joined
		# to the main chart (?)
	def _save_object(self):
		return {'x': self.point.x, 'y': self.point.y, 'name': self.name, 'metadata': self.metadata}

	@staticmethod
	def _gen_from_save_object(o, parent):
		raise NotImplementedError
		# bit diff from other ones bc this always has a parent and is only ever called from the parent
		return Parallel(Point(o['x'], o['y']), parent, o['name'])

	def get_height(self, position:Point):
		# find v distance from line (trigonometry innit)
		# CASE A: uptrending
		#									--/ |
		#	 ----------  point			  -/	|
		#	 |				|	  trend--/		|
		#  h |				|		--/			|
		#	 |				|	 --/			|
		#	 |				|  -/				|
		#	 ------------	|-/					|
		#				 --/|					|
		#			  --/	|					|
		#		   --/		| <--g				|
		#		 -/			|					|
		#	  --/			|					|
		#	-/--------------|-------------------|
		#	|	   C		|
		if self.qqparent.trendline.uptrending:
			C = abs(self.qqparent.trendline.start.x - position.x())
			g = C * math.tan(self.qqparent.trendline.angle)
			gh = position.y() - self.qqparent.trendline.start.y
			h = gh - g
			return h
		else:
			C = abs(self.qqparent.trendline.end.x - position.x())
			g = C * math.tan(self.qqparent.trendline.angle)
			gh = position.y() - self.qqparent.trendline.end.y
			h = gh - g
			return h

	def add_point(self, position:Point):
		h = self.get_height(position)
		point = QQTargetItem(position)
		point.setParentItem(self.qqparent)

		parallel = QQGraphicsLineItem(self.gen_parallel(h), self)
		parallel.setPen(self.pen)

		self.parallel = parallel
		self.point = point

	def gen_parallel(self, height):
		latest_line = self.qqparent.trendline.prev_line
		newy1 = latest_line.y1() + height
		newy2 = latest_line.y2() + height
		return PySide6.QtCore.QLineF(latest_line.x1(), newy1, latest_line.x2(), newy2)

	def regen_line(self):
		h = self.get_height(self.point.pos())
		return self.gen_parallel(h)

	def boundingRect(self):
		return self.parallel.boundingRect()

	def paint(self, p, *_):
		#TODO: some performance enhancements by not doing this every time
		self.parallel.setLine(self.regen_line())
		pass

	def setLogMode(self, x, y):
		self.point.setLogMode(x, y)
		self.parallel.setLogMode(x, y)

import math
import numpy as np
import pandas as pd
import requests
import time

class OHLCPriceAction:
	""" 
	Data must be pandas df and contain an index named "time".
	* price_action.data - pandas DataFrame (functional)
	* price_action.array - numpy ndarray (fast)
	price_action[] accesses the array.
	TODO: simplify
	"""
	def __init__(self, data, resolution='1min', label="no_label"):
		# TODO: determine; for now we rely on .resample() setting this
		# NB: this can probably be done w pd.infer_freq(data.index), just needs testing
		self.resolution = resolution
		self.label = label

		self.data = data

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, data):
		if not isinstance(data.index, pd.DatetimeIndex):
			data.index = pd.to_datetime(data.index)
		self._data = data
		self.array = data.to_records()
		self.array.flags.writeable = False

	def copy(self):
		return OHLCPriceAction(self.data, self.resolution, self.label)

	def __repr__(self):
		range_ = f"range {self.range}"
		return f"PA({self.label}); {range_}"

	def __getitem__(self, index):
		return self.array[index]

	@property
	def time(self):
		return self[-1]["time"]

	@property
	def range(self):
		""" Returns min and max of time """
		return [self[0].time, self[-1].time]

	def resample(self, freq, cut_partial_candles=False):
		# see https://stackoverflow.com/questions/24635721/how-to-compare-frequencies-sampling-rates-in-pandas
		common_dt = pd.to_datetime("2016-07-31") #date choice is important, this is not random.
		assert common_dt + pd.tseries.frequencies.to_offset(freq) >= \
			   common_dt + pd.tseries.frequencies.to_offset(self.resolution)
		ohlc_transform = {"open": "first", "high": "max", "low": "min",
						  "close": "last", "volume": "sum"}
		counts = self.data.close.resample(freq).count()
		data = self.data.resample(freq).agg(ohlc_transform)

		if cut_partial_candles:
			full_bin = counts.iloc[-2]	# assume that the new freq is divisible by 1 minute
			first_bin, last_bin = counts.iloc[0], counts.iloc[-1]
			idxs = slice(0 if first_bin == full_bin else 1,
						 None if last_bin == full_bin else -1)
			pa = OHLCPriceAction(data[idxs], freq, self.label)
		else:
			pa = OHLCPriceAction(data, freq, self.label)
		return pa

	def save_object(self):
		return {'label': self.label,
				'exchange': 'undefined',
				'data': self.data_source,
				'initial_resolution': self.resolution}
	
	def gen_from_save_object(o):
		pa = OHLCPriceAction(o['data'], o['initial_resolution'], o['label'])
		return pa

	def update(self):
		raise NotImplementedError()

class BinancePriceAction(OHLCPriceAction):
	def __init__(self, data_source, resolution='1min', label="no_label", symbol=None):
		self.data_source = data_source
		self.symbol = symbol
		candles = open(data_source, 'r').read()
		candles = candles.strip('][').replace('"', "").split("],[")
		candles = [[float(value) for value in candle.split(",")] for candle in candles]
		candles = np.array(candles)
		candles[:,0] = candles[:,0]*1000000
		# TODO: otime or ctime?
		data = pd.DataFrame(candles, index=candles[:,0], columns=['otime', 'open', 'high', 'low', 'close', 'volume', 'ctime', 'quote_volume', 'num_trades', 'taker_buy_base_volume', 'taker_buy_quote_volume', 'unused_field'])
		data.index.rename('time', inplace=True)
		super().__init__(data, resolution, label)


	def copy(self):
		return BinancePriceAction(self.data_source, self.resolution, self.label, self.symbol)
	
	def save_object(self):
		return {'label': self.label,
				'exchange': 'binance',
				'data_source': self.data_source,
				'initial_resolution': self.resolution,
				'symbol': self.symbol}
	
	def gen_from_save_object(o):
		pa = BinancePriceAction(o['data_source'], o['initial_resolution'], o['label'], o['symbol'])
		return pa
	
	def update(self):
		end = int((pd.Timestamp(time.time()*1e9)-pd.Timedelta('1min')).timestamp())
		start = int((pd.Timestamp(self.data.index[-1])-pd.Timedelta('1min')).timestamp())

		gettable_string=f"https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval={self.binance_interval}&startTime={start*1000}&endTime={end*1000}"
		candles = requests.get(gettable_string)
		candles = candles.json()
		import pdb
		try:
			candles = np.array(candles, dtype=float)
		except:
			print("updating chart failed; debugging")
			pdb.set_trace()

		candles[:,0] = candles[:,0]*1000000
		new_data = pd.DataFrame(candles, index=candles[:,0], columns=['otime', 'open', 'high', 'low', 'close', 'volume', 'ctime', 'quote_volume', 'num_trades', 'taker_buy_base_volume', 'taker_buy_quote_volume', 'unused_field'])
		new_data.index.rename('time', inplace=True)

		total_data = pd.concat([self.data, new_data], axis=0)
		
		self.data = total_data
	
	@property
	def binance_interval(self):
		if 'min' in self.resolution:
			return self.resolution.replace('min', 'm')
		else:
			return self.resolution


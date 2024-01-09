from qraph import Qraph
import numpy as np
from price_action import OHLCPriceAction, BinancePriceAction
import pandas as pd
import pdb

pa = BinancePriceAction('test_candles2', '1min', 'test_data', 'BTCUSDT')

q = Qraph()
q.add_candlestick_chart(pa)
line = {1704371880: 43820, 1704391880: 43820, 1704401879: 44400}
l = q.add_line(line, width=2)
s = q.add_scatter({1704385818.5410824: 43750, 1704390133.8042243: 43800})
q.add_scatter({1704389119.4595015: 44250, 1704394810.105318: 44200}, symbol='t', color2='k')
q.show()
 

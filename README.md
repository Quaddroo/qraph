# Qraph

![showcase](https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjVpMGlqeWhqM3F1aXl3ZjVjd29pY2RveHIxd3M5MjJpbmhmNTh0dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ItxqVuG7kGHFFNgxsY/source.gif)

Qraph is a tool for candlestick charting, with a few useful properties that
other tools like Tradingview seem to lack:

    + SPEED
    + Dynamic timeframe change
    + Changing timeframe maintains current chart position
    + Drawing tools stay at their timeframes and lower, and don't overshadow higher timeframes (unless explicitly forced to)

It is built on pyqtgraph, and so anything that can be done with pyqtgraph can be
done with it.

Qraph is in alpha, so expect many issues.

## Example

```
git clone https://github.com/Quaddroo/qraph.git
pip install -r requirements.txt
python3 example.py
```

## Design principle
It needs to be FAST.
It needs to be EASY.

## Some features
    + Automatic timeframe change
    + Basic drawing tools
    + Automatic drawing tool timeframe setting as most traders would want it
    + Saving drawings
    + Extremely basic chart live-updating
    + Log scale works on candles and provided drawing tools

## Controls
### Navigation
Left mouse button + drag to pan    
Right mouse button + drag to resize the screen    
Right mouse button to bring up the pyqtgraph menu for log-scale settings and others


### Drawings
Right mouse button on a drawing handle to select it    
Shift while drawing lines or parallels to constrain to horizontal drawing    
Ctrl while drawing lines or parallels to pan (the line or the parallel)    
s - start drawing parallels    
t - start trading trendline    
r - start drawing rr tool    
delete - delete selected drawing    
escape - exit selection    

## Some issues
    + Startup needs to be FASTER
    + Sometimes some parts of the screen do not redraw until the screen is
      panned (pyqtgraph issue?).
    + When forced to resample to a tiny timeframe on a high zoom-out, starts
      lagging (need to simplify the drawing for this to work).
    + Auto-zoom to drawing feature does not work.
    + Log mode code is dirty, should fix pygtgraph code instead.
    + Pyqtgraph auto-culling does not work, so there is sub-optimal manual code
      written for it.

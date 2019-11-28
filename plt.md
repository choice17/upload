## MATPLOTLIB utils   

Reference  

* plt subplot  
* [axis labels for subplot](https://stackoverflow.com/questions/6963035/pyplot-axes-labels-for-subplots)  
* [subplot](https://morvanzhou.github.io/tutorials/data-manipulation/plt/4-1-subpot1/)  
* [add mouse callback](https://stackoverflow.com/questions/25521120/store-mouse-click-event-coordinates-with-matplotlib)  
* [add verticle line](https://matplotlib.org/3.1.1/api/axes_api.html#matplotlib.axes.Axes)  
* [set title](https://stackoverflow.com/questions/12444716/how-do-i-set-the-figure-title-and-axes-labels-font-size-in-matplotlib)  

Below is the python script for animation   

```python
class PLT(object):

	def __init__(self, title='PLOT'):
		self.cid = None
		self.fig = None
		self.ax = []
		self.bx = []
		self.title = title

	def onclick(self, event):
    """ allow animation: and extract position in the plot """
		global g_ctrl
		g_ctrl.x, g_ctrl.y = event.xdata, event.ydata 
		print(g_ctrl.x, g_ctrl.y, g_ctrl.cnt)
		g_ctrl.cnt += 1
		if g_ctrl.cnt == 3:
			self.fig.canvas.mpl_disconnect(self.cid)
			g_ctrl.cnt = 0
			self.repeat()
		return


	def repeat(self):
		_len = len(self.data)
		self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
		for i in range(_len):
			num = _len * 100 + 10 + i + 1
			self.data[i][1] += 500
			y = self.data[i][1]
			self.ax[i].set_ylim(0, y.max())
			self.bx[i].set_ydata(self.data[i][1])
			self.ax[i].set_ylabel(self.data[i][0])
		plt.draw()

	def plot(self, data, times=None):
		self.data = data
		_len = len(data)
		self.fig = plt.figure()
    """ Add button handler """
		self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
		self.ax = []
		for i in range(_len):
			num = _len * 100 + 10 + i + 1
			self.ax.append(self.fig.add_subplot(num))
			y = data[i][1]
			bx, = self.ax[i].plot(data[i][1])
      """ bx allows set ydata!!! """
			self.bx.append(bx)      
			self.ax[i].set_ylabel(data[i][0])
			ymin = y.min()
			ymax = y.max()
			if ymin == ymax and ymin == 0:
				ymin = 0
				ymax = 1
			if times is not None:
				for t in times:
          """ Allow vertical line"""
					self.ax[i].vlines(x=t,ymin=ymin,ymax=ymax,color='r')
    """ Allow redraw """
		self.fig.canvas.draw()
		self.fig.suptitle(self.title, fontsize=12)
		plt.show()
```

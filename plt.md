## MATPLOTLIB utils   

Reference  

* plt subplot  
* [axis labels for subplot](https://stackoverflow.com/questions/6963035/pyplot-axes-labels-for-subplots)  
* [subplot](https://morvanzhou.github.io/tutorials/data-manipulation/plt/4-1-subpot1/)  
* [add mouse callback](https://stackoverflow.com/questions/25521120/store-mouse-click-event-coordinates-with-matplotlib)  
* [add verticle line](https://matplotlib.org/3.1.1/api/axes_api.html#matplotlib.axes.Axes)  
* [set title](https://stackoverflow.com/questions/12444716/how-do-i-set-the-figure-title-and-axes-labels-font-size-in-matplotlib)  
* [put legend out of figure](https://kite.com/python/examples/4997/matplotlib-place-a-legend-outside-of-plot-axes)  
* [grid plot](https://jakevdp.github.io/PythonDataScienceHandbook/05.12-gaussian-mixtures.html)  

Below is the python script for animation   
* [example 1 anmination](#example_1)  
* [example 2 subplot utils](#example_2)  

## example_1

// aninmation

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

```python  
	"""get the axis position and set the position and put legend position"""
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.85, box.height])
        plt.legend(('Predicted True', 'Predicted Wrong',*STATE.STATE_STR[:CLASS]),
                   loc=pos,bbox_to_anchor=(1,0.5))
```

```python
def plot_digits(data):
    fig, ax = plt.subplots(10, 10, figsize=(8, 8),
                           subplot_kw=dict(xticks=[], yticks=[]))
    fig.subplots_adjust(hspace=0.05, wspace=0.05)
    for i, axi in enumerate(ax.flat):
        im = axi.imshow(data[i].reshape(8, 8), cmap='binary')
        im.set_clim(0, 16)
plot_digits(digits.data)
```

## example_2  

subplot utils

1. plt.figure(figsize=figsize)
2. plt.subplot(Len, 1, i+1)
3. figure plot(x, y, symbol, color, width)
4. axis position
box = ax.get_position()
`ax.set_position([box.x0, box.y0, box.width*0.85, box.height])`
5. plt.legend((tuple name for lines), loc='center left', bbox_to_anchor=(1,0.5))
6. plt.xlabel, plt.ylabel

```
plot(datalist, mask, CFG, [FeatureLabels[i] for i in FEATURE_IDX], pred_ally, featureidx=0, figsize=(16,24), cls=2)

def plot(datalist, masklist, cfglist, featureLabels, predyall, featureidx=4, figsize=(12,8), cls=-1, pos='center left'):
    color = ["grey", "red", 'wheat', "orange", "navy","black"]
    marker = [".", ".", ".", ".",".","."]
    if cls == -1:
        marker = ["o" for _ in marker]
    else:
        marker[cls] = "o"
    Len = len(datalist)

    # figure width height
    plt.figure(figsize=figsize)
    for i in range(Len):
        xar = np.arange(datalist[i].shape[0])
        #num = Len * 100 + 10 + i + 1
        mask = masklist[i]
        xx = datalist[i][:,featureidx]
        
	# figure subplot index
        ax = plt.subplot(Len, 1, i+1)
	
	# figure plot(x, y, symbol, color, width)
        ax.plot(xar, datalist[i][:,featureidx], 'b')
        ax.plot(xar[mask], datalist[i][mask,featureidx], 'x', color='orange', linewidth=3)

        for k in range(CLASS+1):
            clsmask = (predyall[i] == k) * mask
            ax.plot(xar[clsmask], datalist[i][clsmask,featureidx], marker[k], color=color[k], linewidth=3)
        
	# subplot axis position resizing
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.85, box.height])
        #plt.legend(["blue", "green"], loc='center left', bbox_to_anchor=(1, 5))

        #handles, _ = ax.get_legend_handles_labels()
        #lgd = ax.legend(handles, ('Predicted True', 'Predicted Wrong',*STATE.STATE_STR[:CLASS]),
        #                loc=pos, bbox_to_anchor=(1,0.5))
    
        plt.legend(('Predicted True', 'Predicted Wrong',*STATE.STATE_STR[:CLASS]),
                   loc=pos,bbox_to_anchor=(1,0.5))

        # figure vertical line over all subplot
        for j in cfglist[i].TIMES:
            plt.vlines(j, ymin=xx.min(), ymax=xx.max(), color='red')
        plt.ylabel("video 0%d" % (i+1))
    plt.xlabel(featureLabels[featureidx] + ' vs frame number')
```

## example_3 

heatmap for confusion matrix for sns

```
cm_train = confusion_matrix(seq_pred_y, seq_train_y)
plt.figure(figsize=(12,6))
ax= plt.subplot()
sns.heatmap(cm_train, annot=True, ax = ax)
ax.set_ylabel('Predicted labels');ax.set_xlabel('True labels'); 
ax.set_title('Confusion Matrix'); 
ax.xaxis.set_ticklabels(STATE.STATE_STR); ax.yaxis.set_ticklabels(STATE.STATE_STR);
```

## example_4  

dot utils

```
FILE = "stateflow.dot"
dotstr ="\
digraph D {\n\
 label = \"State Flow\";\
  EMPTY -> {FILLING, LINGER, EMPTY}\n\
  FILLING -> {FILLING, FILLED, LINGER, EATING}\n\
  FILLED -> {FILLED, LINGER, EATING}\n\
  EATING -> {LINGER, EATING}\n\
  EATING -> {EMPTY} [ label=\"No FILLED Prev Or Have EATING Prev\"]\
  LINGER -> {FILLED, EMPTY, LINGER}\n\
  LINGER -> {FILLING} [ label=\"No FILLED Prev\"]\
  LINGER -> {EATING} [ label=\"Have FILLED/FILLING Prev\"]\
}\n\
"
with open(FILE, 'w') as f:
    f.write(dotstr)

!dot -Tpng stateflow.dot -o stateflow.png
img = plt.imread("stateflow.png")
plt.figure(figsize=(16,10))
plt.axis("off")
plt.imshow(img)
```



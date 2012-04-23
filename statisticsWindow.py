from PySide.QtCore import *
from PySide.QtGui import *

import sys, os, random,csv

import matplotlib as mpl
mpl.use('Qt4Agg')
mpl.rcParams['backend.qt4']='PySide'
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolBar
from matplotlib.figure import Figure



class StatisticsWindow(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('Statistics:')
        self.parent=parent
        self.figure,self.axes = plt.subplots(2,1,sharex=True)
        self.figure.set_size_inches((5.0,4.0))
        self.canvas=FigureCanvas(self.figure)
        self.canvas.setParent(self)       
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        #commented away as it causes segmentation faults in my ubuntu, even though
        #it works fine in my windows 7 computer.
        #self.mpl_toolbar = NavigationToolBar(self.canvas,self)         
        #layout.addWidget(self.mpl_toolbar)
        self.setLayout(layout)
        self.dataChanged()
        
    def draw(self):
        self.canvas.draw()
    
    def closeEvent(self,event):
        self.parent.closeStatWindow()
        self.close()
        
    def exportStats(self):
        dialog = QFileDialog(self, "Choose a filename and type to save to, suffix declares type","./stats.csv")
        filetypes = self.canvas.get_supported_filetypes_grouped().items()
        filetypes.append(('Spreadsheet',['csv']))
        filetypes.sort()
        default_filetype = 'csv'
        filters = []
        selectedFilter = None
        for name, exts in filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = '%s (%s)' % (name, exts_list)
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)
        filters = ';;'.join(filters)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter(filters)
        dialog.selectNameFilter(selectedFilter)
        dialog.setViewMode(QFileDialog.Detail)

        if not dialog.exec_():
            return
        fname = dialog.selectedFiles()
        if not fname[0]:
            return
        fname=fname[0]
        if not '.' in fname:
            fname+='.csv'
        self.dataChanged()
        if '.csv' in fname:
            with open(fname, 'wb') as f:
                w = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE)
                w.writerow(["Total Eaten:", "Total Walked:"])
                for i in range(len(self.parent.statEaten)):
                    w.writerow([self.parent.statEaten[i],
                                self.parent.statWalked[i]])
        else:
            try:
                self.canvas.print_figure( unicode(fname) )
            except Exception, e:
                QMessageBox.critical(
                    self, "Error saving file", str(e),
                    QMessageBox.Ok, QMessageBox.NoButton)   
    
    #when year changes and statistical data updates, clear old graph
    #and draw a new one
    def dataChanged(self):
        
        #x-axes data
        x=range(1,len(self.parent.statEaten)+1)
        self.axes[0].clear()
        self.axes[1].clear()
        for label in self.axes[0].get_xticklabels():
            label.set_visible(False)
        self.axes[0].set_ylabel("Food eaten")
        self.axes[1].set_ylabel("Tiles walked")
        self.axes[1].set_xlabel("Generation")
        
        for ax in self.axes:
            ax.grid(True)
            
        l1=self.axes[0].plot(x,self.parent.statEaten,'b-',label='current')[0]
        l2=self.axes[0].plot(x,self.parent.statAverageEaten,'r--',label='average')[0]
        leg=self.axes[0].legend(bbox_to_anchor=(0.,1.02,1.,.102),loc=3,ncol=2,mode="expand",borderaxespad=0)
        self.axes[0].fill_between(l1.get_xdata(),
                                  l1.get_ydata(),
                                  l2.get_ydata(),
                                  where=l1.get_ydata()>l2.get_ydata(),
                                  facecolor='blue',
                                  alpha=0.2,
                                  interpolate=True)
        self.axes[0].fill_between(l1.get_xdata(),
                                  l1.get_ydata(),
                                  l2.get_ydata(),
                                  where=l1.get_ydata()<l2.get_ydata(),
                                  facecolor='red',
                                  alpha=0.2,
                                  interpolate=True)        

        l1,l2=self.axes[1].plot(x,self.parent.statWalked,'b-',
                          x,self.parent.statAverageWalked,'r--')
                
        self.axes[1].fill_between(l1.get_xdata(),
                                  l1.get_ydata(),
                                  l2.get_ydata(),
                                  where=l1.get_ydata()>l2.get_ydata(),
                                  facecolor='blue',
                                  alpha=0.2,
                                  interpolate=True)
        self.axes[1].fill_between(l1.get_xdata(),
                                  l1.get_ydata(),
                                  l2.get_ydata(),
                                  where=l1.get_ydata()<l2.get_ydata(),
                                  facecolor='red',
                                  alpha=0.2,
                                  interpolate=True)

import random

__author__ = 'aberg'
#!/usr/bin/env python

import sys
import time

if True:
    from PySide import QtGui
    from PySide import QtCore
else:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

    QtCore.Signal = QtCore.pyqtSignal

TOTAL_WIDGETS = 10


class Worker(QtCore.QRunnable, QtCore.QObject):
    processed = QtCore.Signal(int)
    finished = QtCore.Signal()

    def __init__(self, parent=None):
        # IMPORTANT: We must call the constructors of *both* parents.
        QtCore.QObject.__init__(self, parent)
        QtCore.QRunnable.__init__(self, parent)

    def run(self):
        for i in xrange(TOTAL_WIDGETS):
            # We sleep first to simulate an operation taking place.
            time.sleep(random.uniform(.1, 1.0))
            print 'Thread: {0}, Processed: {1}'.format(
                QtCore.QThread.currentThread(), i)
            self.processed.emit(i + 1)

        # Must manually emit the finished signal.
        self.finished.emit()


class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self._thread_pool = QtCore.QThreadPool.globalInstance()


        # IMPORTANT: Don't quit the app until the thread has completed.
        # Prevents errors like:
        #
        #     QThread: Destroyed while thread is still running
        #

        # QThreadPool.waitForDone() is, unfortunately, not a slot.
        QtGui.QApplication.instance().aboutToQuit.connect(
            lambda: self._thread_pool.waitForDone())

        self._layout = QtGui.QVBoxLayout(self)
        self._add_button = QtGui.QPushButton('Start New Task')
        self._layout.addWidget(self._add_button)
        self._add_button.clicked.connect(self._start_new_task)

    def on_finish(self, widget):
        print 'finish', widget
        widget.close()

    def closeEvent(self, QCloseEvent):
        print 'close event'

    def _start_new_task(self):
        task = Worker()
        progress_bar = QtGui.QProgressBar()
        progress_bar.setRange(0, TOTAL_WIDGETS)
        task.processed.connect(progress_bar.setValue)
        task.finished.connect(lambda x = progress_bar: self.on_finish(x))
        self._layout.addWidget(progress_bar)
        self._thread_pool.start(task)
        print self._thread_pool.activeThreadCount()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.raise_()
    raise SystemExit(app.exec_())
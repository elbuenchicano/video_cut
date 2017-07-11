import cv2
import numpy
import sys
import yaml
import re
import glob, os

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QAction
from PyQt5.uic  import loadUi
from video      import video_sequence_by1, video_sequence_byn
from PyQt5.QtGui import QImage, QPixmap, QIcon

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def mat2Qpix(frame):
    he, wi, ch = frame.shape
    bytes   = 3 * wi
    qImg    = QImage(frame.data, wi, he, bytes, QImage.Format_RGB888)
    pix     = QPixmap(qImg)
    return pix

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
################################################################################
################################################################################
#class Main(QMainWindow, Ui_MainWindow):
class Main(QMainWindow):
    #constructor................................................................
    def __init__(self):
        super(Main, self).__init__()

        #loading qtcreator ui
        self.ui = loadUi('mainwindow.ui')
        
        self.ui.btn_play.clicked.connect(self.btnPlay) 
        self.ui.btn_record.clicked.connect(self.btnRecord) 
        self.ui.btn_record_step.clicked.connect(self.btnRecordStep) 

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        self.ui.action_open.setShortcut('Ctrl+O')
        self.ui.action_open.setStatusTip('Exit application')
        self.ui.action_open.triggered.connect(self.btnFileDialog)

        
      
        self.ui.show()    
#button filedialog..............................................................
    def btnFileDialog(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     'Open file',
                                                     'Z:\\tmp\\Anomalies\\Videos\\Bank',
                                                     "Video files (*.avi; *.yml; *.mp4)")
        self.ui.edt_file.setText(file[0])
        
        #loading video
        if len(file[0]) == 0: 
            return

        self.video =  video_sequence_by1(file[0])
        fps = str('%.2f'%(self.video.cap.get(cv2.CAP_PROP_FPS)))
        data = 'Frame count:\t' + str(self.video.pos_fin) + '\n' 
        data = data + 'Frame width:\t' + str(self.video.width) + '\n'
        data = data + 'Frame height:\t' + str(self.video.height) + '\n'
        data = data + 'Frame rate:\t' + fps + '\n'

        self.ui.edt_data.setText(data)
        self.ui.edt_frame.setText(str(self.video.current))
        self.ui.edt_frame_stop.setText(str(int(self.video.pos_fin)))

        ret, frame = self.video.getCurrent()
        pix = mat2Qpix(frame)

        self.ui.lbl_image.setPixmap(pix)

#button play....................................................................
    def btnPlay(self):
        frms = int(self.ui.edt_frame.text())
        stop = int(self.ui.edt_frame_stop.text())
        self.video.setCurrent(frms)
        ret, frame = self.video.getCurrent()
        while(ret and self.video.current <= stop):
            pix = mat2Qpix(frame)
            self.ui.lbl_image.setPixmap(pix)
            self.ui.lbl_image.repaint()
            
            self.ui.edt_frame.setText(str(self.video.current))
            self.ui.repaint()

            ret, frame = self.video.getCurrent()
#record video...................................................................
    def saveVideo2File(self, dir_name, file_name, ini, fin, video, fps):

        tok = '_' + str(ini) + '_' + str(fin) 
        file = dir_name + "/" + file_name + tok + ".avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(  file, fourcc, fps, 
                                (int(video.width), int(video.height)))
                                
        self.video.setCurrent(ini)
        ret, frame = self.video.getCurrent()

        while(ret and self.video.current <= fin):
            pix = mat2Qpix(frame)
            out.write(frame)

            self.ui.lbl_image.setPixmap(pix)
            self.ui.lbl_image.repaint()
            
            self.ui.edt_frame.setText(str(self.video.current))
            self.ui.repaint()

            #so momentaneo
            #fileid = dir_name + "/" + file_name + tok + '_'+ str(self.video.current) + '.jpg'
            
            #cv2.imwrite( fileid, frame)

            ret, frame = self.video.getCurrent()
        out.release()
        print ('Writting in: ' + file)
        return file
#button record..................................................................
    def btnRecord(self):
        
        if(not self.video.cap.isOpened()):
            return

        fps = int(self.video.cap.get(cv2.CAP_PROP_FPS))

        dir_name = os.path.dirname( self.ui.edt_file.text() )
        file_name = os.path.basename( self.ui.edt_file.text() ).split('.')[0]
        
        ini = int(self.ui.edt_frame.text())
        fin = int(self.ui.edt_frame_stop.text())
        
        self.saveVideo2File(dir_name, file_name, ini, fin, self.video, fps)

#button record..................................................................
    def btnRecordStep(self):
        
        sstep = self.ui.edt_step.text()

        if(not self.video.cap.isOpened() or len(sstep) == 0):
            return

        step = int(sstep)
        fps = int(self.video.cap.get(cv2.CAP_PROP_FPS))

        dir_name = os.path.dirname( self.ui.edt_file.text() )
        file_name = os.path.basename( self.ui.edt_file.text() ).split('.')[0]
        
        ini = int(self.ui.edt_frame.text())
        fin = int(self.ui.edt_frame_stop.text())
        
        ant = ini
        for i in range(ini+step, fin+1, step):
            self.saveVideo2File(dir_name, file_name, ant, i, self.video, fps)
            ant = i


################################################################################
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv) 
    main = Main()
    sys.exit(app.exec_())
# coding=utf-8
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
import glob
import dicom
import sys  # Pegar infos do sistema
from natsort import natsorted
import os
import vtk
import numpy
from design import design  # Neste arquivo está a MainWindow que foi desenhada

dcmFiles = [] # lista onde guarda os arquivos da pasta selecionada
index = 0
ArrayDicom = []

class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Project N")
        self.setWindowIcon(QtGui.QIcon('design\\brain_icon2.png'))

        self.actionSelecionar_Pasta.triggered.connect(self.browse_folder)
        self.btnLeft.clicked.connect(self.toTheLetf)
        self.btnRight.clicked.connect(self.toRight)

        self.hSlider.valueChanged.connect(self.changeWithSlider)



        global ArrayDicom
        PathDicom = "./dicom_images/"
        lstFilesDCM = []  # create an empty list
        for dirName, subdirList, fileList in os.walk(PathDicom):
            for filename in fileList:
                if ".dcm" in filename.lower():  # check whether the file's DICOM
                    lstFilesDCM.append(os.path.join(dirName, filename))

        # Get ref file
        RefDs = dicom.read_file(lstFilesDCM[0])

        # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
        ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))

        # Load spacing values (in mm)
        ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))

        x = numpy.arange(0.0, (ConstPixelDims[0] + 1) * ConstPixelSpacing[0], ConstPixelSpacing[0])
        y = numpy.arange(0.0, (ConstPixelDims[1] + 1) * ConstPixelSpacing[1], ConstPixelSpacing[1])
        z = numpy.arange(0.0, (ConstPixelDims[2] + 1) * ConstPixelSpacing[2], ConstPixelSpacing[2])

        # The array is sized based on 'ConstPixelDims'
        ArrayDicom = numpy.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)

        # loop through all the DICOM files
        for filenameDCM in lstFilesDCM:
            # read the file
            ds = dicom.read_file(filenameDCM)
            # store the raw image data
            ArrayDicom[:, :, lstFilesDCM.index(filenameDCM)] = ds.pixel_array


    def dumpDicomImg(self, index):
        global ArrayDicom
        imv = self.graphicsView
        imv.setImage(ArrayDicom[:, :, index])
        imv.getView()

    def browse_folder(self):
        global dcmFiles
        dcmFiles = natsorted(glob.glob("dicom_images\*.dcm"))
        self.hSlider.setMaximum(len(dcmFiles) - 1)
        self.dumpDicomInfo(0)
        self.dumpDicomImg(0)
        #directory = QtGui.QFileDialog.getExistingDirectory(self, "Escolha uma pasta!")

        #path = unicode(directory.toUtf8(), encoding="UTF-8") + "/*.dcm"
        #dcmFiles = glob.glob(path)

    def toRight(self):
        global index
        if index + 1 != len(dcmFiles):
            index += 1
            self.hSlider.setValue(index)
            self.dumpDicomInfo(index)
            self.dumpDicomImg(index)

    def toTheLetf(self):
        global index
        if index > 0:
            index = index - 1
            self.hSlider.setValue(index)
            self.dumpDicomInfo(index)
            self.dumpDicomImg(index)

    def changeWithSlider(self):
        global index
        index = self.hSlider.value()
        self.dumpDicomInfo(index)
        self.dumpDicomImg(index)

    def dumpDicomInfo(self, index):
        self.listInfo.clear()

        file = dcmFiles[index]
        self.listInfo.addItem("file: %s" % file)
        data = dicom.read_file("%s" % file)

        keysWeWant = ['PatientName', 'PatientSex', 'PatientBirthDate', 'PerformedProcedureStepDescription', 'PerformedStationAETitle', 'InstitutionName', 'SliceLocation', 'SliceThickness', 'SpacingBetweenSlices']
        for key in data.dir():
            value = getattr(data, key, '')
            if type(value) is dicom.UID.UID or key == "PixelData":
                continue

            for k in keysWeWant:
                if key == k:
                    self.listInfo.addItem("%s : %s" % (key, value))


def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    app = QtGui.QApplication(sys.argv)  # uma nova instância do QApplication
    form = MainWindow()  # seta este formulários para o que esta no design
    form.show()  # mostra o form
    # form.iren.Initialize()
    app.exec_()  # e executa o app


if __name__ == '__main__':
    main()

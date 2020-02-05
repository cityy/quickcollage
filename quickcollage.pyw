#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Ferdinand List
Last edited: Feb 2020
"""

# todo
# make it possible to run the tool via windows context menu

import sys
from PyQt5.QtWidgets import ( QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QApplication, QListWidget, QFileDialog, QCheckBox, QLineEdit, QLabel )
from PyQt5 import QtCore
from PIL import Image
from math import ceil
from os import remove as removeFile


# for high dpi displays
QApplication.setAttribute( QtCore.Qt.AA_EnableHighDpiScaling, True )

class dropList( QListWidget ):
    def __init__( self, parent=None ):
        super().__init__( )
        self.setAcceptDrops( True )

    def dragEnterEvent( self, e ):
        if e.mimeData().hasImage:
            e.accept()
        else:
            e.ignore() 

    def dragMoveEvent( self, e ):
        if e.mimeData().hasImage:
            e.setDropAction( QtCore.Qt.CopyAction )
            e.accept()
        else:
            e.ignore() 

    def dropEvent(self, e):
        if e.mimeData().hasImage:
            e.setDropAction( QtCore.Qt.CopyAction )
            e.accept()
            for url in e.mimeData().urls():
                mn.addImagePath( str( url.toLocalFile() ) )


class main( QWidget ):

    def __init__( self ):
        super().__init__()
        self.initUI( )
        self.cols = 2
        self.colSizeX = 2500

    def fileDropped( self, drop):
        print( drop )
        
    def closeProgram( self ):
        app.quit()

    def getImages(self):
        fnames = QFileDialog.getOpenFileNames(self, 'Open file', '/home', "Image files (*.jpg *.gif)" )
        imagePaths = fnames[0]
        for path in imagePaths:
            self.addImagePath( path )
    def addImagePath( self, path ):
        row = self.fileList.currentRow()
        self.fileList.insertItem( row, path )
        self.browseButton.setText( "Clear" )
        self.browseButton.disconnect( )
        self.browseButton.clicked.connect( lambda: self.clearFileList() )

    def clearFileList( self ):
        self.fileList.clear()
        self.browseButton.disconnect( )
        self.browseButton.clicked.connect( lambda: self.getImages() )
        self.browseButton.setText( "Browse" )

    def makeCollage( self ):
        imageCount = self.fileList.count()

        if( imageCount > 1 ):
            imagePaths = []
            images = []

            spacing = 100 # spacing between collage images
            collageSize = ( int( self.sizeEdit.text() ) + ( spacing * ( int( self.colEdit.text() ) - 1 ) ), 10000 )
            collage = Image.new( 'RGB', collageSize, ( 255, 255, 255 ) )

            cols = int( self.colEdit.text() )
            rows = ceil( imageCount / cols )
            i =  0
            x =  0
            y =  0
            newW = int( int( self.sizeEdit.text() ) / cols )
            newH = 0
            rowH = 0

            for index in range( imageCount ):
                 imagePaths.append( self.fileList.item(index).text() )

            for imagePath in imagePaths:
                images.append( Image.open( imagePath ) )

            filename = imagePaths[0].split('/')[-1].split('.')[0] + "_collage"

            for row in range( rows ):
                for col in range( cols ):
                    if( len( images ) >= i+1 ):
                        currentW = images[i].size[0]
                        currentH = images[i].size[1]
                        factor = newW / currentW
                        newH = int( currentH * factor )
                        if newH > rowH:
                            rowH = newH
                        images[i] = images[i].resize( ( newW, newH ), Image.ANTIALIAS )
                        collage.paste( images[i], ( int( x ), int( y ) ) )
                    i += 1
                    x += newW + spacing
                y += (rowH + spacing)
                x = 0

            collage = collage.crop( ( 0, 0, collageSize[0], y - spacing ) ) # crop collage to match the total images height
            # collage preview if option is checked
            if( self.previewChecker.isChecked() ):
                collage.show()
            # saving
            success = self.saveCollage( collage, filename )
            # delete source images if option is checked
            if( self.deleteChecker.isChecked() and success ):
                for path in imagePaths: 
                    removeFile( path )


    def saveCollage( self, collage, filename ):
            newFilePath = QFileDialog.getSaveFileName(self, 'Save file', filename, "Image files (*.jpg )" )[0]
            # print( newFilePath )
            if( newFilePath ):
                collage.save( newFilePath + ".jpg" )
                self.clearFileList()
                return True
            else:
                return False

    def initUI( self ):

        # browse for images
        browseBox = QHBoxLayout( )
        self.browseButton = QPushButton( "Browse" )
        self.browseButton.clicked.connect( lambda: self.getImages() )
        browseBox.addWidget( self.browseButton )
        
        # file list
        fileListBox = QHBoxLayout( )
        self.fileList = dropList( )
        fileListBox.addWidget( self.fileList )

        # checkboxes
        checkersBox = QHBoxLayout()
        self.deleteChecker = QCheckBox( )
        self.deleteChecker.setText( "Delete Source Files" )
        self.previewChecker = QCheckBox( )
        self.previewChecker.setText( "Show Collage Preview" )
        self.previewChecker.setChecked( True )
        checkersBox.addWidget( self.deleteChecker )
        checkersBox.addWidget( self.previewChecker )

        # values
        valuesBox = QHBoxLayout()
        colLabel = QLabel()
        colLabel.setText("Columns: ")
        sizeLabel = QLabel()
        sizeLabel.setText("width (px): ")
        self.colEdit = QLineEdit( )
        self.colEdit.setText( "2" )
        self.sizeEdit = QLineEdit( )
        self.sizeEdit.setText( "2500" )

        valuesBox.addWidget( colLabel )
        valuesBox.addWidget( self.colEdit )
        valuesBox.addWidget( sizeLabel )
        valuesBox.addWidget( self.sizeEdit )

        # run or cancel
        runBox = QHBoxLayout( )
        self.runButton = QPushButton( "Run" )
        cancelButton = QPushButton( "Cancel" )
        self.runButton.clicked.connect( lambda: self.makeCollage() )
        cancelButton.clicked.connect( lambda: self.closeProgram() )
        runBox.addWidget( self.runButton )
        runBox.addWidget( cancelButton )

        # container
        container = QVBoxLayout( )
        container.addStretch( 1 )
        container.addLayout( browseBox )
        container.addLayout( fileListBox )
        container.addLayout( checkersBox )
        container.addLayout( valuesBox )
        container.addLayout( runBox )

        self.setLayout( container )

        self.move(300, 300)
        self.setWindowTitle( 'Collage Maker' )
        self.show( )
        
        
if __name__ == '__main__':
    
    app = QApplication( sys.argv )
    mn = main( )
    sys.exit( app.exec_() )
import os
import numpy as np
from skimage.io import imread
from skimage.color import label2rgb


from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt, QVariant, QDir
from PyQt5.QtGui import QImage

from dcp_client.utils import settings

class MyQFileSystemModel(QFileSystemModel):
    def __init__(self, app):
        """
        Initializes a custom QFileSystemModel
        """
        super().__init__()
        self.app = app
        self.img_x = 100
        self.img_y = 100

    def setFilter(self, filters):
        """
        Sets filters for the model.

        :param filters: The filters to be applied. (QDir.Filters)
        """
        filters |= QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files
        super().setFilter(filters)

        # Exclude files containing '_seg' in their names
        self.addFilter(lambda fileInfo: "_seg" not in fileInfo.fileName())

    def addFilter(self, filterFunc):
        """
        Adds a custom filter function to the model.

        :param filterFunc: The filter function to be added. (function)
        """
        self.filterFunc = filterFunc

    def headerData(self, section, orientation, role):
        """
        Reimplemented method to provide custom header data for the model's headers.

        :param section: The section (column) index. (int)
        :param orientation: The orientation of the header. (Qt.Orientation)
        :param role: The role of the header data. (int)
        :rtype: QVariant
        """
        if section == 0 and role == Qt.DisplayRole:
            return ""
        else:
            return super().headerData(section, orientation, role)


    def data(self, index, role=Qt.DisplayRole):
        """
        Reimplemented method to provide custom data for the model's items.

        :param index: The index of the item. (QModelIndex)
        :param role: The role of the data. (int)
        :rtype: QVariant
        """
        if not index.isValid():
            return QVariant()
        
        if role == Qt.DecorationRole:

            filepath_img = self.filePath(index)
            # if an image of our dataset
            if filepath_img.endswith(settings.accepted_types):
                
                # if a mask make sure it is displayed properly
                if "_seg" in filepath_img and os.path.exists(filepath_img):
                    img = imread(filepath_img)
                    if img.ndim > 2: img = img[0]
                    img = label2rgb(img)
                    img = (255 * img.copy()).astype(
                        np.uint8
                    )#np.transpose(img, (1, 0, 2))
                    height, width = img.shape[0], img.shape[1]
                    img = QImage(img, 
                                width, 
                                height, 
                                3 * width,
                                QImage.Format_RGB888
                    )
                    #img  = img.scaled(self.img_x, (width*self.img_x)//height, Qt.KeepAspectRatio)
                    img  = img.scaled(self.img_x, self.img_y, Qt.KeepAspectRatio) # yields the same
                else:
                    img = QImage(filepath_img).scaled(self.img_x, self.img_y, Qt.KeepAspectRatio)
                '''
                # It would be cool if instead of the mask and the image we could show them both merged 
                # together with label2rgb if the mask exists - would need to remove _seg files from list
                filepath_mask = '.'.join(filepath_img.split('.')[:-1])+'_seg.tiff'
                if os.path.exists(filepath_mask):
                    mask = imread(filepath_mask)
                    if mask.ndim>2: mask = mask[0]
                    img = imread(filepath_img, as_gray=True)
                    img = label2rgb(mask, img)
                    img = QImage(img,
                                img.shape[1], 
                                img.shape[0],
                                QImage.Format_RGB888
                                ).scaled(self.img_x, self.img_y, Qt.KeepAspectRatio)
                '''
                return img
            
        return super().data(index, role)


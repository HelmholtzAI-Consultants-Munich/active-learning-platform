from PyQt5.QtWidgets import  QFileIconProvider, QStyledItemDelegate
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QIcon

from dcp_client.utils import settings

class IconProvider(QFileIconProvider):
    def __init__(self) -> None:
        """Initializes the IconProvider with the default icon size."""
        super().__init__()
        self.ICON_SIZE = QSize(512, 512)

    def icon(self, type: QFileIconProvider.IconType) -> QIcon:
        """Returns the icon for the specified file type.

        :param type: The type of the file for which the icon is requested.
        :type type: QFileIconProvider.IconType
        :return: The icon for the file type.
        :rtype: QIcon
        """
        try:
            fn = type.filePath()
        except AttributeError:
            return super().icon(type)  # TODO handle exception differently?

        if fn.endswith(settings.accepted_types):
            a = QPixmap(self.ICON_SIZE)
            # a = a.scaled(QSize(1024, 1024))
            a.load(fn)
            return QIcon(a)
        else:
            return super().icon(type)


class CustomItemDelegate(QStyledItemDelegate):
    """
    A custom item delegate for setting a fixed height for items in a view.
    This delegate overrides the sizeHint method to set a fixed height for items.
    """
    def __init__(self, parent=None):
        """
        Initialize the CustomItemDelegate.

        :param parent: The parent QObject. Default is None.
        :type parent: QObject
        """
        super().__init__(parent)

    def sizeHint(self, option, index):
        """
        Returns the size hint for the item specified by the given index.

        :param option: The parameters used to draw the item.
        :type option: QStyleOptionViewItem
        
        :param index: The model index of the item.
        :type index: QModelIndex
        
        :returns: The size hint for the item.
        :rtype: QSize
        """
        size = super().sizeHint(option, index)
        size.setHeight(100)  
        return size

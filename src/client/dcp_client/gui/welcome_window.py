from __future__ import annotations
from typing import TYPE_CHECKING

from qtpy.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QLineEdit,
)
from qtpy.QtCore import Qt, QEvent


from dcp_client.gui.main_window import MainWindow
from dcp_client.gui._my_widget import MyWidget

if TYPE_CHECKING:
    from dcp_client.app import Application


class WelcomeWindow(MyWidget):
    """Welcome Window Widget object.
    The first window of the application providing a dialog that allows users to select directories.
    Currently supported image file types that can be selected for segmentation are: .jpg, .jpeg, .png, .tiff, .tif.
    By clicking 'start' the MainWindow is called.
    """

    def __init__(self, app: Application) -> None:
        """Initializes the WelcomeWindow.

        :param app: The Application instance.
        :type app: Application
        """
        super().__init__()
        self.app = app
        self.setWindowTitle("DCP")
        self.setStyleSheet("background-color: #f3f3f3;")
        self.resize(590, 250)

        self.main_layout = QVBoxLayout()
    
        title_label = QLabel("Welcome to the Helmholtz AI Data-Centric Tool!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #015998;"
        )
        self.main_layout.addWidget(title_label)

        instructions_label = QLabel("Please select your dataset folders:")
        instructions_label.setAlignment(Qt.AlignLeft)# AlignCenter)
        instructions_label.setStyleSheet(
            "font-size: 14px; color: #000000;"
        )
        self.main_layout.addWidget(instructions_label)


        input_layout = QHBoxLayout()
        
        self.text_layout = QVBoxLayout()
        self.path_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()

        val_label = QLabel(self)
        val_label.setText('Uncurated dataset:')


        inprogr_label = QLabel(self)
        inprogr_label.setText("In progress directory:")
        train_label = QLabel(self)
        train_label.setText('Curated dataset:')


        self.text_layout.addWidget(val_label)
        self.text_layout.addWidget(inprogr_label)
        self.text_layout.addWidget(train_label)

        self.val_textbox = QLineEdit(self)
        self.val_textbox.setPlaceholderText("Double-click to browse")
        # self.val_textbox.setToolTip("Double-click to browse")
       
        self.val_textbox.textEdited.connect(lambda x: self.on_text_changed(self.val_textbox, "eval", x))
        self.val_textbox.installEventFilter(self)

        self.inprogr_textbox = QLineEdit(self)
        self.inprogr_textbox.setPlaceholderText("Double-click to browse")
        # self.inprogr_textbox.setToolTip("Double-click to browse")
        self.inprogr_textbox.textEdited.connect(lambda x: self.on_text_changed(self.inprogr_textbox, "inprogress", x))
        self.inprogr_textbox.installEventFilter(self)

        self.train_textbox = QLineEdit(self)
        self.train_textbox.setPlaceholderText("Double-click to browse")
        # self.train_textbox.setToolTip("Double-click to browse")
        self.train_textbox.textEdited.connect(lambda x: self.on_text_changed(self.train_textbox, "train", x))
        self.train_textbox.installEventFilter(self)
        '''
        self.val_textbox.textEdited.connect(
            lambda x: self.on_text_changed(self.val_textbox, "eval", x)
        )

        self.inprogr_textbox = QLineEdit(self)
        self.inprogr_textbox.textEdited.connect(
            lambda x: self.on_text_changed(self.inprogr_textbox, "inprogress", x)
        )

        self.train_textbox = QLineEdit(self)
        self.train_textbox.textEdited.connect(
            lambda x: self.on_text_changed(self.train_textbox, "train", x)
        )
        '''

        self.path_layout.addWidget(self.val_textbox)
        self.path_layout.addWidget(self.inprogr_textbox)
        self.path_layout.addWidget(self.train_textbox)
        '''
        self.file_open_button_val = QPushButton("Browse", self)
        self.file_open_button_val.setFixedSize(80, 30)
        self.file_open_button_val.setStyleSheet(
            """QPushButton 
            { 
                  background-color: #3d81d1;
                  font-size: 11px; 
                  font-weight: bold;
                  color: #ffffff; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
            "QPushButton:hover { background-color: #006FBA; }"
        )
        self.file_open_button_val.show()
        self.file_open_button_val.clicked.connect(self.browse_eval_clicked)

        self.file_open_button_prog = QPushButton("Browse", self)
        self.file_open_button_prog.setFixedSize(80, 30)
        self.file_open_button_prog.setStyleSheet(
            """QPushButton 
            { 
                  background-color: #3d81d1;
                  font-size: 11px; 
                  font-weight: bold;
                  color: #ffffff; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
            "QPushButton:hover { background-color: #006FBA; }"
        )
        self.file_open_button_prog.show()
        self.file_open_button_prog.clicked.connect(self.browse_inprogr_clicked)


        self.file_open_button_train = QPushButton("Browse", self)
        self.file_open_button_train.setFixedSize(80, 30)
        self.file_open_button_train.setStyleSheet(
            """QPushButton 
            { 
                  background-color: #3d81d1;
                  font-size: 11px; 
                  font-weight: bold;
                  color: #ffffff; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
            "QPushButton:hover { background-color: #006FBA; }"
           
        )
        self.file_open_button_train.show()
        self.file_open_button_train.clicked.connect(self.browse_train_clicked)

        self.button_layout.addWidget(self.file_open_button_val)
        self.button_layout.addWidget(self.file_open_button_prog)
        self.button_layout.addWidget(self.file_open_button_train)
        '''
        input_layout.addLayout(self.text_layout)
        input_layout.addLayout(self.path_layout)
        input_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(input_layout)

        self.start_button = QPushButton("Start", self)
        self.start_button.setFixedSize(120, 30)
        self.start_button.setStyleSheet(
            """QPushButton 
            { 
                  background-color: #3d81d1;
                  font-size: 12px; 
                  font-weight: bold;
                  color: #ffffff; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
            "QPushButton:hover { background-color: #7bc432; }"
          
        )
        self.start_button.show()
        # check if we need to upload data to server
        self.done_upload = False  # we only do once
        if self.app.syncer.host_name == "local":
            self.start_button.clicked.connect(self.start_main)
        else:
            self.start_button.clicked.connect(self.start_upload_and_main)
        self.main_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.setLayout(self.main_layout)

        self.show()

    def browse_eval_clicked(self) -> None:
        """Activates  when the user clicks the button to choose the evaluation directory (QFileDialog) and
        displays the name of the evaluation directory chosen in the validation textbox line (QLineEdit).
        """
        self.fd = QFileDialog()
        try:
            self.fd.setFileMode(QFileDialog.Directory)
            if self.fd.exec_():
                self.app.eval_data_path = self.fd.selectedFiles()[0]
            self.val_textbox.setText(self.app.eval_data_path)
        finally:
            self.fd = None

    def browse_train_clicked(self) -> None:
        """Activates  when the user clicks the button to choose the train directory (QFileDialog) and
        displays the name of the train directory chosen in the train textbox line (QLineEdit).
        """

        fd = QFileDialog()
        fd.setFileMode(QFileDialog.Directory)
        if fd.exec_():
            self.app.train_data_path = fd.selectedFiles()[0]
        self.train_textbox.setText(self.app.train_data_path)

    def on_text_changed(self, field_obj: QLineEdit, field_name: str, text: str) -> None:
        """
        Update data paths based on text changes in input fields.
        Used for copying paths in the welcome window.

        :param field_obj: The QLineEdit object.
        :type field_obj: QLineEdit
        :param field_name: The name of the data field being updated.
        :type field_name: str
        :param text: The updated text.
        :type text: str
        """

        if field_name == "train":
            self.app.train_data_path = text
        elif field_name == "eval":
            self.app.eval_data_path = text
        elif field_name == "inprogress":
            self.app.inprogr_data_path = text
        field_obj.setText(text)
        
    def eventFilter(self, obj, event):
        ''' Event filter to capture double-click events on QLineEdit widgets '''
        if event.type() == QEvent.MouseButtonDblClick:
            if obj == self.val_textbox:
                self.browse_eval_clicked()
            elif obj == self.inprogr_textbox:
                self.browse_inprogr_clicked()
            elif obj == self.train_textbox:
                self.browse_train_clicked()
        return super().eventFilter(obj, event)
    

    def browse_inprogr_clicked(self):
        """ Activates  when the user clicks the button to choose the curation in progress directory (QFileDialog) and 
        displays the name of the evaluation directory chosen in the validation textbox line (QLineEdit).
        """

        fd = QFileDialog()
        fd.setFileMode(QFileDialog.Directory)
        if fd.exec_():  # Browse clicked
            self.app.inprogr_data_path = fd.selectedFiles()[
                0
            ]  # TODO: case when browse is clicked but nothing is specified - currently it is filled with os.getcwd()
        self.inprogr_textbox.setText(self.app.inprogr_data_path)

    def start_main(self) -> None:
        """Starts the main window after the user clicks 'Start' and only if both evaluation and train directories are chosen and all unique."""

        if (
            len(
                {
                    self.app.inprogr_data_path,
                    self.app.train_data_path,
                    self.app.eval_data_path,
                }
            )
            < 3
        ):
            self.message_text = "All directory names must be distinct."
            _ = self.create_warning_box(self.message_text, message_title="Warning")

        elif self.app.train_data_path and self.app.eval_data_path:
            self.hide()
            self.mw = MainWindow(self.app)
        else:
            self.message_text = "You need to specify a folder both for your uncurated and curated dataset (even if the curated folder is currently empty). Please go back and select folders for both."
            _ = self.create_warning_box(self.message_text, message_title="Warning")

    def start_upload_and_main(self) -> None:
        """
        If the configs are set to use remote not local server then the user is asked to confirm the upload of their data
        to the server and the upload starts before launching the main window.
        """
        if self.done_upload is False:
            message_text = (
                "Your current configurations are set to run some operations on the cloud. \n"
                "For this we need to upload your data to our server."
                "We will now upload your data. Click ok to continue. \n"
                "If you do not agree close the application and contact your software provider."
            )
            usr_response = self.create_warning_box(
                message_text, message_title="Warning", add_cancel_btn=True
            )
            if usr_response:
                success_up1, success_up2, _, _ = self.app.upload_data_to_server()
                if success_up1 == "Error" or success_up2 == "Error":
                    message_text = (
                        "An error has occured during data upload to the server. \n"
                        "Please check your configuration file and ensure that the server connection settings are correct and you have been given access to the server. \n"
                        "If the problem persists contact your software provider. Exiting now."
                    )
                    usr_response = self.create_warning_box(
                        message_text, message_title="Error"
                    )
                    self.close()
                else:
                    self.done_upload = True
                    self.start_upload_and_main()
        else:
            self.start_main()

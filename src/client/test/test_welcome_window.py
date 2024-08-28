import pytest
import sys

sys.path.append("../")

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from dcp_client.gui.welcome_window import WelcomeWindow
from dcp_client.app import Application
from dcp_client.utils.bentoml_model import BentomlModel
from dcp_client.utils.fsimagestorage import FilesystemImageStorage
from dcp_client.utils.sync_src_dst import DataRSync
from dcp_client.utils import settings


@pytest.fixture
def setup_global_variable():
    settings.accepted_types = (".jpg", ".jpeg", ".png", ".tiff", ".tif")
    yield settings.accepted_types


@pytest.fixture
def app(qtbot):
    rsyncer = DataRSync(user_name="local", host_name="local", server_repo_path=".")
    application = Application(
        BentomlModel(), rsyncer, FilesystemImageStorage(), "0.0.0.0", 7010
    )
    # Create an instance of WelcomeWindow
    # q_app = QApplication([])
    widget = WelcomeWindow(application)
    qtbot.addWidget(widget)
    yield widget
    widget.close()


@pytest.fixture
def app_remote(qtbot):
    rsyncer = DataRSync(user_name="remote", host_name="remote", server_repo_path=".")
    application = Application(
        BentomlModel(), rsyncer, FilesystemImageStorage(), "0.0.0.0", 7010
    )
    # Create an instance of WelcomeWindow
    # q_app = QApplication([])
    widget = WelcomeWindow(application)
    qtbot.addWidget(widget)
    yield widget
    widget.close()


def test_welcome_window_initialization(app):
    assert app.windowTitle() == "DCP"
    assert app.val_textbox.text() == ""
    assert app.inprogr_textbox.text() == ""
    assert app.train_textbox.text() == ""


def test_warning_for_same_paths(qtbot, app, monkeypatch):
    app.app.eval_data_path = "/same/path"
    app.app.train_data_path = "/same/path"
    app.app.inprogr_data_path = "/same/path"

    # Define a custom exec method that always returns QMessageBox.Ok
    def custom_exec(self):
        return QMessageBox.Ok

    monkeypatch.setattr(QMessageBox, "exec", custom_exec)
    qtbot.mouseClick(app.start_button, Qt.LeftButton)

    assert app.create_warning_box
    assert app.message_text == "All directory names must be distinct."


def test_on_text_changed(qtbot, app):
    app.app.train_data_path = "/initial/train/path"
    app.app.eval_data_path = "/initial/eval/path"
    app.app.inprogr_data_path = "/initial/inprogress/path"

    app.on_text_changed(
        field_obj=app.train_textbox, field_name="train", text="/new/train/path"
    )
    assert app.app.train_data_path == "/new/train/path"

    app.on_text_changed(
        field_obj=app.val_textbox, field_name="eval", text="/new/eval/path"
    )
    assert app.app.eval_data_path == "/new/eval/path"

    app.on_text_changed(
        field_obj=app.inprogr_textbox,
        field_name="inprogress",
        text="/new/inprogress/path",
    )
    assert app.app.inprogr_data_path == "/new/inprogress/path"


def test_start_main_not_selected(qtbot, app):
    app.app.train_data_path = None
    app.app.eval_data_path = None
    app.sim = True
    qtbot.mouseClick(app.start_button, Qt.LeftButton)
    assert not hasattr(app, "mw")


def test_start_main(qtbot, app, setup_global_variable):
    settings.accepted_types = setup_global_variable

    # app.app.cur_selected_path = app.app.eval_data_path
    # app.app.cur_selected_img = 'cat.png'

    # Set some paths for testing
    app.app.eval_data_path = "/path/to/eval"
    app.app.train_data_path = "/path/to/train"
    # Simulate clicking the start button
    qtbot.mouseClick(app.start_button, Qt.LeftButton)
    # Check if the main window is created
    # assert qtbot.waitUntil(lambda: hasattr(app, 'mw'), timeout=1000)
    assert hasattr(app, "mw")
    # Check if the WelcomeWindow is hidden
    assert app.isHidden()


def test_start_upload_and_main(qtbot, app_remote, setup_global_variable, monkeypatch):
    settings.accepted_types = setup_global_variable
    app_remote.app.eval_data_path = "/path/to/eval"
    app_remote.app.train_data_path = "/path/to/train"

    # Define a custom exec method that always returns QMessageBox.Ok
    def custom_exec(self):
        return QMessageBox.Ok

    monkeypatch.setattr(QMessageBox, "exec", custom_exec)
    qtbot.mouseClick(app_remote.start_button, Qt.LeftButton)
    # should close because error on upload!
    assert app_remote.done_upload == False
    assert not app_remote.isVisible()
    assert not hasattr(app_remote, "mw")


"""'
# TODO wait for github respose
def test_browse_eval_clicked(qtbot, app, monkeypatch):
    # Mock the QFileDialog so that it immediately returns a directory
    def handle_dialog(*args, **kwargs):
        #if app.fd.isVisible(): 
        QCoreApplication.processEvents()
        app.app.eval_data_path = '/path/to/selected/directory'

    #def mock_file_dialog(*args, **kwargs):
    #       return ['/path/to/selected/directory']
    
    #monkeypatch.setattr(QFileDialog, 'getExistingDirectory', mock_file_dialog)
    QTimer.singleShot(100, handle_dialog)

    #monkeypatch.setattr(app, 'browse_eval_clicked', mock_file_dialog)
    #monkeypatch.setattr(QFileDialog, 'getExistingDirectory', mock_file_dialog)
    # Simulate clicking the browse button for evaluation directory
    qtbot.mouseClick(app.file_open_button_val, Qt.LeftButton, delay=1)
    # Check if the textbox is updated with the selected path
    assert app.val_textbox.text() == '/path/to/selected/directory'

def test_browse_eval_clicked(qtbot, app):
    # Simulate clicking the browse button for evaluation directory
    qtbot.mouseClick(app.file_open_button_val, Qt.LeftButton)
    # Check if the QFileDialog is shown
    assert qtbot.waitUntil(lambda: hasattr(app, 'app.eval_data_path'), timeout=1000)
    # Check if the textbox is updated with the selected path
    assert app.val_textbox.text() == app.app.eval_data_path


def test_browse_train_clicked(qtbot, app):
    # Simulate clicking the browse button for train directory
    qtbot.mouseClick(app.file_open_button_train, Qt.LeftButton)
    # Check if the QFileDialog is shown
    assert qtbot.waitUntil(lambda: hasattr(app, 'app.train_data_path'), timeout=1000)
    # Check if the textbox is updated with the selected path
    assert app.train_textbox.text() == app.app.train_data_path

def test_browse_inprogr_clicked(qtbot, app):
    # Simulate clicking the browse button for in-progress directory
    qtbot.mouseClick(app.file_open_button_prog, Qt.LeftButton)
    # Check if the QFileDialog is shown
    assert qtbot.waitUntil(lambda: hasattr(app, 'app.inprogr_data_path'), timeout=1000)
    # Check if the textbox is updated with the selected path
    assert app.inprogr_textbox.text() == app.app.inprogr_data_path

"""

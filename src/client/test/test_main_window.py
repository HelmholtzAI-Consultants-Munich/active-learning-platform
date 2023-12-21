import os
import pytest
import sys
sys.path.append('../')

from skimage import data
from skimage.io import imsave

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from dcp_client.gui.main_window import MainWindow
from dcp_client.app import Application
from dcp_client.utils.bentoml_model import BentomlModel
from dcp_client.utils.fsimagestorage import FilesystemImageStorage
from dcp_client.utils.sync_src_dst import DataRSync
from dcp_client.utils import settings

@pytest.fixture()
def setup_global_variable():
    settings.accepted_types = (".jpg", ".jpeg", ".png", ".tiff", ".tif")
    yield settings.accepted_types

@pytest.fixture
def app(qtbot, setup_global_variable):

    settings.accepted_types = setup_global_variable

    img1 = data.astronaut()
    img2 = data.coffee()
    img3 = data.cat()

    if not os.path.exists('train_data_path'): 
        os.mkdir('train_data_path')
        imsave('train_data_path/astronaut.png', img1)

    if not os.path.exists('in_prog'): 
        os.mkdir('in_prog')
        imsave('in_prog/coffee.png', img2)
    
    if not os.path.exists('eval_data_path'): 
        os.mkdir('eval_data_path')
        imsave('eval_data_path/cat.png', img3)

    rsyncer = DataRSync(user_name="local", host_name="local", server_repo_path='.')
    application = Application(BentomlModel(),
                              rsyncer,
                              FilesystemImageStorage(),
                              "0.0.0.0",
                              7010,
                              'eval_data_path',
                              'train_data_path',
                              'in_prog')
    # Create an instance of MainWindow
    widget = MainWindow(application)
    qtbot.addWidget(widget)
    yield widget
    widget.close()
    
def test_main_window_setup(qtbot, app, setup_global_variable):
    settings.accepted_types = setup_global_variable
    assert app.title == "Data Overview"

def test_item_train_selected(qtbot, app, setup_global_variable):
    settings.accepted_types = setup_global_variable
    # Select the first item in the tree view
    #index = app.list_view_train.model().index(0, 0)
    index = app.list_view_train.indexAt(app.list_view_train.viewport().rect().topLeft())
    pos = app.list_view_train.visualRect(index).center()
    # Simulate file click
    QTest.mouseClick(app.list_view_train.viewport(), 
                     Qt.LeftButton, 
                     pos=pos)

    app.on_item_train_selected(index)
    # Assert that the selected item matches the expected item
    assert app.list_view_train.selectionModel().currentIndex() == index
    assert app.app.cur_selected_img=='astronaut.png'
    assert app.app.cur_selected_path==app.app.train_data_path
    os.remove('train_data_path/astronaut.png')
    os.rmdir('train_data_path')

def test_item_inprog_selected(qtbot, app, setup_global_variable):
    settings.accepted_types = setup_global_variable
    # Select the first item in the tree view
    index = app.list_view_inprogr.indexAt(app.list_view_inprogr.viewport().rect().topLeft())
    pos = app.list_view_inprogr.visualRect(index).center()
    # Simulate file click
    QTest.mouseClick(app.list_view_inprogr.viewport(), 
                     Qt.LeftButton, 
                     pos=pos)
    app.on_item_inprogr_selected(index)
    # Assert that the selected item matches the expected item
    assert app.list_view_inprogr.selectionModel().currentIndex() == index
    assert app.app.cur_selected_img == "coffee.png"
    assert app.app.cur_selected_path == app.app.inprogr_data_path
    os.remove('in_prog/coffee.png')
    os.rmdir('in_prog')

def test_item_eval_selected(qtbot, app, setup_global_variable):
    settings.accepted_types = setup_global_variable
    # Select the first item in the tree view
    index = app.list_view_eval.indexAt(app.list_view_eval.viewport().rect().topLeft())
    pos = app.list_view_eval.visualRect(index).center()
    # Simulate file click
    QTest.mouseClick(app.list_view_eval.viewport(), 
                     Qt.LeftButton, 
                     pos=pos)
    app.on_item_eval_selected(index)
    # Assert that the selected item matches the expected item
    assert app.list_view_eval.selectionModel().currentIndex() == index
    assert app.app.cur_selected_img=='cat.png'
    assert app.app.cur_selected_path==app.app.eval_data_path
    os.remove('eval_data_path/cat.png')
    os.rmdir('eval_data_path')
    

def test_train_button_click(qtbot, app):
    # Click the "Train Model" button
    QTest.mouseClick(app.train_button, Qt.LeftButton)
    # Assert that the worker thread is properly configured
    assert app.worker_thread.task == 'train'
    assert not app.train_button.isEnabled()
    # Wait for the worker thread to finish
    QTest.qWaitForWindowActive(app)
    # The train functionality of the thread is tested with app tests

def test_inference_button_click(qtbot, app):
    # Click the "Generate Labels" button
    QTest.mouseClick(app.inference_button, Qt.LeftButton)
    # Assert that the worker thread is properly configured
    assert app.worker_thread.task == 'inference'
    assert not app.inference_button.isEnabled()
    # Wwait for the worker thread to finish
    QTest.qWaitForWindowActive(app)
    # The inference functionality of the thread is tested with app tests

def test_on_finished(qtbot, app):
    assert app.train_button.isEnabled()
    assert app.inference_button.isEnabled()
    assert not app.worker_thread.isRunning()

def test_launch_napari_button_click_without_selection(qtbot, app):
    # Try clicking the view button without having selected an image
    app.sim = True
    qtbot.mouseClick(app.launch_nap_button, Qt.LeftButton)
    assert not hasattr(app, 'nap_win')

def test_launch_napari_button_click(qtbot, app):
    settings.accepted_types = setup_global_variable
    # Simulate selection of an image to view before clivking on view button
    index = app.list_view_eval.indexAt(app.list_view_eval.viewport().rect().topLeft())
    pos = app.list_view_eval.visualRect(index).center()
    # Simulate file click
    QTest.mouseClick(app.list_view_eval.viewport(), 
                     Qt.LeftButton, 
                     pos=pos)
    app.on_item_eval_selected(index)
    # Now click the view button
    qtbot.mouseClick(app.launch_nap_button, Qt.LeftButton)
    # Assert that the napari window has launched
    assert hasattr(app, 'nap_win')
    assert app.nap_win.isVisible()

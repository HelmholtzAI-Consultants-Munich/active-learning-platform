from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from copy import deepcopy

from qtpy.QtWidgets import QPushButton, QComboBox, QLabel, QGridLayout
from qtpy.QtCore import Qt
from qtpy.QtGui import QGuiApplication
import napari
import numpy as np

if TYPE_CHECKING:
    from dcp_client.app import Application
from dcp_client.utils.utils import get_path_stem, check_equal_arrays
from dcp_client.utils.compute4mask import Compute4Mask
from dcp_client.gui._my_widget import MyWidget


class NapariWindow(MyWidget):
    """Napari Window Widget object.
    Opens the napari image viewer to view and fix the labeles.
    :param app: The Application instance.
    :type app: Application
    """

    def __init__(self, app: Application) -> None:
        """Initializes the NapariWindow.

        :param app: The Application instance.
        :type app: Application
        """
        super().__init__()
        self.app = app
        self.setWindowTitle("napari viewer")
        self.setStyleSheet("background-color: #262930;")
        screen_size = QGuiApplication.primaryScreen().geometry()
        self.resize(int(screen_size.width()*0.8), int(screen_size.height()*0.8))

        # Load image and get corresponding segmentation filenames
        img = self.app.load_image()
        self.app.search_segs()
        self.seg_files = self.app.seg_filepaths.copy()

        # Set the viewer
        self.viewer = napari.Viewer(show=False)
        self.viewer.window.add_plugin_dock_widget("napari-sam")

        self.viewer.add_image(img, name=get_path_stem(self.app.cur_selected_img))
        for seg_file in self.seg_files:
            self.viewer.add_labels(
                self.app.load_image(seg_file), name=get_path_stem(seg_file)
            )

        main_window = self.viewer.window._qt_window
        layout = QGridLayout()
        layout.addWidget(main_window, 0, 0, 1, 4)

        # select the first seg as the currently selected layer if there are any segs
        if (
            len(self.seg_files)
            and len(self.viewer.layers[get_path_stem(self.seg_files[0])].data.shape) > 2
        ):
            self.cur_selected_seg = self.viewer.layers.selection.active.name
            self.layer = self.viewer.layers[self.cur_selected_seg]
            self.viewer.layers.selection.events.changed.connect(
                self.on_seg_channel_changed
            )
            # set first mask as active by default
            self.active_mask_index = 0
            self.viewer.dims.events.current_step.connect(self.axis_changed)
            self.original_instance_mask = {}
            self.original_class_mask = {}
            self.instances = {}
            self.contours_mask = {}
            for seg_file in self.seg_files:
                layer_name = get_path_stem(seg_file)
                # get unique instance labels for each seg
                self.original_instance_mask[layer_name] = deepcopy(
                    self.viewer.layers[layer_name].data[0]
                )
                self.original_class_mask[layer_name] = deepcopy(
                    self.viewer.layers[layer_name].data[1]
                )
                # compute unique instance ids
                self.instances[layer_name] = Compute4Mask.get_unique_objects(
                    self.original_instance_mask[layer_name]
                )
                # remove border from class mask
                self.contours_mask[layer_name] = Compute4Mask.get_contours(
                    self.original_instance_mask[layer_name], contours_level=0.8
                )
                self.viewer.layers[layer_name].data[1][
                    self.contours_mask[layer_name] != 0
                ] = 0

            self.qctrl = self.viewer.window.qt_viewer.controls.widgets[self.layer]

            if len(self.layer.data.shape) > 2:
                # User hint
                message_label = QLabel('Choose an active mask')
                message_label.setStyleSheet(
                """
                    font-size: 12px;
                    font-weight: bold; 
                    background-color: #262930;
                    color: #D1D2D4;
                    border-radius: 5px; 
                    padding: 8px 16px;"""
                )

                message_label.setAlignment(Qt.AlignRight)
                layout.addWidget(message_label, 1, 0)

                # Drop list to choose which is an active mask
                self.mask_choice_dropdown = QComboBox()
                self.mask_choice_dropdown.setEnabled(False)
                self.mask_choice_dropdown.addItem(
                    "Instance Segmentation Mask", userData=0
                )
                self.mask_choice_dropdown.addItem("Labels Mask", userData=1)
                layout.addWidget(self.mask_choice_dropdown, 1, 1)

                # when user has chosen the mask, we don't want to change it anymore to avoid errors
                lock_button = QPushButton("Confirm Final Choice")
                lock_button.setStyleSheet(
                """QPushButton 
                        { 
                            background-color: #5A626C;
                            font-size: 12px; 
                            font-weight: bold;
                            color: #D1D2D4; 
                            border-radius: 5px;
                            padding: 8px 16px; }"""
                "QPushButton:hover { background-color: #6A7380; }"
                "QPushButton:pressed { background-color: #6A7380; }" 
                    )

                lock_button.setEnabled(True)
                lock_button.clicked.connect(self.set_editable_mask)

                layout.addWidget(lock_button, 1, 2)
        else:
            self.layer = None

        # add buttons for moving images to other dirs
        add_to_inprogress_button = QPushButton('Move to \'Curatation in progress\' folder')
        add_to_inprogress_button.setStyleSheet(
        """QPushButton 
            { 
                  background-color: #0064A8;
                  font-size: 12px; 
                  font-weight: bold;
                  color: #D1D2D4; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
        "QPushButton:hover { background-color: #006FBA; }"
        "QPushButton:pressed { background-color: #006FBA; }" 
               
         
        )
        layout.addWidget(add_to_inprogress_button, 2, 0, 1, 2)
        add_to_inprogress_button.clicked.connect(
            self.on_add_to_inprogress_button_clicked
        )

        add_to_curated_button = QPushButton('Move to \'Curated dataset\' folder')
        add_to_curated_button.setStyleSheet(
        """QPushButton 
            { 
                  background-color: #0064A8;
                  font-size: 12px; 
                  font-weight: bold;
                  color: #D1D2D4; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
        "QPushButton:hover { background-color: #006FBA; }"
        "QPushButton:pressed { background-color: #006FBA; }" 
         
        )

        layout.addWidget(add_to_curated_button, 2, 2, 1, 2)
        add_to_curated_button.clicked.connect(self.on_add_to_curated_button_clicked)

        self.setLayout(layout)

        remove_from_dataset_button = QPushButton('Remove from dataset')
        remove_from_dataset_button.setStyleSheet(
        """QPushButton 
            { 
                  background-color: #0064A8;
                  font-size: 12px; 
                  font-weight: bold;
                  color: #D1D2D4; 
                  border-radius: 5px;
                  padding: 8px 16px; }"""
        "QPushButton:hover { background-color: #006FBA; }"
        "QPushButton:pressed { background-color: #006FBA; }" 
         
        )
        layout.addWidget(remove_from_dataset_button, 3, 0, 1, 4)
        remove_from_dataset_button.clicked.connect(self.on_remove_from_dataset_button_clicked)

    def on_remove_from_dataset_button_clicked(self) -> None:
        """
        Defines what happens when the "Remove from dataset" button is clicked.
        """
        '''
        try:
            # get image name
            files_to_remove = [self.viewer.layers.selection.active.name]
        except AttributeError:
            message_text = "Please first select the image in the layer list."
            _ = self.create_warning_box(message_text, message_title="Warning")
            return
        '''
        rmv_files = [self.app.cur_selected_img]
        self.app.search_segs()
        rmv_files.extend(self.app.seg_filepaths)
        # Delete the image and corresponding masks from the dataset
        self.app.delete_images(rmv_files)
        self.app.cur_selected_img = ""
        self.app.seg_filepaths = []
        self.viewer.close()
        self.close()

    def set_editable_mask(self) -> None:
        """
        This function is not implemented. In theory the use can choose between which mask to edit.
        Currently painting and erasing is only possible on instance mask and in the class mask only
        the class labels can be changed.
        """
        pass

    def on_seg_channel_changed(self, event) -> None:
        """
        Is triggered each time the user selects a different layer in the viewer.
        """
        if (act := self.viewer.layers.selection.active) is not None:
            # updater cur_selected_seg with the new selection from the user
            self.cur_selected_seg = act.name
            if type(self.viewer.layers[self.cur_selected_seg]) == napari.layers.Image:
                pass
            # set self.layer to new selection from user
            elif self.layer is not None:
                self.layer = self.viewer.layers[self.cur_selected_seg]
        else:
            pass

    def axis_changed(self, event) -> None:
        """
        Is triggered each time the user switches the viewer between the mask channels. At this point the class mask
        needs to be updated according to the changes made tot the instance segmentation mask.
        """

        if self.app.cur_selected_img=="": return # because this also gets triggered when removing outlier

        self.active_mask_index = self.viewer.dims.current_step[0]
        masks = deepcopy(self.layer.data)

        # if user has switched to the instance mask
        if self.active_mask_index == 0:
            class_mask_with_contours = Compute4Mask.add_contour(masks[1], masks[0])
            if not check_equal_arrays(
                class_mask_with_contours.astype(bool),
                self.original_class_mask[self.cur_selected_seg].astype(bool),
            ):
                self.update_instance_mask(masks[0], masks[1])
            self.switch_to_instance_mask()

        # else if user has switched to the class mask
        elif self.active_mask_index == 1:
            if not check_equal_arrays(
                masks[0], self.original_instance_mask[self.cur_selected_seg]
            ):
                self.update_labels_mask(masks[0])
            self.switch_to_labels_mask()

    def switch_to_instance_mask(self) -> None:
        """
        Switch the application to the active mask mode by enabling 'paint_button', 'erase_button'
        and 'fill_button'.
        """
        
        self.original_class_mask[self.cur_selected_seg] = deepcopy(self.layer.data[1])
        self.switch_controls("paint_button", True)
        self.switch_controls("erase_button", True)
        self.switch_controls("fill_button", True)

    def switch_to_labels_mask(self) -> None:
        """
        Switch the application to non-active mask mode by enabling 'fill_button' and disabling 'paint_button' and 'erase_button'.
        """

        self.original_instance_mask[self.cur_selected_seg] = deepcopy(self.layer.data[0])
        if self.cur_selected_seg in [layer.name for layer in self.viewer.layers]:
            self.viewer.layers[self.cur_selected_seg].mode = "pan_zoom"
        info_message_paint = (
            "Painting objects is only possible in the instance layer for now."
        )
        info_message_erase = (
            "Erasing objects is only possible in the instance layer for now."
        )
        self.switch_controls("paint_button", False, info_message_paint)
        self.switch_controls("erase_button", False, info_message_erase)
        self.switch_controls("fill_button", True)

    def update_labels_mask(self, instance_mask: np.ndarray) -> None:
        """Updates the class mask based on changes in the instance mask.

        If the instance mask has changed since the last switch between channels, the class mask needs to be updated accordingly.

        :param instance_mask: The updated instance mask, changed by the user.
        :type instance_mask: numpy.ndarray
        :return: None
        """
        self.original_class_mask[self.cur_selected_seg] = (
            Compute4Mask.compute_new_labels_mask(
                self.original_class_mask[self.cur_selected_seg],
                instance_mask,
                self.original_instance_mask[self.cur_selected_seg],
                self.instances[self.cur_selected_seg],
            )
        )
        # update original instance mask and instances
        self.original_instance_mask[self.cur_selected_seg] = instance_mask
        self.instances[self.cur_selected_seg] = Compute4Mask.get_unique_objects(
            self.original_instance_mask[self.cur_selected_seg]
        )
        # compute contours to remove from class mask visualisation
        self.contours_mask[self.cur_selected_seg] = Compute4Mask.get_contours(
            instance_mask, contours_level=0.8
        )
        vis_labels_mask = deepcopy(self.original_class_mask[self.cur_selected_seg])
        vis_labels_mask[self.contours_mask[self.cur_selected_seg] != 0] = 0
        # update the viewer
        self.layer.data[1] = vis_labels_mask
        self.layer.refresh()

    def update_instance_mask(
        self, instance_mask: np.ndarray, labels_mask: np.ndarray
    ) -> None:
        """Updates the instance mask based on changes in the labels mask.

        If the labels mask has changed, but only if an object has been removed, the instance mask is updated accordingly.

        :param instance_mask: The existing instance mask, which needs to be updated.
        :type instance_mask: numpy.ndarray
        :param labels_mask: The updated labels mask, changed by the user.
        :type labels_mask: numpy.ndarray
        """
        # add contours back to labels mask
        labels_mask = Compute4Mask.add_contour(labels_mask, instance_mask)
        # and compute the updated instance mask
        self.original_instance_mask[self.cur_selected_seg] = (
            Compute4Mask.compute_new_instance_mask(labels_mask, instance_mask)
        )
        self.instances[self.cur_selected_seg] = Compute4Mask.get_unique_objects(
            self.original_instance_mask[self.cur_selected_seg]
        )
        self.original_class_mask[self.cur_selected_seg] = labels_mask
        # update the viewer
        self.layer.data[0] = self.original_instance_mask[self.cur_selected_seg]
        self.layer.refresh()

    def switch_controls(
        self, target_widget: str, status: bool, info_message: Optional[str] = None
    ) -> None:
        """Enables or disables a specific widget.

        :param target_widget: The name of the widget to be controlled within the QCtrl object.
        :type target_widget: str
        :param status: If True, the widget will be enabled; if False, it will be disabled.
        :type status: bool
        :param info_message: Optionally add an info message when hovering over some widget. Default is None.
        :type info_message: str or None
        """
        try:
            getattr(self.qctrl, target_widget).setEnabled(status)
            if info_message is not None:
                getattr(self.qctrl, target_widget).setToolTip(info_message)
        except:
            pass

    def on_add_to_curated_button_clicked(self) -> None:
        """Defines what happens when the "Move to curated dataset folder" button is clicked."""
        if self.app.cur_selected_path == str(self.app.train_data_path):
            message_text = "Image is already in the 'Curated data' folder and should not be changed again"
            _ = self.create_warning_box(message_text, message_title="Warning")
            return

        # take the name of the currently selected layer (by the user)
        seg_name_to_save = self.viewer.layers.selection.active.name
        # TODO if more than one item is selected this will break!
        if "_seg" not in seg_name_to_save:
            message_text = (
                "Please select the segmenation you wish to save from the layer list."
                "The labels layer should have the same name as the image to which it corresponds, followed by _seg."
            )
            _ = self.create_warning_box(message_text, message_title="Warning")
            return

        # Save the (changed) seg
        seg = self.viewer.layers[seg_name_to_save].data
        seg[1] = Compute4Mask.add_contour(seg[1], seg[0])
        annot_error, mask_mismatch_error, faulty_ids_annot, faulty_ids_missmatch = (
            Compute4Mask.assert_consistent_labels(seg)
        )
        if annot_error:
            message_text = (
                "There seems to be a problem with your mask. We expect each object to be a connected component. For object(s) with ID(s) \n"
                + str(faulty_ids_annot)
                + "\n"
                "more than one connected component was found. Please go back and fix this."
            )
            self.create_warning_box(message_text, "Warning")
        elif mask_mismatch_error:
            message_text = (
                "There seems to be a mismatch between your class and instance masks for object(s) with ID(s) \n"
                + str(faulty_ids_missmatch)
                + "\n"
                "This should not occur and will cause a problem later during model training. Please go back and check."
            )
            self.create_warning_box(message_text, "Warning")
        else:
            # Move original image
            self.app.move_images(self.app.train_data_path)

            self.app.save_image(
                self.app.train_data_path, seg_name_to_save + ".tiff", seg
            )

            # We remove seg from the current directory if it exists (both eval and inprogr allowed)
            self.app.delete_images(self.seg_files)
            # TODO Create the Archive folder for the rest? Or move them as well?

            self.viewer.close()
            self.close()

    def on_add_to_inprogress_button_clicked(self) -> None:
        """Defines what happens when the "Move to curation in progress folder" button is clicked."""
        # TODO: Do we allow this? What if they moved it by mistake? User can always manually move from their folders?)
        if self.app.cur_selected_path == str(self.app.train_data_path):
            message_text = "Images from '\Curated data'\ folder can not be moved back to 'Curatation in progress' folder."
            _ = self.create_warning_box(message_text, message_title="Warning")
            return

        # take the name of the currently selected layer (by the user)
        seg_name_to_save = self.viewer.layers.selection.active.name
        # TODO if more than one item is selected this will break!
        if "_seg" not in seg_name_to_save:
            message_text = (
                "Please select the segmenation you wish to save from the layer list."
                "The labels layer should have the same name as the image to which it corresponds, followed by _seg."
            )
            _ = self.create_warning_box(message_text, message_title="Warning")
            return

        # Move original image
        self.app.move_images(self.app.inprogr_data_path, move_segs=True)
        # Save the (changed) seg - this will overwrite existing seg if seg name hasn't been changed in viewer
        seg = self.viewer.layers[seg_name_to_save].data
        seg[1] = Compute4Mask.add_contour(seg[1], seg[0])
        self.app.save_image(self.app.inprogr_data_path, seg_name_to_save + ".tiff", seg)

        self.viewer.close()
        self.close()

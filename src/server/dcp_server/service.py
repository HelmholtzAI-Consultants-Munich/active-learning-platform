from __future__ import annotations
import os
import typing as t
import bentoml

from dcp_server.serviceclasses import CustomBentoService, CustomRunnable
from dcp_server.utils.fsimagestorage import FilesystemImageStorage
from dcp_server.utils.helpers import read_config


models_module = __import__("models")
segmentation_module = __import__("segmentationclasses")

# Import configuration
script_path = os.path.abspath(__file__)
config_path = os.path.join(os.path.dirname(script_path), "config.yaml")
service_config = read_config("service", config_path=config_path)
model_config = read_config("model", config_path=config_path)
data_config = read_config("data", config_path)
train_config = read_config("train", config_path)
eval_config = read_config("eval", config_path)
setup_config = read_config("setup", config_path)

# instantiate the model

model_class = getattr(models_module, setup_config["model_to_use"])
model = model_class(
    model_name=setup_config["model_to_use"],
    model_config=model_config,
    data_config=data_config,
    train_config=train_config,
    eval_config=eval_config,
)
custom_model_runner = t.cast(
    "CustomRunner",
    bentoml.Runner(
        CustomRunnable,
        name=service_config["runner_name"],
        runnable_init_params={
            "model": model,
            "save_model_path": service_config["bento_model_path"],
        },
    ),
)
# instantiate the segmentation type
segm_class = getattr(segmentation_module, setup_config["segmentation"])
fsimagestorage = FilesystemImageStorage(data_config, setup_config["model_to_use"])
segmentation = segm_class(
    imagestorage=fsimagestorage, runner=custom_model_runner, model=model
)


# Call the service
service = CustomBentoService(
    runner=segmentation.runner,
    segmentation=segmentation,
    service_name=service_config["service_name"],
)
svc = service.start_service()

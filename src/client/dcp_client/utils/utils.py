from pathlib import Path, PurePath
import yaml
import numpy as np

def read_config(name: str, config_path: str = "config.yaml") -> dict:
    """Reads the configuration file

    :param name: name of the section you want to read (e.g. 'setup','train')
    :type name: string
    :param config_path: path to the configuration file, defaults to 'config.yaml'
    :type config_path: str, optional
    :return: dictionary from the config section given by name
    :rtype: dict
    """
    with open(config_path) as config_file:
        config_dict = yaml.safe_load(
            config_file
        )  # json.load(config_file) for .cfg file
        # Check if config file has main mandatory keys
        assert all([i in config_dict.keys() for i in ["server"]])
        return config_dict[name]


def get_relative_path(filepath: str) -> str:
    """Returns the name of the file from the given filepath.

    :param filepath: The path of the file.
    :type filepath: str
    :return: The name of the file.
    :rtype: str
    """
    return PurePath(filepath).name


def get_path_stem(filepath: str) -> str:
    """Returns the stem (filename without its extension) from the given filepath.

    :param filepath: The path of the file.
    :type filepath: str
    :return: The stem of the file.
    :rtype: str
    """
    return str(Path(filepath).stem)

def get_path_name(filepath: str) -> str:
    """Returns the name of the file from the given filepath.

    :param filepath: The path of the file.
    :type filepath: str
    :return: The name of the file.
    :rtype: str
    """
    return str(Path(filepath).name)


def get_path_parent(filepath: str) -> str:
    """Returns the parent directory of the given filepath.

    :param filepath: The path of the file.
    :type filepath: str
    :return: The parent directory of the file.
    :rtype: str
    """
    return str(Path(filepath).parent)


def join_path(root_dir: str, filepath: str) -> str:
    """Joins the root directory path with the given filepath.

    :param root_dir: The root directory.
    :type root_dir: str
    :param filepath: The path of the file.
    :type filepath: str
    :return: The joined path.
    :rtype: str
    """
    return str(Path(root_dir, filepath))


def check_equal_arrays(array1: np.ndarray, array2: np.ndarray) -> bool:
    """Checks if two arrays are equal.

    :param array1: The first array.
    :type array1: numpy.ndarray
    :param array2: The second array.
    :type array2: numpy.ndarray
    :return: True if the arrays are equal, False otherwise.
    :rtype: bool
    """
    return np.array_equal(array1, array2)

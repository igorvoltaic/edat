""" Set of helper function to generate plots based on dataset data """
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from helpers.exceptions import FileAccessError
from helpers.file_tools import get_dir_path


def render_plot(csv_file: str, x_axis: str, y_axis: str) -> str:
    """ Take filepath and axis selections and return plot img filepath """
    try:
        data = pd.read_csv(csv_file)
    except (FileExistsError, OSError) as e:
        raise FileAccessError("Cannot read dataset file") from e
    sns.relplot(
       x=x_axis,
       y=y_axis,
       data=data,
       kind="box"
    )
    dataset_dir = get_dir_path(csv_file)
    image_name = "plot_x_{}_y_{}.png".format(x_axis, y_axis)
    image_path = os.path.join(dataset_dir, image_name)
    try:
        plt.savefig(image_path, bbox_inches='tight')
    except (FileExistsError, OSError) as e:
        raise FileAccessError("Cannot read dataset file") from e
    return image_path

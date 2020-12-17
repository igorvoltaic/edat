""" Set of helper function to generate plots based on dataset data """
import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Optional

from apps.datasets.dtos import CsvDialectDTO

from helpers.exceptions import FileAccessError
from helpers.file_tools import get_dir_path


matplotlib.use('Agg')


def render_plot(
        csv_file: str,
        x_axis: str,
        y_axis: str,
        dialect: Optional[CsvDialectDTO] = None) -> str:
    """ Take filepath and axis selections and return plot img filepath """
    dataset_dir = get_dir_path(csv_file)
    image_name = "plot_x_{}_y_{}.png".format(x_axis, y_axis)
    image_path = os.path.join(dataset_dir, image_name)
    if os.path.isfile(image_path):
        return image_path
    try:
        if dialect:
            data = pd.read_csv(
                csv_file,
                delimiter=dialect.delimiter,
                quotechar=dialect.quotechar,
                skiprows=dialect.start_row,
                # header=dialect.has_header
            )
        else:
            data = pd.read_csv(csv_file)
    except (FileExistsError, OSError) as e:
        raise FileAccessError("Cannot read dataset file") from e
    sns.catplot(
       x=x_axis,
       y=y_axis,
       data=data,
       kind="box"
    )
    dpi = 300
    try:
        plt.savefig(image_path, bbox_inches='tight', figsize=(1200/dpi, 1200/dpi), dpi=dpi)
    except (FileExistsError, OSError) as e:
        raise FileAccessError("Cannot read dataset file") from e
    return image_path

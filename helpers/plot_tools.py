""" Set of helper function to generate plots based on dataset data """
import os
import hashlib
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from django.conf import settings

from apps.datasets.dtos import CsvDialectDTO, PlotDTO

from helpers.exceptions import FileAccessError
from helpers.file_tools import get_dir_path


matplotlib.use('Agg')

DPI = settings.PLOT_IMG_DPI


def plotter_class(kind):
    return {
        "box": sns.catplot,
        "violin": sns.catplot,
        "boxen": sns.catplot,
        "bar": sns.catplot,
        "point": sns.catplot,
        "strip": sns.catplot,
        "swarm": sns.catplot,
        "count": sns.catplot,
        "scatter": sns.relplot,
        "line": sns.relplot,
        "hist": sns.displot,
        "kde": sns.displot,
        "ecdf": sns.displot,
    }[kind]


def get_plot_hash(dto: PlotDTO) -> str:
    """ return DTO's md5 hash """
    hash_object = hashlib.md5(str(dto).encode())
    return hash_object.hexdigest()


def pixel(px_size: int) -> int:
    """ Take size in pixels and return size value accepted by matplotlib """
    size = px_size/DPI
    return size


def render_plot(
        plot_hash: str,
        csv_file: str,
        plot_dto: PlotDTO,
        dialect: Optional[CsvDialectDTO] = None) -> str:
    """ Take filepath and axis selections and return plot img filepath """
    dataset_dir = get_dir_path(csv_file)
    image_name = "{}.png".format(plot_hash)
    image_path = os.path.join(dataset_dir, image_name)
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
    sns_class = plotter_class(plot_dto.plot_type.value)
    plot = sns_class(
       data=data,
       kind=plot_dto.plot_type.value,
       **plot_dto.params.dict()
    )
    plot.fig.set_figwidth(pixel(plot_dto.width))
    plot.fig.set_figheight(pixel(plot_dto.height))
    plot.fig.dpi = DPI
    try:
        plt.savefig(
            image_path,
            bbox_inches='tight',
        )
    except (FileExistsError, OSError) as e:
        raise FileAccessError("Cannot read dataset file") from e
    return image_path

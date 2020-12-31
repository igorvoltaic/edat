""" Set of helper function to generate plots based on dataset data """
import os
import hashlib
import logging
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from django.conf import settings

from apps.datasets.dtos import CsvDialectDTO, PlotDTO

from helpers.exceptions import FileAccessError, PlotRenderError
from helpers.file_tools import get_plot_img_name


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
        csv_file: str,
        plot_dto: PlotDTO,
        dialect: Optional[CsvDialectDTO] = None) -> str:
    """ Take filepath and axis selections and return plot img filepath """
    image_path = get_plot_img_name(csv_file)
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
    except (FileExistsError, OSError) as err:
        raise FileAccessError("Cannot read dataset file") from err
    sns_class = plotter_class(plot_dto.plot_type.value)
    try:
        plot = sns_class(
           data=data,
           kind=plot_dto.plot_type.value,
           **plot_dto.params.dict()
        )
    except (ValueError, TypeError, NotImplementedError) as err:
        raise PlotRenderError(str(err)) from err
    plot.fig.set_figwidth(pixel(plot_dto.width))
    plot.fig.set_figheight(pixel(plot_dto.height))
    plot.fig.dpi = DPI
    try:
        plt.savefig(
            image_path,
            bbox_inches='tight',
        )
    except (FileExistsError, OSError) as err:
        raise FileAccessError("Cannot save plot image file") from err
    logging.info("Image '%s' was created", image_path)
    return image_path

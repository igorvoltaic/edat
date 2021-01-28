""" Set of helper function to generate plots based on dataset data """
from typing import Dict

from celery import shared_task

from apps.datasets.dtos import CsvDialectDTO, PlotDTO
from apps.datasets.models import Plot

from helpers.exceptions import FileAccessError, PlotRenderError
from helpers.plot_tools import render_plot


@shared_task(expires=60*5)
def render_plot_task(plot_dict: Dict) -> str:
    """ Take task parameters and pass them to render_plot helper
        In case there was not plot created, delete the plot object
        Taks expiration time is set in seconds.
    """
    plot_dto = PlotDTO(**plot_dict)
    plot = Plot.objects.get(pk=plot_dto.id)  # type: ignore
    csv_file = plot.dataset.file.name
    dialect = CsvDialectDTO.from_orm(plot.dataset.csv_dialect)
    try:
        image_path = render_plot(
                csv_file,
                plot_dto,
                dialect
        )
        plot.file = image_path
        plot.save()
    except (FileNotFoundError, FileExistsError, OSError) as err:
        plot.delete()
        raise FileAccessError(
            "Cannot read dataset file or save the plot image"
        ) from err
    except (ValueError, TypeError, NotImplementedError) as err:
        plot.delete()
        raise PlotRenderError(str(err)) from err
    return image_path

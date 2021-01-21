""" Set of helper function to generate plots based on dataset data """
from typing import Optional, Dict

from celery import shared_task

from apps.datasets.dtos import CsvDialectDTO, PlotDTO
from apps.datasets.models import Plot

from helpers.exceptions import FileAccessError, PlotRenderError
from helpers.plot_tools import render_plot


@shared_task
def render_plot_task(
        csv_file: str,
        plot_id: int,
        plot_dict: Dict,
        dialect_dict: Optional[Dict] = None) -> str:
    """ Take task parameters and pass them to render_plot helper """
    plot_dto = PlotDTO(**plot_dict)
    dialect = CsvDialectDTO(**dialect_dict)
    try:
        image_path = render_plot(
                csv_file,
                plot_id,
                plot_dto,
                dialect
        )
    except (FileNotFoundError, FileExistsError, OSError) as err:
        Plot.objects.get(pk=plot_id).delete()  # type: ignore
        raise FileAccessError(
            "Cannot read dataset file or save the plot image"
        ) from err
    except (ValueError, TypeError, NotImplementedError) as err:
        Plot.objects.get(pk=plot_id).delete()  # type: ignore
        raise PlotRenderError(str(err)) from err
    return image_path

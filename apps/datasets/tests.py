import string
from django.test import TestCase

from .models.datasets import Dataset, Column, Plot, CsvDialect
from .dtos.datasets import Delimiter, Quotechar, ColumnType, PlotType


class PostTestCase(TestCase):

    def setUp(self):

        datasets = {}
        for i in range(10):
            datasets[i] = Dataset.objects.create(  # type: ignore
                    name='testfile{}.csv'.format(i),
                    height=256,
                    width=26,
                    comment='test comment'
                    )

            for c, index in zip(string.ascii_uppercase, [i for i in range(26)]):
                Column.objects.create(  # type: ignore
                        dataset=datasets[i],
                        index=index,
                        name=c,
                        datatype=ColumnType('string'),
                        )

            CsvDialect.objects.create(  # type: ignore
                    dataset=datasets[i],
                    delimiter=Delimiter(";"),
                    quotechar=Quotechar('"'),
                    has_header=True,
                    start_row=None
                    )

            Plot.objects.create(  # type: ignore
                    dataset=datasets[i],
                    height=600,
                    width=600,
                    plot_type=PlotType('scatter'),
                    params='{"testname":"testvalue"}',
                    checksum="xxx",
                    file='/filepath/img.png'
                    )

    def test_dataset_count(self):
        datasets = Dataset.objects.all()  # type: ignore
        self.assertEqual(datasets.count(), 10)

    def test_column_count(self):
        columns = Column.objects.all()  # type: ignore
        self.assertEqual(columns.count(), 260)

    def test_dataset_column_count(self):
        dataset = Dataset.objects.get(pk=5)  # type: ignore
        self.assertEqual(dataset.columns.count(), 26)

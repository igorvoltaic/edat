class DatasetDTO:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.timestamp = kwargs['timestamp']
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.comment = kwargs.get('comment')

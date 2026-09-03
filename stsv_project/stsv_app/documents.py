from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Event

@registry.register_document
class EventDocument(Document):
    category_name = fields.TextField(attr='category.name')
    
    class Index:
        # Name of the Elasticsearch index
        name = 'events'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Event

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'title',
            'description',
            'location',
            'status',
        ]

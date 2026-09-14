from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Event
from .models.system import NotificationTemplate
from .models.users import OrgProfile

@registry.register_document
class EventDocument(Document):
    category_name = fields.TextField(attr='category.name')
    
    class Index:
        name = 'events'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Event

        fields = [
            'id',
            'title',
            'description',
            'location',
            'status',
        ]


@registry.register_document
class NotificationDocument(Document):
    class Index:
        name = 'notifications'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = NotificationTemplate

        fields = [
            'id',
            'title',
            'message',
            'type',
        ]


@registry.register_document
class OrgProfileDocument(Document):
    class Index:
        name = 'org_profiles'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = OrgProfile

        fields = [
            'id',
            'org_name',
            'description',
            'org_type',
        ]

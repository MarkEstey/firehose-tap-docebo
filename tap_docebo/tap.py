from singer_sdk import Tap

from singer_sdk.typing import (
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_docebo.streams import (
    LearnCatalog,
    LearnCategories,
    LearnCourses,
    LearnEnrollments,
    LearnLearningPlans,
    ManageUsers,
)

class TapDocebo(Tap):
    name = 'tap-docebo'

    config_jsonschema = PropertiesList(
        Property(
            'url_base',
            StringType,
            default='https://docebosaas.com',
            description='The base url for the Docebo',
        ),
        Property(
            'oauth_client_id',
            StringType,
            description='Client ID used for OAuth authentication',
        ),
        Property(
            'oauth_client_secret',
            StringType,
            secret=True,
            description='Client secret used for OAuth authentication',
        ),
        Property(
            'oauth_username',
            StringType,
            description='Username used for OAuth authentication',
        ),
        Property(
            'oauth_password',
            StringType,
            secret=True,
            description='Password used for OAuth authentication',
        ),
        Property(
            'bearer_token',
            StringType,
            secret=True,
            description='Bearer token used for manual authentication',
        ),
        Property(
            'page_size',
            IntegerType,
            default=100,
            description='The number of results to request per page. Must be in the range 1-200.',
        ),
        Property(
            'stream_type_conformance',
            StringType,
            default='none',
            description='The level of type conformance to apply to streams '
            '(see: https://sdk.meltano.com/en/latest/classes/singer_sdk.Stream.html#singer_sdk.Stream.TYPE_CONFORMANCE_LEVEL). '
            'Defaults to none. Must be one of: none, root_only, recursive',
            allowed_values=['none', 'root_only', 'recursive'],
        ),
        Property(
            'stream_maps',
            ObjectType(),
            description='Inline stream maps (see: https://sdk.meltano.com/en/latest/stream_maps.html)',
        ),
        Property(
            'stream_maps_config',
            ObjectType(),
            description='Inline stream maps config (see: https://sdk.meltano.com/en/latest/stream_maps.html)',
        ),
    ).to_dict()

    def discover_streams(self):
        return [
            LearnCatalog(self),
            LearnCategories(self),
            LearnCourses(self),
            LearnEnrollments(self),
            LearnLearningPlans(self),
            ManageUsers(self),
        ]

if __name__ == '__main__':
    TapDocebo.cli()

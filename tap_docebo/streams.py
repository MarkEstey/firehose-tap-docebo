from functools import cached_property
from singer_sdk.authenticators import BearerTokenAuthenticator, OAuthAuthenticator
from singer_sdk.helpers._typing import TypeConformanceLevel
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

from singer_sdk.typing import (
    DateTimeType,
    IntegerType,
    PropertiesList,
    Property,
    StringType,
)

class DoceboAuthenticator(OAuthAuthenticator):
    @property
    def oauth_request_body(self):
        return {
            'client_id': self.config['oauth_client_id'],
            'client_secret': self.config['oauth_client_secret'],
            'grant_type': 'password',
            'scope': 'api',
            'username': self.config['oauth_username'],
            'password': self.config['oauth_password'],
        }

class DoceboPaginator(BaseAPIPaginator):
    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)

    def get_next(self, response):
        response_json = response.json()

        if not bool(response_json['data']['has_more_data']):
            return None

        token = {}
        token['page'] = int(response_json['data']['current_page']) + 1

        if 'cursor' in response_json['data'] and response_json['data']['cursor']:
            token['cursor'] = str(response_json['data']['cursor'])

        return token

class DoceboStream(RESTStream):
    additional_params = {}
    records_jsonpath = '$.data.items[*]'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.TYPE_CONFORMANCE_LEVEL = {
            'none': TypeConformanceLevel.NONE,
            'root_only': TypeConformanceLevel.ROOT_ONLY,
            'recursive': TypeConformanceLevel.RECURSIVE,
        }.get(self.config['stream_type_conformance'])

    @property
    def url_base(self):
        return self.config['url_base']

    @cached_property
    def authenticator(self):
        if 'bearer_token' in self.config:
            return BearerTokenAuthenticator(self, self.config['bearer_token'])
        else:
            return DoceboAuthenticator(self, f"{self.config['url_base']}/oauth2/token")

    def get_new_paginator(self):
        return DoceboPaginator()

    def get_url_params(self, context, next_page_token):
        params = {}
        params['page_size'] = self.config['page_size']

        if self.additional_params:
            params |= self.additional_params

        if next_page_token:
            params['page'] = next_page_token['page']

            if 'cursor' in next_page_token:
                params['cursor'] = next_page_token['cursor']

        if self.replication_key and self.get_starting_timestamp(context):
            params['updated_from'] = self.get_starting_timestamp(context).replace(tzinfo=None).isoformat(' ', timespec='seconds')

        return params

class LearnCatalog(DoceboStream):
    name = 'learn_catalog'
    path = '/learn/v1/catalog'
    additional_params = {'show_item_list': '1'}
    primary_keys = ['catalogue_id']
    schema = PropertiesList(
        Property('catalogue_id', IntegerType, required=True),
    ).to_dict()

class LearnCategories(DoceboStream):
    name = 'learn_categories'
    path = '/learn/v1/categories'
    primary_keys = ['id']
    schema = PropertiesList(
        Property('id', IntegerType, required=True),
    ).to_dict()

class LearnCourses(DoceboStream):
    name = 'learn_courses'
    path = '/learn/v1/courses'
    additional_params = {'sort_by': 'last_update', 'sort_by_direction': 'asc'}
    primary_keys = ['id_course']
    replication_key = 'date_last_updated'
    schema = PropertiesList(
        Property('id_course', IntegerType, required=True),
        Property('date_last_updated', DateTimeType, required=True),
    ).to_dict()

class LearnEnrollments(DoceboStream):
    name = 'learn_enrollments'
    path = '/learn/v1/enrollments'
    primary_keys = ['id', 'user_id']
    replication_key = 'date_last_updated'
    schema = PropertiesList(
        Property('id', IntegerType, required=True),
        Property('user_id', IntegerType, required=True),
        Property('date_last_updated', DateTimeType, required=True),
    ).to_dict()

class LearnLearningPlans(DoceboStream):
    name = 'learn_learning_plans'
    path = '/learn/v1/lp'
    additional_params = {'sort_attr': 'last_update', 'sort_dir': 'asc'}
    primary_keys = ['id']
    replication_key = 'date_last_updated'
    schema = PropertiesList(
        Property('id', StringType, required=True),
        Property('date_last_updated', DateTimeType, required=True),
    ).to_dict()

class ManageUsers(DoceboStream):
    name = 'manage_users'
    path = '/manage/v1/user'
    primary_keys = ['user_id']
    replication_key = 'last_update'
    schema = PropertiesList(
        Property('user_id', StringType, required=True),
        Property('last_update', DateTimeType, required=True),
    ).to_dict()

from os import environ
from authlib.integrations.starlette_client import OAuth

#oauth = None
# if 'OIDC_SERVER' in environ and len(environ['OIDC_SERVER']) > 0:
#     oauth = OAuth()
#     oauth.register(
#         name='oidc',
#         client_id=environ['OIDC_CLIENT_ID'],
#         client_secret=environ['OIDC_CLIENT_SECRET'],
#         server_metadata_url=environ['OIDC_SERVER'] + '/.well-known/openid-configuration',
#         client_kwargs={
#             'scope': 'openid profile email'
#         }
#     )

oauth = OAuth()
oauth.register(
        name='oidc',
        client_id='nl_clariah_oidc-test',
        client_secret='d3860f36-5d8e-11f0-9a20-3b86b64afb06',
        server_metadata_url='https://authentication.clariah.nl/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid profile email'
        }
    )
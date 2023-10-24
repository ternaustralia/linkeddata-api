FLASK_APP=linkeddata_api
FLASK_ENV=development

LINKEDDATA_API_SETTINGS=development.cfg

# TODO: move this into development.cfg?
#       it's secrets ... would be much better to fake it away somehow
LINKEDDATA_API_OIDC_DISCOVERY_URL='https://auth-test.tern.org.au/auth/realms/local/.well-known/openid-configuration'
LINKEDDATA_API_OIDC_CLIENT_ID=dst
LINKEDDATA_API_OIDC_CLIENT_SECRET=
LINKEDDATA_API_OIDC_USE_REFRESH_TOKEN=True

LINKEDDATA_API_ELASTICSEARCH_URL=https://es-test.tern.org.au
LINKEDDATA_API_ELASTICSEARCH_VERIFY_CERTS=
LINKEDDATA_API_ELASTICSEARCH_SSL_SHOW_WARN=
import upstox_client
from upstox_client.rest import ApiException

api_key = 'cf060510-4bc6-4c4a-abc4-06cdd9960fdc'
api_secret = '8f2z05bdck'
redirect_url = 'https://www.google.com/'
state = 'sunil'
output_link = 'https://www.google.com/?code=_nIcv_&state=sunil'
auth_code = output_link[output_link.index('code=')+5:output_link.index('&state')]
print(auth_code)

api_instance = upstox_client.LoginApi()
api_version = '2.0'
code = auth_code
client_id = api_key
client_secret = api_secret
redirect_uri = redirect_url
grant_type = 'authorization_code'

try:
    # Get token API
    api_response = api_instance.token(api_version, code=code, client_id=client_id, client_secret=client_secret,
                                      redirect_uri=redirect_uri, grant_type=grant_type)
    print(api_response)
    print(api_response.access_token)
except ApiException as e:
    print("Exception when calling LoginApi->token: %s\n" % e)
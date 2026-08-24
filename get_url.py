# SDK - 
# 
import upstox_client
from upstox_client.rest import ApiException


api_key = 'cf060510-4bc6-4c4a-abc4-06cdd9960fdc'
api_secret = '8f2z05bdck'
redirect_url = 'https://www.google.com/'
state = 'sunil'


sample_url = f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={api_key}&redirect_uri={redirect_url}&state={state}'
print(sample_url)
exit()


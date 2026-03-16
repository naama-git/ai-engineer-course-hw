# netfree_patch.py
import os
import ssl
import certifi
import aiohttp
import httpx
import urllib3
from dotenv import load_dotenv
from urllib3 import PoolManager

load_dotenv()

# 1. הגדרת משתני סביבה
os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] 
os.environ['REQUESTS_CA_BUNDLE'] 
os.environ['SSL_CERT_FILE']
os.environ['CURL_CA_BUNDLE']

# 2. הגדרת SSL Context לשימוש כללי
netfree_ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = ssl._create_unverified_context

# 3. Patch ל-httpx
original_client_init = httpx.Client.__init__
original_async_client_init = httpx.AsyncClient.__init__

def patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_client_init(self, *args, **kwargs)

def patched_async_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_async_client_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_client_init
httpx.AsyncClient.__init__ = patched_async_client_init

# 4. Patch ל-aiohttp
original_connector_init = aiohttp.TCPConnector.__init__

def patched_connector_init(self, *args, **kwargs):
    kwargs['ssl'] = netfree_ssl_context
    original_connector_init(self, *args, **kwargs)

aiohttp.TCPConnector.__init__ = patched_connector_init

# 5. Patch ל-urllib3
urllib3.disable_warnings()
original_pool_manager_init = PoolManager.__init__

def patched_pool_manager_init(self, *args, **kwargs):
    kwargs['cert_reqs'] = 'CERT_NONE'
    original_pool_manager_init(self, *args, **kwargs)

PoolManager.__init__ = patched_pool_manager_init

print("NetFree Patches applied successfully.")
import os
from dotenv import load_dotenv 
from cognite.client.credentials import OAuthClientCredentials, Token
from cognite.client import CogniteClient, ClientConfig

def init_cognite_connect():
    """
    This function will initialize the connection to Cognite Data Fusion (CDF) using the credentials stored in the .env file.
    Parameters: 
        None
    Returns:
        creds: OAuthClientCredentials
        config: ClientConfig
        client: CogniteClient
    """
    load_dotenv()
    TOKEN_URL = os.getenv("TOKEN_URL")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    CDF_CLUSTER = os.getenv("CDF_CLUSTER")
    BASE_URL = f"https://{CDF_CLUSTER}.cognitedata.com"
    SCOPES = [f"{BASE_URL}/.default"]
    COGNITE_PROJECT=os.getenv("COGNITE_PROJECT")
    creds = OAuthClientCredentials(token_url = TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
    config = ClientConfig(client_name="",project=COGNITE_PROJECT,credentials=creds,base_url=BASE_URL)
    client=CogniteClient(config)
    return creds, config, client

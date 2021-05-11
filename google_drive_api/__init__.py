import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging


logger = logging.getLogger("google_drive_api")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.FileHandler('./logs/app_logs/app.log')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


path = "./configuration/input.json"


with open(path, 'r') as f:
    config_input = json.load(f)

SCOPES = config_input["SCOPES"]
SERVICE_ACCOUNT_FILE = config_input["SERVICE_ACCOUNT_FILE"]
api_folder_path = config_input["api_folder_path"]
data_folder = config_input["data_folder"]
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

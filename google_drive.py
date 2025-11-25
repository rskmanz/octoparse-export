"""
Google Drive Integration
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Optional
from datetime import datetime

from auth import get_credentials

TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'


class GoogleDriveClient:
    """Google Drive client for uploading files"""

    def __init__(self):
        credentials = get_credentials()
        self.service = build('drive', 'v3', credentials=credentials)

    def find_folder_by_name(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(q=query, fields="files(id, name)", pageSize=1).execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None

    def create_folder(self, folder_name: str, parent_id: str = None) -> str:
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]

        folder = self.service.files().create(body=metadata, fields='id').execute()
        return folder['id']

    def find_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        folder_id = self.find_folder_by_name(folder_name, parent_id)
        return folder_id if folder_id else self.create_folder(folder_name, parent_id)

    def upload_file(self, local_path: str, filename: str, folder_id: str) -> dict:
        metadata = {'name': filename, 'parents': [folder_id]}
        media = MediaFileUpload(local_path, mimetype='text/csv', resumable=True)
        file = self.service.files().create(body=metadata, media_body=media, fields='id, webViewLink').execute()
        return {
            'id': file['id'],
            'url': file.get('webViewLink', f"https://drive.google.com/file/d/{file['id']}/view")
        }

    def upload_task_data(self, local_path: str, task_name: str, root_folder_id: str = None) -> dict:
        task_folder_id = self.find_or_create_folder(task_name, root_folder_id)
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        timestamp_folder_id = self.create_folder(timestamp, task_folder_id)
        result = self.upload_file(local_path, 'data.csv', timestamp_folder_id)
        return {
            'task_folder_id': task_folder_id,
            'timestamp_folder_id': timestamp_folder_id,
            'file_id': result['id'],
            'url': result['url']
        }

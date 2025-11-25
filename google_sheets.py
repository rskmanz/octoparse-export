"""
Google Sheets Integration
"""

import gspread
from typing import List, Dict
from datetime import datetime

from auth import get_credentials

TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'

# Header mappings (Japanese)
HEADERS = {
    'task_id': 'タスクID',
    'task_name': 'タスク名',
    'file_location': 'ファイル場所',
    'record_count': 'レコード数',
    'status': 'ステータス',
    'timestamp': '更新日時'
}


class GoogleSheetsClient:
    """Google Sheets client for reading and updating spreadsheet"""

    def __init__(self):
        credentials = get_credentials()
        self.client = gspread.authorize(credentials)

    def open_spreadsheet(self, url: str):
        return self.client.open_by_url(url)

    def create_spreadsheet(self, title: str, folder_id: str = None):
        spreadsheet = self.client.create(title, folder_id=folder_id)
        # Add Japanese headers
        worksheet = spreadsheet.sheet1
        worksheet.update(values=[[HEADERS['task_id'], HEADERS['task_name']]], range_name='A1:B1')
        return spreadsheet

    def get_tasks(self, spreadsheet_url: str, sheet_name: str = None) -> List[Dict]:
        spreadsheet = self.open_spreadsheet(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
        records = worksheet.get_all_records()

        tasks = []
        for i, record in enumerate(records, start=2):
            # Support both English and Japanese headers
            task_id = record.get('task_id', '') or record.get(HEADERS['task_id'], '')
            task_name = record.get('task_name', '') or record.get(HEADERS['task_name'], '')

            task = {
                'task_id': task_id,
                'task_name': task_name,
                'row_number': i,
                'raw_data': record
            }
            if task['task_id']:
                tasks.append(task)

        return tasks

    def update_result(self, spreadsheet_url: str, row_number: int,
                      file_location: str, record_count: int,
                      status: str, sheet_name: str = None):
        spreadsheet = self.open_spreadsheet(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
        headers = worksheet.row_values(1)

        # Use Japanese headers for output columns
        output_columns = [
            HEADERS['file_location'],
            HEADERS['record_count'],
            HEADERS['status'],
            HEADERS['timestamp']
        ]

        for col_name in output_columns:
            if col_name not in headers:
                next_col = len(headers) + 1
                worksheet.update_cell(1, next_col, col_name)
                headers.append(col_name)

        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)

        worksheet.update_cell(row_number, headers.index(HEADERS['file_location']) + 1, file_location)
        worksheet.update_cell(row_number, headers.index(HEADERS['record_count']) + 1, record_count)
        worksheet.update_cell(row_number, headers.index(HEADERS['status']) + 1, status)
        worksheet.update_cell(row_number, headers.index(HEADERS['timestamp']) + 1, timestamp)

    def update_status(self, spreadsheet_url: str, row_number: int,
                      status: str, sheet_name: str = None):
        spreadsheet = self.open_spreadsheet(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
        headers = worksheet.row_values(1)

        status_header = HEADERS['status']
        if status_header not in headers:
            next_col = len(headers) + 1
            worksheet.update_cell(1, next_col, status_header)
            headers.append(status_header)

        worksheet.update_cell(row_number, headers.index(status_header) + 1, status)

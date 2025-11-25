"""
Octoparse Export App - Main Entry Point

Fetches Octoparse data and exports to Google Drive with tracking.

Usage:
    python main.py <spreadsheet_url> [folder_id]
"""

import os
import sys
import tempfile
from datetime import datetime

from octoparse_client import OctoparseClient
from google_sheets import GoogleSheetsClient
from google_drive import GoogleDriveClient

TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'


def process_task(task: dict, octoparse: OctoparseClient,
                 drive: GoogleDriveClient, sheets: GoogleSheetsClient,
                 spreadsheet_url: str, root_folder_id: str = None) -> dict:
    """Process a single task: fetch data, upload to Drive, update spreadsheet"""
    task_id = task['task_id']
    task_name = task['task_name']
    row_number = task['row_number']

    # Fetch task name from Octoparse if not provided
    if not task_name:
        print(f"\n[FETCHING] Getting task name for ID: {task_id}")
        task_name = octoparse.get_task_name(task_id)
        if task_name:
            print(f"  [OK] Task name: {task_name}")
            # Update spreadsheet with task name
            spreadsheet = sheets.client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.sheet1
            worksheet.update_cell(row_number, 2, task_name)
        else:
            task_name = task_id[:20]  # Use truncated ID as fallback

    print(f"\n[PROCESSING] Task: {task_name} (ID: {task_id})")

    result = {
        'task_id': task_id,
        'task_name': task_name,
        'status': 'Failed',
        'record_count': 0,
        'file_url': ''
    }

    try:
        sheets.update_status(spreadsheet_url, row_number, 'In Progress')

        print(f"  [1/3] Fetching data from Octoparse...")
        df = octoparse.get_task_data(task_id)

        if df.empty:
            print(f"  [WARNING] No data found for task")
            result['status'] = 'No Data'
            sheets.update_result(spreadsheet_url, row_number, '', 0, 'No Data')
            return result

        record_count = len(df)
        print(f"  [OK] Retrieved {record_count} records")

        print(f"  [2/3] Exporting to CSV...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
            temp_path = f.name
            df.to_csv(f, index=False)

        print(f"  [3/3] Uploading to Google Drive...")
        upload_result = drive.upload_task_data(temp_path, task_name, root_folder_id)
        os.unlink(temp_path)

        file_url = upload_result['url']
        print(f"  [OK] Uploaded: {file_url}")

        sheets.update_result(spreadsheet_url, row_number, file_url, record_count, 'Success')

        result['status'] = 'Success'
        result['record_count'] = record_count
        result['file_url'] = file_url
        print(f"  [DONE] Task completed successfully")

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        result['status'] = 'Failed'
        result['error'] = str(e)
        try:
            sheets.update_result(spreadsheet_url, row_number, '', 0, f'Failed: {str(e)[:50]}')
        except:
            pass

    return result


def run(spreadsheet_url: str, root_folder_id: str = None):
    """Main function to process all tasks from spreadsheet"""
    print("="*60)
    print("OCTOPARSE DATA EXPORT APP")
    print("="*60)
    print(f"\nStarted at: {datetime.now().strftime(TIMESTAMP_FORMAT)}")
    print(f"Spreadsheet: {spreadsheet_url}")
    print(f"Root folder ID: {root_folder_id or 'Not specified'}")

    print("\n[INIT] Initializing clients...")

    try:
        octoparse = OctoparseClient()
        print("  [OK] Octoparse client")
    except Exception as e:
        print(f"  [ERROR] Octoparse client: {e}")
        return

    try:
        sheets = GoogleSheetsClient()
        print("  [OK] Google Sheets client")
    except Exception as e:
        print(f"  [ERROR] Google Sheets client: {e}")
        return

    try:
        drive = GoogleDriveClient()
        print("  [OK] Google Drive client")
    except Exception as e:
        print(f"  [ERROR] Google Drive client: {e}")
        return

    print("\n[FETCH] Getting tasks from spreadsheet...")
    try:
        tasks = sheets.get_tasks(spreadsheet_url)
        print(f"  [OK] Found {len(tasks)} tasks")
    except Exception as e:
        print(f"  [ERROR] Failed to get tasks: {e}")
        return

    if not tasks:
        print("\n[INFO] No tasks to process")
        return

    print("\n" + "-"*60)
    print("PROCESSING TASKS")
    print("-"*60)

    results = {'success': 0, 'failed': 0, 'no_data': 0, 'total': len(tasks)}

    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}] Processing...")
        result = process_task(task, octoparse, drive, sheets, spreadsheet_url, root_folder_id)

        if result['status'] == 'Success':
            results['success'] += 1
        elif result['status'] == 'No Data':
            results['no_data'] += 1
        else:
            results['failed'] += 1

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tasks: {results['total']}")
    print(f"Success: {results['success']}")
    print(f"No data: {results['no_data']}")
    print(f"Failed: {results['failed']}")
    print(f"\nCompleted at: {datetime.now().strftime(TIMESTAMP_FORMAT)}")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <spreadsheet_url> [root_folder_id]")
        sys.exit(1)

    spreadsheet_url = sys.argv[1]
    root_folder_id = sys.argv[2] if len(sys.argv) > 2 else None

    run(spreadsheet_url, root_folder_id)

"""
Octoparse API Client
"""

from octoparse import Octoparse
import pandas as pd


class OctoparseClient:
    """Wrapper for Octoparse API"""

    def __init__(self):
        self.client = Octoparse()

    def get_task_data(self, task_id: str) -> pd.DataFrame:
        """Get task data as DataFrame"""
        data = self.client.get_task_data(task_id)
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()

    def list_task_groups(self):
        """List all task groups"""
        return self.client.list_all_task_groups()

    def list_tasks(self, group_id: str):
        """List tasks in a group"""
        return self.client.list_all_tasks_in_group(group_id)

    def get_task_name(self, task_id: str) -> str:
        """Get task name by task ID"""
        groups = self.client.list_all_task_groups()
        for group in groups:
            tasks = self.client.list_all_tasks_in_group(group['taskGroupId'])
            for task in tasks:
                if task['taskId'] == task_id:
                    return task.get('taskName', '')
        return ''

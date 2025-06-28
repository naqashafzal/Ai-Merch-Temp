# src/history_manager.py

import json
import os
from datetime import datetime

class HistoryManager:
    """Saves and retrieves analysis results from a local JSON file."""
    def __init__(self, history_file='history.json'):
        self.history_file = history_file
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def get_history(self):
        """Retrieves all historical records, most recent first."""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            return sorted(history, key=lambda x: x['timestamp'], reverse=True)
        except (IOError, json.JSONDecodeError):
            return []

    def save_analysis(self, analysis_data):
        """Saves a new analysis record to the history file."""
        history = self.get_history()
        record = {
            "id": len(history) + 1,
            "timestamp": datetime.now().isoformat(),
            **analysis_data
        }
        history.insert(0, record)
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=4)
        return record
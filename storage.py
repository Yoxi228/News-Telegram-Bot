import json
import os
from config import SOURCES_FILE, logger

class Storage:
    def __init__(self):
        self.sources = self._load_sources()
        self.chat_ids = set()  # Store chat IDs where bot should send messages

    def _load_sources(self):
        """Load sources from JSON file"""
        if os.path.exists(SOURCES_FILE):
            try:
                with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Initialize chat_ids from saved data
                    self.chat_ids = set(data.get('chat_ids', []))
                    return data.get('sources', {"vk": [], "twitter": []})
            except json.JSONDecodeError:
                logger.error("Error decoding sources file")
                return {"vk": [], "twitter": []}
        return {"vk": [], "twitter": []}

    def _save_sources(self):
        """Save sources to JSON file"""
        try:
            data = {
                'sources': self.sources,
                'chat_ids': list(self.chat_ids)
            }
            with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving sources: {e}")

    def add_chat(self, chat_id):
        """Add a chat ID to receive messages"""
        self.chat_ids.add(chat_id)
        self._save_sources()

    def remove_chat(self, chat_id):
        """Remove a chat ID from receiving messages"""
        self.chat_ids.discard(chat_id)
        self._save_sources()

    def get_chats(self):
        """Get all chat IDs"""
        return list(self.chat_ids)

    def add_source(self, source_type, source_id, name):
        """Add a new source"""
        if source_type not in self.sources:
            self.sources[source_type] = []

        # Check if source already exists
        if any(s['id'] == source_id for s in self.sources[source_type]):
            return False

        self.sources[source_type].append({
            'id': source_id,
            'name': name,
            'last_post_id': None
        })
        self._save_sources()
        return True

    def remove_source(self, source_type, source_id):
        """Remove a source"""
        if source_type in self.sources:
            self.sources[source_type] = [
                s for s in self.sources[source_type] if s['id'] != source_id
            ]
            self._save_sources()
            return True
        return False

    def get_sources(self, source_type=None):
        """Get all sources or sources of specific type"""
        if source_type:
            return self.sources.get(source_type, [])
        return self.sources

    def update_last_post_id(self, source_type, source_id, post_id):
        """Update the last post ID for a source"""
        for source in self.sources[source_type]:
            if source['id'] == source_id:
                source['last_post_id'] = post_id
                self._save_sources()
                return True
        return False

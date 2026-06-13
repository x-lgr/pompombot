import os
from config import Config

class UserBackup:
    @staticmethod
    def add_user_to_txt(user_id):
        """Add user ID to users.txt if not exists"""
        if not os.path.exists(Config.USERS_TXT_FILE):
            with open(Config.USERS_TXT_FILE, 'w') as f:
                pass
        
        with open(Config.USERS_TXT_FILE, 'r') as f:
            existing_users = f.read().splitlines()
        
        if str(user_id) not in existing_users:
            with open(Config.USERS_TXT_FILE, 'a') as f:
                f.write(f"{user_id}\n")
            return True
        return False
    
    @staticmethod
    def get_all_users_from_txt():
        """Get all user IDs from users.txt"""
        if not os.path.exists(Config.USERS_TXT_FILE):
            return []
        
        with open(Config.USERS_TXT_FILE, 'r') as f:
            users = [line.strip() for line in f if line.strip()]
        return users
    
    @staticmethod
    def import_users_from_content(content):
        """Import users from uploaded file content"""
        imported = 0
        skipped = 0
        users = content.splitlines()
        
        existing_users = UserBackup.get_all_users_from_txt()
        
        for user in users:
            user = user.strip()
            if user.isdigit() and user not in existing_users:
                with open(Config.USERS_TXT_FILE, 'a') as f:
                    f.write(f"{user}\n")
                imported += 1
            else:
                skipped += 1
        
        return imported, skipped
    
    @staticmethod
    def rebuild_database_from_txt(db):
        """Rebuild user database from users.txt"""
        users = UserBackup.get_all_users_from_txt()
        imported = 0
        
        for user_id in users:
            if user_id.isdigit():
                # Check if user exists in database
                if not db.get_user(int(user_id)):
                    db.add_user(int(user_id), None, None, None)
                    imported += 1
        
        return imported

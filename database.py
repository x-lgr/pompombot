import sqlite3
from datetime import datetime
from config import Config

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP,
                is_premium BOOLEAN DEFAULT 0,
                premium_plan TEXT,
                premium_purchase_date TIMESTAMP,
                premium_status TEXT DEFAULT 'inactive'
            )
        ''')
        
        # Start message table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS start_settings (
                id INTEGER PRIMARY KEY,
                message TEXT,
                image_file_id TEXT
            )
        ''')
        
        # Insert default start settings if not exists
        self.cursor.execute("SELECT COUNT(*) FROM start_settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO start_settings (id, message, image_file_id) 
                VALUES (1, ?, ?)
            ''', (Config.DEFAULT_START_MESSAGE, Config.DEFAULT_START_IMAGE))
            self.conn.commit()
        
        # Buttons table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS start_buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                button_id TEXT UNIQUE,
                button_name TEXT,
                button_url TEXT,
                position INTEGER
            )
        ''')
        
        # Plans table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT,
                price INTEGER,
                description TEXT,
                duration TEXT,
                sort_order INTEGER
            )
        ''')
        
        # Discounts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS discounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                discount_code TEXT,
                discount_percent INTEGER,
                original_amount INTEGER,
                discounted_amount INTEGER,
                used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP
            )
        ''')
        
        # Pending payments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_name TEXT,
                original_price INTEGER,
                discount_percent INTEGER DEFAULT 0,
                final_amount INTEGER,
                utr_number TEXT,
                screenshot_file_id TEXT,
                user_message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP
            )
        ''')
        
        # Payment settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_settings (
                id INTEGER PRIMARY KEY,
                upi_id TEXT,
                receiver_name TEXT,
                upi_name TEXT,
                bank_name TEXT,
                payment_url TEXT
            )
        ''')
        
        # Insert default payment settings if not exists
        self.cursor.execute("SELECT COUNT(*) FROM payment_settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO payment_settings (id, upi_id, receiver_name, upi_name, bank_name, payment_url)
                VALUES (1, '', '', '', '', '')
            ''')
            self.conn.commit()
        
        # Channel settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_settings (
                id INTEGER PRIMARY KEY,
                premium_channel_id TEXT,
                demo_channel_url TEXT
            )
        ''')
        
        # Insert default channel settings if not exists
        self.cursor.execute("SELECT COUNT(*) FROM channel_settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO channel_settings (id, premium_channel_id, demo_channel_url)
                VALUES (1, '', '')
            ''')
            self.conn.commit()
        
        self.conn.commit()
    
    # User methods
    def add_user(self, user_id, username, first_name, last_name):
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, join_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, datetime.now()))
        self.conn.commit()
    
    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def get_all_users(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_user_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]
    
    def make_premium(self, user_id, plan_name):
        self.cursor.execute('''
            UPDATE users 
            SET is_premium = 1, premium_plan = ?, premium_purchase_date = ?, premium_status = 'active'
            WHERE user_id = ?
        ''', (plan_name, datetime.now(), user_id))
        self.conn.commit()
    
    def get_premium_users(self):
        self.cursor.execute("SELECT user_id FROM users WHERE is_premium = 1")
        return self.cursor.fetchall()
    
    # Start message methods
    def get_start_message(self):
        self.cursor.execute("SELECT message FROM start_settings WHERE id = 1")
        result = self.cursor.fetchone()
        return result[0] if result else Config.DEFAULT_START_MESSAGE
    
    def set_start_message(self, message):
        self.cursor.execute("UPDATE start_settings SET message = ? WHERE id = 1", (message,))
        self.conn.commit()
    
    def reset_start_message(self):
        self.cursor.execute("UPDATE start_settings SET message = ? WHERE id = 1", (Config.DEFAULT_START_MESSAGE,))
        self.conn.commit()
    
    # Start image methods
    def get_start_image(self):
        self.cursor.execute("SELECT image_file_id FROM start_settings WHERE id = 1")
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def set_start_image(self, file_id):
        self.cursor.execute("UPDATE start_settings SET image_file_id = ? WHERE id = 1", (file_id,))
        self.conn.commit()
    
    def remove_start_image(self):
        self.cursor.execute("UPDATE start_settings SET image_file_id = ? WHERE id = 1", (None,))
        self.conn.commit()
    
    # Button methods
    def add_button(self, button_id, button_name, button_url, position):
        self.cursor.execute('''
            INSERT INTO start_buttons (button_id, button_name, button_url, position)
            VALUES (?, ?, ?, ?)
        ''', (button_id, button_name, button_url, position))
        self.conn.commit()
    
    def get_buttons(self):
        self.cursor.execute("SELECT * FROM start_buttons ORDER BY position")
        return self.cursor.fetchall()
    
    def get_button(self, button_id):
        self.cursor.execute("SELECT * FROM start_buttons WHERE button_id = ?", (button_id,))
        return self.cursor.fetchone()
    
    def update_button(self, button_id, button_name=None, button_url=None):
        if button_name:
            self.cursor.execute("UPDATE start_buttons SET button_name = ? WHERE button_id = ?", (button_name, button_id))
        if button_url:
            self.cursor.execute("UPDATE start_buttons SET button_url = ? WHERE button_id = ?", (button_url, button_id))
        self.conn.commit()
    
    def delete_button(self, button_id):
        self.cursor.execute("DELETE FROM start_buttons WHERE button_id = ?", (button_id,))
        self.conn.commit()
    
    def get_button_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM start_buttons")
        return self.cursor.fetchone()[0]
    
    # Plan methods
    def add_plan(self, plan_name, price, description, duration, sort_order):
        self.cursor.execute('''
            INSERT INTO plans (plan_name, price, description, duration, sort_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (plan_name, price, description, duration, sort_order))
        self.conn.commit()
    
    def get_plans(self):
        self.cursor.execute("SELECT * FROM plans ORDER BY sort_order")
        return self.cursor.fetchall()
    
    def get_plan(self, plan_id):
        self.cursor.execute("SELECT * FROM plans WHERE id = ?", (plan_id,))
        return self.cursor.fetchone()
    
    def update_plan(self, plan_id, plan_name=None, price=None, description=None, duration=None, sort_order=None):
        if plan_name:
            self.cursor.execute("UPDATE plans SET plan_name = ? WHERE id = ?", (plan_name, plan_id))
        if price:
            self.cursor.execute("UPDATE plans SET price = ? WHERE id = ?", (price, plan_id))
        if description:
            self.cursor.execute("UPDATE plans SET description = ? WHERE id = ?", (description, plan_id))
        if duration:
            self.cursor.execute("UPDATE plans SET duration = ? WHERE id = ?", (duration, plan_id))
        if sort_order:
            self.cursor.execute("UPDATE plans SET sort_order = ? WHERE id = ?", (sort_order, plan_id))
        self.conn.commit()
    
    def delete_plan(self, plan_id):
        self.cursor.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
        self.conn.commit()
    
    # Discount methods
    def save_discount(self, user_id, discount_code, discount_percent, original_amount, discounted_amount):
        self.cursor.execute('''
            INSERT INTO discounts (user_id, discount_code, discount_percent, original_amount, discounted_amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, discount_code, discount_percent, original_amount, discounted_amount, datetime.now()))
        self.conn.commit()
        return discount_code
    
    def get_discount(self, user_id, discount_code):
        self.cursor.execute('''
            SELECT * FROM discounts 
            WHERE user_id = ? AND discount_code = ? AND used = 0
        ''', (user_id, discount_code))
        return self.cursor.fetchone()
    
    def use_discount(self, discount_id):
        self.cursor.execute("UPDATE discounts SET used = 1 WHERE id = ?", (discount_id,))
        self.conn.commit()
    
    # Payment methods
    def add_pending_payment(self, user_id, plan_name, original_price, discount_percent, final_amount, utr_number, screenshot_file_id, user_message):
        self.cursor.execute('''
            INSERT INTO pending_payments 
            (user_id, plan_name, original_price, discount_percent, final_amount, utr_number, screenshot_file_id, user_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, plan_name, original_price, discount_percent, final_amount, utr_number, screenshot_file_id, user_message, datetime.now()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_pending_payments(self):
        self.cursor.execute("SELECT * FROM pending_payments WHERE status = 'pending' ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def get_pending_payment(self, payment_id):
        self.cursor.execute("SELECT * FROM pending_payments WHERE id = ?", (payment_id,))
        return self.cursor.fetchone()
    
    def update_payment_status(self, payment_id, status):
        self.cursor.execute("UPDATE pending_payments SET status = ? WHERE id = ?", (status, payment_id))
        self.conn.commit()
    
    def get_pending_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM pending_payments WHERE status = 'pending'")
        return self.cursor.fetchone()[0]
    
    # Payment settings
    def get_payment_settings(self):
        self.cursor.execute("SELECT upi_id, receiver_name, upi_name, bank_name, payment_url FROM payment_settings WHERE id = 1")
        return self.cursor.fetchone()
    
    def set_upi_id(self, upi_id):
        self.cursor.execute("UPDATE payment_settings SET upi_id = ? WHERE id = 1", (upi_id,))
        self.conn.commit()
    
    def set_receiver_name(self, name):
        self.cursor.execute("UPDATE payment_settings SET receiver_name = ? WHERE id = 1", (name,))
        self.conn.commit()
    
    def set_upi_name(self, upi_name):
        self.cursor.execute("UPDATE payment_settings SET upi_name = ? WHERE id = 1", (upi_name,))
        self.conn.commit()
    
    def set_bank_name(self, bank_name):
        self.cursor.execute("UPDATE payment_settings SET bank_name = ? WHERE id = 1", (bank_name,))
        self.conn.commit()
    
    def set_payment_url(self, url):
        self.cursor.execute("UPDATE payment_settings SET payment_url = ? WHERE id = 1", (url,))
        self.conn.commit()
    
    # Channel settings
    def get_channel_settings(self):
        self.cursor.execute("SELECT premium_channel_id, demo_channel_url FROM channel_settings WHERE id = 1")
        return self.cursor.fetchone()
    
    def set_premium_channel(self, channel_id):
        self.cursor.execute("UPDATE channel_settings SET premium_channel_id = ? WHERE id = 1", (channel_id,))
        self.conn.commit()
    
    def set_demo_channel(self, url):
        self.cursor.execute("UPDATE channel_settings SET demo_channel_url = ? WHERE id = 1", (url,))
        self.conn.commit()
    
    # Statistics
    def get_today_users_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?", (today,))
        return self.cursor.fetchone()[0]
    
    def get_week_users_count(self):
        self.cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE join_date >= datetime('now', '-7 days')
        ''')
        return self.cursor.fetchone()[0]
    
    def get_approved_payments_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM pending_payments WHERE status = 'approved'")
        return self.cursor.fetchone()[0]
    
    def get_rejected_payments_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM pending_payments WHERE status = 'rejected'")
        return self.cursor.fetchone()[0]
    
    def get_discounts_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM discounts")
        return self.cursor.fetchone()[0]

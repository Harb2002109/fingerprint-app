
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.clock import Clock
import sqlite3
import hashlib
import json
import os

DB_PATH = "users.db"
DATA_DIR = "user_data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fingerprint_registered INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text='🔐 تسجيل الدخول', font_size='28sp', size_hint_y=None, height=50))
        layout.add_widget(Label(text='اسم المستخدم:', size_hint_y=None, height=30))
        self.username = TextInput(multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.username)
        layout.add_widget(Label(text='كلمة المرور:', size_hint_y=None, height=30))
        self.password = TextInput(password=True, multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.password)
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        fp_btn = Button(text='👆 بصمة الإصبع')
        fp_btn.bind(on_press=self.use_fingerprint)
        btn_layout.add_widget(fp_btn)
        login_btn = Button(text='دخول')
        login_btn.bind(on_press=self.login)
        btn_layout.add_widget(login_btn)
        layout.add_widget(btn_layout)
        register_btn = Button(text='📝 إنشاء حساب جديد', size_hint_y=None, height=40)
        register_btn.bind(on_press=self.go_to_register)
        layout.add_widget(register_btn)
        self.message = Label(text='', color=(1, 0.2, 0.2, 1), size_hint_y=None, height=30)
        layout.add_widget(self.message)
        self.add_widget(layout)

    def use_fingerprint(self, instance):
        try:
            from plyer import fingerprint
            fingerprint.authenticate(on_success=self.fp_success, on_error=self.fp_error)
            self.message.text = '⏳ اضغط على مستشعر البصمة...'
        except:
            self.message.text = '❌ المستشعر غير مدعوم أو لا يعمل على الكمبيوتر'

    def fp_success(self):
        Clock.schedule_once(lambda dt: self._fp_success_ui(), 0)

    def _fp_success_ui(self):
        username = self.username.text.strip()
        if not username:
            self.message.text = '❌ أدخل اسم المستخدم أولاً'
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND fingerprint_registered = 1", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.message.text = '✅ تم الدخول بالبصمة!'
            self.manager.get_screen('home').user_id = user[0]
            self.manager.get_screen('home').username = user[1]
            Clock.schedule_once(lambda dt: self._switch_to_home(), 1)
        else:
            self.message.text = '❌ لم يتم تسجيل بصمة لهذا المستخدم'

    def _switch_to_home(self):
        self.manager.current = 'home'
        self.message.text = ''
        self.username.text = ''
        self.password.text = ''

    def fp_error(self, error):
        Clock.schedule_once(lambda dt: self._fp_error_ui(error), 0)

    def _fp_error_ui(self, error):
        self.message.text = f'❌ خطأ: {error}'

    def login(self, instance):
        username = self.username.text.strip()
        password = self.password.text
        if not username or not password:
            self.message.text = '❌ أدخل جميع البيانات'
            return
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.message.text = '✅ تم الدخول بنجاح'
            self.manager.get_screen('home').user_id = user[0]
            self.manager.get_screen('home').username = user[1]
            Clock.schedule_once(lambda dt: self._switch_to_home(), 1)
        else:
            self.message.text = '❌ بيانات غير صحيحة'

    def go_to_register(self, instance):
        self.manager.current = 'register'
        self.message.text = ''

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register'
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text='📝 إنشاء حساب جديد', font_size='28sp', size_hint_y=None, height=50))
        layout.add_widget(Label(text='اسم المستخدم:', size_hint_y=None, height=30))
        self.username = TextInput(multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.username)
        layout.add_widget(Label(text='كلمة المرور:', size_hint_y=None, height=30))
        self.password = TextInput(password=True, multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.password)
        layout.add_widget(Label(text='تسجيل بصمة الإصبع:', size_hint_y=None, height=30))
        self.fp_status = Label(text='❌ لم يتم التسجيل', color=(1, 0.5, 0, 1), size_hint_y=None, height=30)
        layout.add_widget(self.fp_status)
        fp_btn = Button(text='👆 تسجيل البصمة الآن', size_hint_y=None, height=50)
        fp_btn.bind(on_press=self.register_fingerprint)
        layout.add_widget(fp_btn)
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        register_btn = Button(text='إنشاء الحساب')
        register_btn.bind(on_press=self.register)
        btn_layout.add_widget(register_btn)
        back_btn = Button(text='رجوع')
        back_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(back_btn)
        layout.add_widget(btn_layout)
        self.message = Label(text='', color=(1, 0.2, 0.2, 1), size_hint_y=None, height=30)
        layout.add_widget(self.message)
        self.fingerprint_ok = False
        self.add_widget(layout)

    def register_fingerprint(self, instance):
        try:
            from plyer import fingerprint
            fingerprint.authenticate(on_success=self.fp_reg_success, on_error=self.fp_reg_error)
            self.message.text = '⏳ اضغط على مستشعر البصمة...'
        except:
            self.message.text = '❌ التسجيل غير مدعوم على هذا الجهاز'

    def fp_reg_success(self):
        Clock.schedule_once(lambda dt: self._fp_reg_success_ui(), 0)

    def _fp_reg_success_ui(self):
        self.fingerprint_ok = True
        self.fp_status.text = '✅ تم تسجيل البصمة'
        self.message.text = ''

    def fp_reg_error(self, error):
        Clock.schedule_once(lambda dt: self._fp_reg_error_ui(error), 0)

    def _fp_reg_error_ui(self, error):
        self.message.text = f'❌ فشل التسجيل: {error}'

    def register(self, instance):
        username = self.username.text.strip()
        password = self.password.text
        if not username or not password:
            self.message.text = '❌ أدخل جميع البيانات'
            return
        if not self.fingerprint_ok:
            self.message.text = '❌ يجب تسجيل البصمة أولاً'
            return
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash, fingerprint_registered) VALUES (?, ?, 1)", (username, password_hash))
            conn.commit()
            conn.close()
            self.message.text = '✅ تم إنشاء الحساب!'
            Clock.schedule_once(lambda dt: self._go_to_login(), 1.5)
        except sqlite3.IntegrityError:
            self.message.text = '❌ اسم المستخدم موجود'
            conn.close()

    def _go_to_login(self):
        self.manager.current = 'login'
        self.message.text = ''
        self.username.text = ''
        self.password.text = ''
        self.fp_status.text = '❌ لم يتم التسجيل'
        self.fingerprint_ok = False

    def go_back(self, instance):
        self.manager.current = 'login'
        self.message.text = ''

class HomeScreen(Screen):
    user_id = None
    username = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.welcome_label = Label(text='', font_size='24sp', size_hint_y=None, height=40)
        layout.add_widget(self.welcome_label)
        layout.add_widget(Label(text='💾 أدخل بياناتك للحفظ:', size_hint_y=None, height=30))
        self.data_input = TextInput(hint_text='اكتب هنا أي بيانات تريد حفظها...', size_hint_y=None, height=100)
        layout.add_widget(self.data_input)
        save_btn = Button(text='حفظ البيانات', size_hint_y=None, height=50)
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)
        layout.add_widget(Label(text='📂 البيانات المخزنة:', size_hint_y=None, height=30))
        self.stored_data_label = Label(text='لا توجد بيانات مخزنة', color=(0.7, 0.7, 0.7, 1), text_size=(400, None), halign='center', valign='top')
        layout.add_widget(self.stored_data_label)
        logout_btn = Button(text='🚪 تسجيل الخروج', size_hint_y=None, height=50)
        logout_btn.bind(on_press=self.logout)
        layout.add_widget(logout_btn)
        self.add_widget(layout)

    def on_enter(self):
        self.welcome_label.text = f'أهلاً {self.username}!'
        self.load_stored_data()

    def load_stored_data(self):
        filename = f"{DATA_DIR}/{self.username}_data.json"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stored_data_label.text = str(data.get('content', 'لا توجد بيانات'))
        except:
            self.stored_data_label.text = 'لا توجد بيانات مخزنة'

    def save_data(self, instance):
        data_content = self.data_input.text.strip()
        if not data_content:
            self.stored_data_label.text = '❌ لا توجد بيانات للحفظ'
            return
        filename = f"{DATA_DIR}/{self.username}_data.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"user_id": self.user_id, "username": self.username, "content": data_content}, f, ensure_ascii=False, indent=2)
            self.stored_data_label.text = f'✅ تم الحفظ: {data_content[:50]}...'
            self.data_input.text = ''
        except Exception as e:
            self.stored_data_label.text = f'❌ خطأ: {e}'

    def logout(self, instance):
        self.user_id = None
        self.username = ""
        self.manager.current = 'login'

class FingerprintAuthApp(App):
    def build(self):
        self.title = '🔐 تطبيق المصادقة'
        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())
        sm.add_widget(HomeScreen())
        return sm

if __name__ == '__main__':
    FingerprintAuthApp().run()[paste the entire main.py code here]

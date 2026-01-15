from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import platform
from datetime import datetime

import db

if platform == "android":
    Window.softinput_mode = "below_target"


# ===============================
# 📋 PRODUCT LIST
# ===============================
class ProductListScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=5
        )

        # 🔝 ÜST BAR
        top_bar = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=5
        )

        menu_btn = Button(
            text="☰",
            size_hint_x=None,
            width=50
        )
        menu_btn.bind(on_release=self.open_menu)

        sort_btn = Button(
            text="⇅ Sırala",
            size_hint_x=None,
            width=100
        )
        sort_btn.bind(on_release=self.open_sort_menu)

        top_bar.add_widget(menu_btn)
        top_bar.add_widget(sort_btn)
        root.add_widget(top_bar)

        # 🔍 ARAMA
        self.search = TextInput(
            hint_text="Ürün ara (kod / isim)",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        self.search.bind(text=self.refresh)
        root.add_widget(self.search)

        # 📜 LİSTE
        scroll = ScrollView()
        self.layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.layout.bind(
            minimum_height=self.layout.setter("height")
        )
        scroll.add_widget(self.layout)
        root.add_widget(scroll)

        # ➕ YENİ ÜRÜN
        root.add_widget(Button(
            text="➕ Yeni Ürün",
            size_hint_y=None,
            height=50,
            on_release=lambda x: setattr(self.manager, "current", "add")
        ))

        self.add_widget(root)

    # ===============================
    # 🔁 LIFECYCLE
    # ===============================
    def on_enter(self):
        self.refresh()

    def refresh(self, *args):
        self.layout.clear_widgets()
        products = db.get_products(self.search.text.strip() or None)

        for p in products:
            btn = Button(
                text=f"{p['name']} ({p['quantity']})",
                size_hint_y=None,
                height=50
            )
            btn.bind(
                on_release=lambda x, pid=p["id"]: self.open_product(pid)
            )
            self.layout.add_widget(btn)

    def open_product(self, product_id):
        detail = self.manager.get_screen("detail")
        detail.load_product(product_id)
        self.manager.current = "detail"

    # ===============================
    # 🔠 SIRALAMA
    # ===============================
    def open_sort_menu(self, instance):
        from kivy.uix.popup import Popup

        box = BoxLayout(
            orientation="vertical",
            spacing=5,
            padding=5
        )

        popup = Popup(
            title="Sıralama",
            content=box,
            size_hint=(0.8, None),
            height=300
        )

        box.add_widget(Button(
            text="Tarih (Yeni → Eski)",
            on_release=lambda x: self.set_sort("date_desc", popup)
        ))
        box.add_widget(Button(
            text="Tarih (Eski → Yeni)",
            on_release=lambda x: self.set_sort("date_asc", popup)
        ))
        box.add_widget(Button(
            text="A → Z",
            on_release=lambda x: self.set_sort("name_asc", popup)
        ))
        box.add_widget(Button(
            text="Z → A",
            on_release=lambda x: self.set_sort("name_desc", popup)
        ))

        popup.open()

    def set_sort(self, sort_key, popup):
        db.set_setting("product_sort", sort_key)
        popup.dismiss()
        self.refresh()

    # ===============================
    # ☰ HAMBURGER MENU
    # ===============================
    def open_menu(self, instance):
        from kivy.uix.popup import Popup

        box = BoxLayout(
            orientation="vertical",
            spacing=5,
            padding=5
        )

        popup = Popup(
            title="Menü",
            content=box,
            size_hint=(0.7, None),
            height=220
        )

        box.add_widget(Button(
            text="ℹ️ Uygulama Hakkında",
            size_hint_y=None,
            height=45,
            on_release=lambda x: self.open_and_close("about", popup)
        ))

        box.add_widget(Button(
            text="🔐 Gizlilik Politikası",
            size_hint_y=None,
            height=45,
            on_release=lambda x: self.open_and_close("privacy", popup)
        ))

        box.add_widget(Button(
            text="❌ Kapat",
            size_hint_y=None,
            height=40,
            on_release=popup.dismiss
        ))

        popup.open()

    def open_and_close(self, screen_name, popup):
        popup.dismiss()
        self.manager.current = screen_name


# ===============================
# ➕ ADD PRODUCT
# ===============================
class AddProductScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )

        # 🔝 ÜST BAR
        top_bar = BoxLayout(size_hint_y=None, height=40)

        back_btn = Button(text="← Geri")
        back_btn.bind(
            on_release=lambda x: setattr(self.manager, "current", "list")
        )

        top_bar.add_widget(back_btn)
        root.add_widget(top_bar)

        # 📄 FORM ALANI
        self.code = TextInput(
            hint_text="Ürün Kodu",
            multiline=False,
            size_hint_y=None,
            height=40
        )

        self.product_name = TextInput(
            hint_text="Ürün Adı",
            multiline=False,
            size_hint_y=None,
            height=40
        )

        self.category = TextInput(
            hint_text="Kategori",
            multiline=False,
            size_hint_y=None,
            height=40
        )

        self.quantity = TextInput(
            hint_text="Başlangıç Adedi",
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=40
        )

        self.note = TextInput(
            hint_text="Not",
            size_hint_y=None,
            height=60
        )

        save_btn = Button(
            text="💾 Kaydet",
            size_hint_y=None,
            height=45
        )
        save_btn.bind(on_release=self.save_product)

        # FORMU ROOT'A EKLE
        root.add_widget(self.code)
        root.add_widget(self.product_name)
        root.add_widget(self.category)
        root.add_widget(self.quantity)
        root.add_widget(self.note)
        root.add_widget(save_btn)

        self.add_widget(root)

    def on_pre_enter(self):
        # Ekran her açıldığında alanları temizle
        self.code.text = ""
        self.product_name.text = ""
        self.category.text = ""
        self.quantity.text = ""
        self.note.text = ""

    def save_product(self, instance):
        if not self.code.text or not self.product_name.text or not self.quantity.text:
            return  # basit validation

        product_id = db.add_product(
            code=self.code.text.strip(),
            name=self.product_name.text.strip(),
            category=self.category.text.strip(),
            quantity=int(self.quantity.text),
            note=self.note.text.strip()
        )

        # İlk stok hareketi
        db.add_movement(
            product_id=product_id,
            mtype="IN",
            amount=int(self.quantity.text),
            description="İlk stok"
        )

        self.manager.current = "list"


# ===============================
# 📄 PRODUCT DETAIL
# ===============================
class ProductDetailScreen(Screen):

    def section_title(self, text):
        return Label(
            text=f"{text}:",
            bold=True,
            size_hint_y=None,
            height=22,
            halign="left",
            valign="middle",
            color=(0.75, 0.75, 0.75, 1),
            text_size=(Window.width - 40, None)
        )

    def section_value(self, text, height=30, font_size=14):
        return Label(
            text=text,
            font_size=font_size,
            size_hint_y=None,
            height=height,
            halign="left",
            valign="middle",
            text_size=(Window.width - 40, None)
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_id = None

        self.root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )
        self.add_widget(self.root)

    def load_product(self, product_id):
        self.product_id = product_id
        self.refresh()

    def refresh(self):
        self.root.clear_widgets()

        product = db.get_product(self.product_id)
        if not product:
            return

        # 🔝 ÜST BAR
        top_bar = BoxLayout(size_hint_y=None, height=50)

        back_btn = Button(text="← Ürün Listesine Dön")
        back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "list"))

        del_btn = Button(
            text="🗑 Sil",
            size_hint_x=None,
            width=80,
            background_normal="",
            background_color=(0.8, 0, 0, 1)
        )
        del_btn.bind(on_release=self.confirm_delete)

        top_bar.add_widget(back_btn)
        top_bar.add_widget(del_btn)
        self.root.add_widget(top_bar)

        self.root.add_widget(Label(
            text="Ürün Hakkında",
            font_size=18,
            size_hint_y=None,
            height=35
        ))

        # 📜 SCROLL
        scroll = ScrollView()
        content = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        # 🏷️ ÜRÜN ADI
        content.add_widget(self.section_title("Ürün Adı"))
        content.add_widget(
    Label(
        text=product["name"],
        font_size=20,
        bold=True,
        size_hint_y=None,
        height=36,
        halign="left",
        valign="middle",
        text_size=(Window.width - 40, None)
    )
)
        # 🏷️ KATEGORİ
        if product["category"]:
            content.add_widget(self.section_title("Kategori"))
            content.add_widget(self.section_value(product["category"]))

        # 🕒 İLK KAYIT
        if product["created_at"]:
            dt = datetime.fromisoformat(product["created_at"])
            content.add_widget(self.section_title("İlk Kayıt"))
            content.add_widget(
                Label(
                    text=dt.strftime("%d.%m.%Y %H:%M"),
                    size_hint_y=None,
                    height=30,
                    halign="left",
                    valign="middle",
                    color=(0.2, 0.8, 0.2, 1),  # YEŞİL
                    text_size=(Window.width - 40, None)
                )
            )

        # 📦 STOK
        content.add_widget(self.section_title("Mevcut Stok"))
        content.add_widget(
            self.section_value(f"{product['quantity']} adet")
        )

        # 📝 NOT
        if product["note"]:
            content.add_widget(self.section_title("Not"))
            content.add_widget(
                self.section_value(product["note"], height=40)
            )

        # ✏️ DÜZENLE
        content.add_widget(Button(
            text="✏️ Ürünü Düzenle",
            size_hint_y=None,
            height=45
        ))

        scroll.add_widget(content)
        self.root.add_widget(scroll)


    def confirm_delete(self, instance):
        from kivy.uix.popup import Popup

        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        box.add_widget(Label(
            text="Bu ürünü silmek istiyor musunuz?\nBu işlem geri alınamaz."
        ))

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        cancel = Button(text="İptal")
        delete = Button(
            text="Sil",
            background_normal="",
            background_color=(0.8, 0, 0, 1)
        )

        btns.add_widget(cancel)
        btns.add_widget(delete)
        box.add_widget(btns)

        popup = Popup(
            title="Onay",
            content=box,
            size_hint=(0.8, None),
            height=220
        )

        cancel.bind(on_release=popup.dismiss)
        delete.bind(on_release=lambda x: self.delete_and_exit(popup))
        popup.open()

    def delete_and_exit(self, popup):
        from kivy.uix.popup import Popup

        try:
            db.delete_product(self.product_id)
            popup.dismiss()
            self.manager.current = "list"

        except ValueError as e:
            popup.dismiss()

            Popup(
                title="Silinemedi",
                content=Label(
                    text=str(e),
                    halign="center"
                ),
                size_hint=(0.8, None),
                height=180
            ).open()


# ===============================
# ℹ️ ABOUT
# ===============================
class AboutScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )

        # 🔝 ÜST BAR
        top_bar = BoxLayout(size_hint_y=None, height=50)

        back_btn = Button(text="← Geri")
        back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "list"))

        top_bar.add_widget(back_btn)
        root.add_widget(top_bar)

        # 📜 SCROLL
        scroll = ScrollView()
        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Label(
            text="Uygulama Hakkında",
            font_size=20,
            size_hint_y=None,
            height=40
        ))

        content.add_widget(Label(
            text=(
                "Bu uygulama, küçük ve orta ölçekli işletmeler için "
                "tasarlanmış offline-öncelikli bir stok takip uygulamasıdır.\n\n"
                "Ürünlerinizi kolayca ekleyebilir, düzenleyebilir, "
                "stok giriş ve çıkışlarını takip edebilirsiniz.\n\n"
                "Uygulama internet bağlantısı gerektirmez. "
                "Tüm veriler yalnızca cihazınızda saklanır.\n\n"
                "Bu uygulama bir muhasebe programı değildir ve "
                "herhangi bir ticari garanti veya yatırım danışmanlığı sunmaz."
            ),
            halign="left",
            valign="top",
            text_size=(Window.width - 40, None),
            size_hint_y=None
        ))

        scroll.add_widget(content)
        root.add_widget(scroll)

        self.add_widget(root)

# ===============================
# 🔐 PRIVACY POLICY
# ===============================
class PrivacyScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )

        # 🔝 ÜST BAR
        top_bar = BoxLayout(size_hint_y=None, height=50)
        back_btn = Button(text="← Geri")
        back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "list"))
        top_bar.add_widget(back_btn)
        root.add_widget(top_bar)

        # 📜 SCROLL
        scroll = ScrollView()
        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        # 🔹 BAŞLIK
        content.add_widget(Label(
            text="Gizlilik Politikası",
            font_size=20,
            size_hint_y=None,
            height=40
        ))

        # 🔹 METİN
        policy_text = Label(
            text=(
                "Bu uygulama, kullanıcı gizliliğine önem verir.\n\n"

                "🔹 Kişisel Veriler\n"
                "Uygulama, kullanıcıdan herhangi bir kişisel veri talep etmez. "
                "Ad, e-posta, telefon numarası, konum bilgisi veya cihaz tanımlayıcıları "
                "toplanmaz ve saklanmaz.\n\n"

                "🔹 Veri Saklama\n"
                "Uygulama içinde girilen tüm veriler yalnızca kullanıcının cihazında "
                "yerel olarak saklanır. Veriler geliştiriciye veya üçüncü taraflara "
                "aktarılmaz.\n\n"

                "🔹 İnternet ve Üçüncü Taraf Hizmetler\n"
                "Uygulama internet bağlantısı gerektirmez ve herhangi bir üçüncü taraf "
                "servis veya API ile veri paylaşımı yapmaz.\n\n"

                "🔹 Veri Güvenliği ve Yedekleme\n"
                "Verilerin güvenliği ve yedeklenmesi tamamen kullanıcının "
                "sorumluluğundadır. Veri kaybı, cihaz arızası veya kullanıcı hatalarından "
                "geliştirici sorumlu tutulamaz.\n\n"

                "🔹 Sorumluluk Reddi\n"
                "Uygulama \"olduğu gibi\" sunulmaktadır. Geliştirici, uygulamanın "
                "kullanımından doğabilecek doğrudan veya dolaylı zararlardan, "
                "veri kayıplarından veya iş kesintilerinden sorumlu değildir.\n\n"

                "🔹 Değişiklikler\n"
                "Bu gizlilik politikası gerektiğinde güncellenebilir. Güncellemeler "
                "uygulama üzerinden yayınlandığı anda geçerli olur."
            ),
            halign="left",
            valign="top",
            text_size=(Window.width - 40, None),
            size_hint_y=None
        )

        policy_text.bind(
            texture_size=lambda instance, value: setattr(instance, "height", value[1])
        )

        content.add_widget(policy_text)

        scroll.add_widget(content)
        root.add_widget(scroll)

        self.add_widget(root)


# ===============================
# 🚀 APP
# ===============================
class StockApp(App):

    def build(self):
        db.init_db()
        db.init_settings()

        sm = ScreenManager(transition=SlideTransition())

        sm.add_widget(ProductListScreen(name="list"))
        sm.add_widget(AddProductScreen(name="add"))
        sm.add_widget(ProductDetailScreen(name="detail"))
        sm.add_widget(AboutScreen(name="about"))
        sm.add_widget(PrivacyScreen(name="privacy"))

        sm.current = "list"
        return sm


if __name__ == "__main__":
    StockApp().run()

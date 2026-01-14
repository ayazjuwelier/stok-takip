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

import db

# -------------------- ANDROID FIX --------------------
if platform == "android":
    Window.softinput_mode = "below_target"

# -------------------- SCREENS --------------------

class ProductListScreen(Screen):

    def __init__(self, **kwargs):
        print(">>> ProductListScreen INIT")
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        # 🔍 ARAMA
        self.search = TextInput(
            hint_text="Ürün ara (kod / isim)",
            multiline=False,
            size_hint_y=None,
            height=45
        )
        self.search.bind(text=self.refresh)
        root.add_widget(self.search)

        # 🔠 SIRALA
        sort_btn = Button(
            text="Sırala",
            size_hint_y=None,
            height=40
        )
        sort_btn.bind(on_release=self.open_sort_menu)
        root.add_widget(sort_btn)

        # 📜 LİSTE
        scroll = ScrollView(size_hint_y=1)
        self.list_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=4,
            padding=4
        )
        self.list_container.bind(
            minimum_height=self.list_container.setter("height")
        )
        scroll.add_widget(self.list_container)
        root.add_widget(scroll)

        # ➕ YENİ ÜRÜN
        add_btn = Button(
            text="＋ Yeni Ürün",
            size_hint_y=None,
            height=50
        )
        root.add_widget(add_btn)

    def on_enter(self):
        if hasattr(self, "list_container"):
            self.refresh()
        else:
            print("⚠ list_container yok, refresh atlandı")

    def refresh(self, *args):
        import db

        self.list_container.clear_widgets()

        search_text = self.search.text.strip()
        products = db.get_products(search_text if search_text else None)

        for p in products:
            btn = Button(
                text=f"{p['name']} ({p['quantity']})",
                size_hint_y=None,
                height=50
            )
            btn.bind(
                on_release=lambda x, pid=p["id"]: self.open_product(pid)
            )
            self.list_container.add_widget(btn)

    def open_product(self, product_id):
        detail = self.manager.get_screen("detail")
        detail.load_product(product_id)
        self.manager.current = "detail"

    def open_sort_menu(self, instance):
        from kivy.uix.popup import Popup

        box = BoxLayout(orientation="vertical", spacing=5, padding=5)

        popup = Popup(
            title="Sıralama",
            content=box,
            size_hint=(0.8, 0.5)
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


    # ---------- AUTOCOMPLETE ----------

    def on_search_text(self, instance, text):
        text = text.strip()

        if len(text) < 2:
            self.close_suggestions()
            return

        products = db.get_products(text)
        if not products:
            self.close_suggestions()
            return

        self.show_suggestions(products[:5])

    def show_suggestions(self, products):
        from kivy.uix.popup import Popup

        if self.suggest_popup:
            self.suggest_layout.clear_widgets()
        else:
            self.suggest_layout = GridLayout(
                cols=1,
                spacing=5,
                padding=5,
                size_hint_y=None
            )
            self.suggest_layout.bind(
                minimum_height=self.suggest_layout.setter("height")
            )

            scroll = ScrollView(size_hint=(1, None), height=200)
            scroll.add_widget(self.suggest_layout)

            self.suggest_popup = Popup(
                title="Ürünler",
                content=scroll,
                size_hint=(0.9, None),
                height=250,
                auto_dismiss=True
            )

        self.suggest_layout.clear_widgets()

        for p in products:
            btn = Button(
                text=f"{p['name']} | {p['code']} | Stok: {p['quantity']}",
                size_hint_y=None,
                height=40,
                halign="left"
            )
            btn.bind(on_release=lambda x, pid=p["id"]: self.select_suggestion(pid))
            self.suggest_layout.add_widget(btn)

        self.suggest_popup.open()

    def select_suggestion(self, product_id):
        self.close_suggestions()
        self.search.text = ""
        self.open_product(product_id)

    def close_suggestions(self):
        if self.suggest_popup:
            self.suggest_popup.dismiss()
            self.suggest_popup = None
            self.suggest_layout = None


    # ---------- INIT ----------

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        top_bar = BoxLayout(size_hint_y=None, height=40)

        sort_btn = Button(
            text="⇅",
            size_hint_x=None,
            width=50
        )
        sort_btn.bind(on_release=self.open_sort_menu)

        root.add_widget(top_bar)

        self.search = TextInput(
            hint_text="Ürün ara (kod / isim)",
            size_hint_y=None,
            height=40,
            multiline=False
        )


        # 🔴 ÖNCE TANIM, SONRA BIND
        self.search.bind(text=self.refresh)
        self.search.bind(text=self.on_search_text)

        root.add_widget(self.search)

        self.suggest_popup = None
        self.suggest_layout = None

        scroll = ScrollView()
        self.layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter("height"))
        scroll.add_widget(self.layout)

        root.add_widget(scroll)

        root.add_widget(Button(
            text="➕ Yeni Ürün",
            size_hint_y=None,
            height=50,
            on_release=lambda x: setattr(self.manager, "current", "add")
        ))

        self.add_widget(root)

class AddProductScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )

        self.code = TextInput(hint_text="Ürün Kodu")
        self.product_name = TextInput(hint_text="Ürün Adı")
        self.category = TextInput(hint_text="Kategori")
        self.qty = TextInput(
            hint_text="Başlangıç Adedi",
            input_filter="int"
        )
        self.location = TextInput(hint_text="Lokasyon")
        self.note = TextInput(hint_text="Not")

        save_btn = Button(
            text="💾 Kaydet",
            size_hint_y=None,
            height=45
        )
        save_btn.bind(on_release=self.save)

        back_btn = Button(
            text="⬅ Geri",
            size_hint_y=None,
            height=45
        )
        back_btn.bind(
            on_release=lambda x: setattr(self.manager, "current", "list")
        )

        layout.add_widget(self.code)
        layout.add_widget(self.product_name)
        layout.add_widget(self.category)
        layout.add_widget(self.qty)
        layout.add_widget(self.location)
        layout.add_widget(self.note)
        layout.add_widget(save_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    # 🔹 EKRAN AÇILMADAN HEMEN ÖNCE ÇAĞRILIR
    def on_pre_enter(self):
        self.clear_form()

    # 🔹 FORM TEMİZLEME
    def clear_form(self):
        self.code.text = ""
        self.product_name.text = ""
        self.category.text = ""
        self.qty.text = ""
        self.location.text = ""
        self.note.text = ""

    def save(self, *args):
        code = self.code.text.strip()
        name = self.product_name.text.strip()
        qty_text = self.qty.text.strip()

        if not code or not name or not qty_text:
            self.show_error("Kod, ad ve adet zorunludur")
            return

        try:
            qty = int(qty_text)
            if qty <= 0:
                raise ValueError
        except ValueError:
            self.show_error("Adet pozitif sayı olmalı")
            return

        try:
            product_id = db.add_product(
                code=code,
                name=name,
                category=self.category.text.strip(),
                quantity=qty,
                location=self.location.text.strip(),
                note=self.note.text.strip(),
                expiry_date=None
            )

            # 🔥 İlk stok hareketi
            db.add_movement(
                product_id=product_id,
                mtype="IN",
                amount=qty,
                description="İlk stok"
            )

            self.manager.current = "list"

        except Exception as e:
            self.show_error(str(e))

    def show_error(self, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label

        Popup(
            title="Hata",
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        ).open()


from kivy.uix.screenmanager import Screen


class ProductDetailScreen(Screen):
    product_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.button import Button

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        # 🔝 ÜST BAR
        top_bar = BoxLayout(size_hint_y=None, height=40, spacing=10)

        btn_back = Button(text="← Geri")
        btn_back.bind(on_release=self.go_back)

        btn_moves = Button(text="Hareketler")
        btn_moves.bind(on_release=self.open_movements)

        top_bar.add_widget(btn_back)
        top_bar.add_widget(btn_moves)
        root.add_widget(top_bar)

        # 📜 SCROLL ALANI
        self.content = BoxLayout(
            orientation="vertical",
            spacing=6,
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.content)

        root.add_widget(scroll)
        self.add_widget(root)

    # 🔙 GERİ
    def go_back(self, *args):
        self.manager.current = "list"

    # 🔁 HAREKETLER
    def open_movements(self, *args):
        self.manager.current = "movements"
        self.manager.get_screen("movements").load(self.product_id)

    # 📦 LOAD
    def load_product(self, product_id):
        self.product_id = product_id
        self.refresh()

    # 🔄 REFRESH
    def refresh(self):
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from datetime import datetime
        import db

        self.content.clear_widgets()

        product = db.get_product(self.product_id)
        if not product:
            return

        # BAŞLIK
        self.content.add_widget(Label(
            text="Ürün Detayı",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=40
        ))

        # ÜRÜN ADI
        self.content.add_widget(Label(
            text=product["name"],
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=35
        ))

        # ✏️ DÜZENLE (FREE)
        edit_btn = Button(
            text="✏️ Düzenle",
            size_hint_y=None,
            height=45
        )
        edit_btn.bind(on_release=self.edit_product)
        self.content.add_widget(edit_btn)

        # STOK
        self.content.add_widget(Label(
            text=f"Mevcut stok: {product['quantity']}",
            size_hint_y=None,
            height=30
        ))

        # NOT
        if product["note"]:
            self.content.add_widget(Label(
                text=f"Not: {product['note']}",
                size_hint_y=None,
                height=30
            ))

        # İLK EKLEME TARİHİ
        created = datetime.fromisoformat(product["created_at"])
        created_str = created.strftime("%d.%m.%Y %H:%M")

        self.content.add_widget(Label(
            text=f"İlk ekleme: {created_str}",
            size_hint_y=None,
            height=30,
            font_size=14,
            color=(0.7, 0.7, 0.7, 1)
        ))

        # SON KULLANMA TARİHİ (OPSİYONEL)
        if product["expiry_date"]:
            self.content.add_widget(Label(
                text=f"Son kullanma: {product['expiry_date']}",
                size_hint_y=None,
                height=30,
                font_size=14,
                color=(0.9, 0.5, 0.3, 1)
            ))

    # ✏️ EDIT ACTION
    def edit_product(self, *args):
        edit_screen = self.manager.get_screen("product_edit")
        edit_screen.load(self.product_id)
        self.manager.current = "product_edit"


class MovementScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.button import Button

        self.product_id = None

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        # 🔝 ÜST BAR
        top_bar = BoxLayout(size_hint_y=None, height=40, spacing=10)

        btn_back = Button(text="← Geri")
        btn_back.bind(on_release=self.go_back)

        top_bar.add_widget(btn_back)
        root.add_widget(top_bar)   # 🔥 EKSİK OLAN SATIR BU

        # 📜 SCROLL ALANI
        self.layout = BoxLayout(
            orientation="vertical",
            spacing=6,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.layout)

        root.add_widget(scroll)
        self.add_widget(root)

    def go_back(self, *args):
        self.manager.current = "detail"

    def load(self, product_id):
        self.product_id = product_id
        self.refresh()

    def toggle_date_order(self, *args):
        if self.date_order == "DESC":
            self.date_order = "ASC"
        else:
            self.date_order = "DESC"

        self.refresh()

    def refresh(self):
        from kivy.uix.label import Label
        from datetime import datetime
        import db

        self.layout.clear_widgets()

        if not self.product_id:
            return

        moves = db.get_movements(self.product_id)

        if not moves:
            self.layout.add_widget(Label(
                text="Hareket bulunamadı",
                size_hint_y=None,
                height=30
            ))
            return

        for m in moves:
            dt = datetime.fromisoformat(m["date"])
            date_str = dt.strftime("%d.%m.%Y %H:%M")

            sign = "+" if m["type"] == "IN" else "-"
            color = (0, 0.7, 0, 1) if m["type"] == "IN" else (0.8, 0, 0, 1)

            self.layout.add_widget(Label(
                text=f"{date_str}   {sign}{m['amount']}   {m['description'] or ''}",
                size_hint_y=None,
                height=30,
                color=color
            ))

class ProductEditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.product_id = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # 🔙 GERİ BUTONU
        back_btn = Button(
            text="← Geri",
            size_hint_y=None,
            height=40
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)

        # 📝 BAŞLIK
        self.title = Label(
            text="Ürün Düzenle",
            font_size=20,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.title)

        self.add_widget(layout)

    def load(self, product_id):
        self.product_id = product_id

    from kivy.app import App

    def go_back(self, *args):
        app = App.get_running_app()
        app.root.current = "list"


# -------------------- APP --------------------


class StockApp(App):
    def build(self):
        import db
        db.init_settings()
        db.init_db()

        sm = ScreenManager(
            transition=SlideTransition()
        )

        sm.add_widget(ProductListScreen(name="list"))
        sm.add_widget(AddProductScreen(name="add"))

        # 📦 Ürün Detay
        sm.add_widget(ProductDetailScreen(name="detail"))

        # 🔁 Hareketler
        sm.add_widget(MovementScreen(name="movements"))

        # ✏️ Ürün Düzenle
        sm.add_widget(ProductEditScreen(name="product_edit"))

        return sm


if __name__ == "__main__":
    StockApp().run()

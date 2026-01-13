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

    def on_enter(self):
        self.refresh()

    def refresh(self, *args):
        self.layout.clear_widgets()

        search_text = self.search.text.strip()
        products = db.get_products(search_text if search_text else None)

        for p in products:
            btn = Button(
                text=f"{p['name']} ({p['quantity']})",
                size_hint_y=None,
                height=50
            )
            btn.bind(on_release=lambda x, pid=p["id"]: self.open_product(pid))
            self.layout.add_widget(btn)

    def open_product(self, product_id):
        self.close_suggestions()
        self.manager.current = "detail"
        self.manager.get_screen("detail").load_product(product_id)

    def open_sort_menu(self, instance):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        import db

        box = BoxLayout(orientation="vertical", spacing=5, padding=5)

        popup = Popup(
            title="Sıralama",
            content=box,
            size_hint=(0.8, 0.5)
        )

        Button(text="Tarih (Yeni → Eski)",
           on_release=lambda x: self.set_sort("date_desc", popup)
        ).add_widget = box.add_widget

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
        import db
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

        top_bar.add_widget(sort_btn)
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
        back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "list"))

        layout.add_widget(self.code)
        layout.add_widget(self.product_name)
        layout.add_widget(self.category)
        layout.add_widget(self.qty)
        layout.add_widget(self.location)
        layout.add_widget(self.note)
        layout.add_widget(save_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

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
            db.add_product(
                code=code,
                name=name,
                category=self.category.text.strip(),
                quantity=qty,
                location=self.location.text.strip(),
                note=self.note.text.strip(),
                expiry_date=None
            )
        except Exception as e:
            self.show_error(str(e))
            return

        # Temizle
        self.code.text = ""
        self.product_name.text = ""
        self.category.text = ""
        self.qty.text = ""
        self.location.text = ""
        self.note.text = ""

        self.manager.current = "list"

    def show_error(self, msg):
        from kivy.uix.popup import Popup
        Popup(
            title="Hata",
            content=Label(text=msg),
            size_hint=(0.8, 0.3)
        ).open()



class ProductDetailScreen(Screen):
    product_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.scrollview import ScrollView

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )

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

    def load_product(self, product_id):
        self.product_id = product_id
        self.refresh()

    def refresh(self):
        from datetime import datetime
        from kivy.uix.label import Label
        import db

        self.layout.clear_widgets()

        product = db.get_product(self.product_id)
        if not product:
            return

        # Ürün adı
        self.layout.add_widget(Label(
            text=product["name"],
            font_size=20,
            size_hint_y=None,
            height=40
        ))

        # İlk ekleme tarihi
        if product["created_at"]:
            created = datetime.fromisoformat(product["created_at"])
            created_str = created.strftime("%d.%m.%Y %H:%M")

            self.layout.add_widget(Label(
                text=f"İlk ekleme: {created_str}",
                size_hint_y=None,
                height=30,
                font_size=14,
                color=(0.7, 0.7, 0.7, 1)
            ))

        # Son kullanma tarihi (opsiyonel)
        if "expiry_date" in product.keys() and product["expiry_date"]:
            self.layout.add_widget(Label(
                text=f"Son kullanma: {product['expiry_date']}",
                size_hint_y=None,
                height=30,
                font_size=14,
                color=(0.9, 0.5, 0.3, 1)
            ))

        # Stok bilgisi
        self.layout.add_widget(Label(
            text=f"Mevcut Stok: {product['quantity']}",
            size_hint_y=None,
            height=30
        ))

        # Not
        if product["note"]:
            self.layout.add_widget(Label(
                text=f"Not: {product['note']}",
                size_hint_y=None,
                height=40,
                font_size=14
            ))


class MovementScreen(Screen):

    def load(self, product_id):
        self.product_id = product_id
        self.refresh()

    def refresh(self):
        from datetime import datetime

        self.layout.clear_widgets()
        moves = db.get_movements(self.product_id)

        for m in moves:
            color = (0, 0.7, 0, 1) if m["type"] == "IN" else (0.8, 0, 0, 1)
            sign = "+" if m["type"] == "IN" else "-"

            dt = datetime.fromisoformat(m["date"])
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")

            lbl = Label(
                text=f"{formatted_date}   {sign}{m['amount']}   {m['description'] or ''}",
                color=color,
                size_hint_y=None,
                height=35,
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.layout.add_widget(lbl)

        self.layout.add_widget(Button(
            text="⬅ Geri",
            size_hint_y=None,
            height=45,
            on_release=lambda x: setattr(self.manager, "current", "detail")
        ))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=5
        )

        scroll = ScrollView()
        self.layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter("height"))
        scroll.add_widget(self.layout)

        root.add_widget(scroll)
        self.add_widget(root)


# -------------------- APP --------------------

class StockApp(App):
    def build(self):
        import db
        db.init_settings()

        # Veritabanını başlat
        db.init_db()

        # Screen manager
        sm = ScreenManager(
            transition=SlideTransition()
        )

        # Ekranlar (sıra önemli değil ama hepsi yukarıda tanımlı olmalı)
        sm.add_widget(ProductListScreen(name="list"))
        sm.add_widget(AddProductScreen(name="add"))
        sm.add_widget(ProductDetailScreen(name="detail"))
        sm.add_widget(MovementScreen(name="movements"))

        return sm


if __name__ == "__main__":
    StockApp().run()

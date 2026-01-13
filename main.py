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
            btn.bind(
                on_release=lambda x, pid=p["id"]: self.open_product(pid)
            )
            self.layout.add_widget(btn)

    def open_product(self, product_id):
        self.manager.current = "detail"
        self.manager.get_screen("detail").load_product(product_id)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        self.search = TextInput(
            hint_text="Ürün ara (kod / isim)",
            size_hint_y=None,
            height=40
        )
        self.search.bind(text=self.refresh)
        root.add_widget(self.search)

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

        root.add_widget(Button(
            text="➕ Yeni Ürün",
            size_hint_y=None,
            height=50,
            on_release=lambda x: setattr(self.manager, "current", "add")
        ))

        self.add_widget(root)


class AddProductScreen(Screen):

    def save(self, *args):
        code = self.code.text.strip()
        name = self.product_name.text.strip()
        qty_text = self.qty.text.strip()

        if not code:
            self.show_error("Ürün kodu boş olamaz")
            return

        if not name:
            self.show_error("Ürün adı boş olamaz")
            return

        if not qty_text:
            self.show_error("Adet boş olamaz")
            return

        try:
            quantity = int(qty_text)
        except ValueError:
            self.show_error("Adet sayı olmalıdır")
            return

        if quantity <= 0:
            self.show_error("Adet 0'dan büyük olmalıdır")
            return

        try:
            db.add_product(
                code=code,
                name=name,
                category=self.category.text.strip() or None,
                quantity=quantity,
                location=self.location.text.strip() or None,
                note=self.note.text.strip() or None
            )
        except Exception as e:
            self.show_error(str(e))
            return

        self.manager.current = "list"

    def show_error(self, msg):
        from kivy.uix.popup import Popup
        Popup(
            title="Hata",
            content=Label(text=msg),
            size_hint=(0.8, 0.3)
        ).open()

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
        self.qty = TextInput(hint_text="Başlangıç Adedi", input_filter="int")
        self.location = TextInput(hint_text="Lokasyon")
        self.note = TextInput(hint_text="Not")

        for w in [
            self.code,
            self.product_name,
            self.category,
            self.qty,
            self.location,
            self.note
        ]:
            layout.add_widget(w)

        layout.add_widget(Button(text="💾 Kaydet", on_release=self.save))
        layout.add_widget(Button(
            text="⬅ Geri",
            on_release=lambda x: setattr(self.manager, "current", "list")
        ))

        self.add_widget(layout)


class ProductDetailScreen(Screen):
    product_id = None

    def load_product(self, product_id):
        self.product_id = product_id
        self.refresh()

    def refresh(self):
        self.layout.clear_widgets()
        p = db.get_product(self.product_id)

        # --- ÜRÜN BİLGİLERİ ---
        self.layout.add_widget(Label(
            text=f"[b]{p['name']}[/b]",
            markup=True,
            font_size="20sp",
            size_hint_y=None,
            height=40
        ))
        self.layout.add_widget(Label(text=f"Kod: {p['code']}", size_hint_y=None, height=30))
        self.layout.add_widget(Label(text=f"Stok: {p['quantity']}", size_hint_y=None, height=30))
        self.layout.add_widget(Label(text=f"Lokasyon: {p['location'] or '-'}", size_hint_y=None, height=30))
        self.layout.add_widget(Label(text=f"Not: {p['note'] or '-'}", size_hint_y=None, height=30))

        # --- ADET GİRİŞİ ---
        self.amount = TextInput(
            hint_text="Adet",
            input_filter="int",
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.amount)

        # --- BUTONLAR ---
        self.layout.add_widget(Button(
            text="➕ Stok Girişi",
            size_hint_y=None,
            height=45,
            on_release=lambda x: self.move("IN")
        ))

        self.layout.add_widget(Button(
            text="➖ Stok Çıkışı",
            size_hint_y=None,
            height=45,
            on_release=lambda x: self.move("OUT")
        ))

        self.layout.add_widget(Button(
            text="📜 Hareketler",
            size_hint_y=None,
            height=45,
            on_release=lambda x: self.open_movements()
        ))

        self.layout.add_widget(Button(
            text="🗑️ Ürünü Sil",
            size_hint_y=None,
            height=45,
            on_release=lambda x: self.confirm_delete()
        ))

        self.layout.add_widget(Button(
            text="⬅ Geri",
            size_hint_y=None,
            height=45,
            on_release=lambda x: setattr(self.manager, "current", "list")
        ))

    # ------------------ STOK HAREKETİ ------------------

    def move(self, t):
        text = self.amount.text.strip()

        if not text:
            self.show_error("Adet boş olamaz")
            return

        try:
            amount = int(text)
        except ValueError:
            self.show_error("Geçerli bir sayı girin")
            return

        if amount <= 0:
            self.show_error("Adet 0'dan büyük olmalı")
            return

        try:
            if t == "IN":
                db.stock_in(self.product_id, amount)
            else:
                db.stock_out(self.product_id, amount)
        except Exception as e:
            self.show_error(str(e))
            return

        self.amount.text = ""
        self.refresh()

    # ------------------ HAREKETLER ------------------

    def open_movements(self):
        scr = self.manager.get_screen("movements")
        scr.load(self.product_id)
        self.manager.current = "movements"

    # ------------------ SİLME ------------------

    def confirm_delete(self):
        from kivy.uix.popup import Popup

        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(Label(text="Bu ürünü silmek istiyor musunuz?"))

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_yes = Button(text="Evet")
        btn_no = Button(text="Hayır")

        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        box.add_widget(btns)

        popup = Popup(
            title="Onay",
            content=box,
            size_hint=(0.8, 0.4)
        )

        btn_yes.bind(on_release=lambda x: self.delete_product(popup))
        btn_no.bind(on_release=lambda x: popup.dismiss())

        popup.open()

    def delete_product(self, popup):
        try:
            db.delete_product(self.product_id)
        except Exception as e:
            popup.dismiss()
            self.show_error(str(e))
            return

        popup.dismiss()
        self.manager.current = "list"

    # ------------------ HATA ------------------

    def show_error(self, msg):
        from kivy.uix.popup import Popup
        Popup(
            title="Hata",
            content=Label(text=msg),
            size_hint=(0.8, 0.3)
        ).open()

    # ------------------ INIT ------------------

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )
        self.add_widget(self.layout)


class MovementScreen(Screen):
    def load(self, product_id):
        self.layout.clear_widgets()
        moves = db.get_movements(product_id)

        for m in moves:
            self.layout.add_widget(Label(
                text=f"{m['date']} | {m['type']} | {m['amount']}"
            ))

        self.layout.add_widget(Button(
            text="⬅ Geri",
            size_hint_y=None,
            height=50,
            on_release=lambda x: setattr(self.manager, "current", "detail")
        ))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        self.layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        scroll.add_widget(self.layout)
        self.add_widget(scroll)


# -------------------- APP --------------------

class StockApp(App):
    def build(self):
        db.init_db()

        sm = ScreenManager(transition=SlideTransition())

        sm.add_widget(ProductListScreen(name="list"))
        sm.add_widget(AddProductScreen(name="add"))
        sm.add_widget(ProductDetailScreen(name="detail"))
        sm.add_widget(MovementScreen(name="movements"))

        return sm


if __name__ == "__main__":
    StockApp().run()

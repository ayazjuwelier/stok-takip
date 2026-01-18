from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle


class ProductCard(BoxLayout):
    def __init__(self, product, on_open, **kwargs):
        super().__init__(
            orientation="horizontal",
            padding=14,
            spacing=10,
            size_hint_y=None,
            height=76,
            **kwargs
        )

        self.product = product
        self.on_open = on_open

        # 🎨 Arka plan
        with self.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            self.bg = RoundedRectangle(
                radius=[16],
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

        # 📦 SOL: isim + kod
        left = BoxLayout(orientation="vertical", spacing=4)

        name_lbl = Label(
            text=product["name"],
            font_size=16,
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=26
        )
        name_lbl.bind(size=lambda i, v: setattr(i, "text_size", i.size))

        code_lbl = Label(
            text=f"Kod: {product['code']}",
            font_size=12,
            color=(0.7, 0.7, 0.7, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=18
        )
        code_lbl.bind(size=lambda i, v: setattr(i, "text_size", i.size))

        left.add_widget(name_lbl)
        left.add_widget(code_lbl)

        # 📊 SAĞ: stok
        stock_lbl = Label(
            text=str(product["quantity"]),
            size_hint=(None, None),
            size=(56, 32),
            font_size=16,
            bold=True,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        stock_lbl.bind(size=stock_lbl.setter("text_size"))

        with stock_lbl.canvas.before:
            Color(0.22, 0.22, 0.22, 1)
            self.stock_bg = RoundedRectangle(
                radius=[16],
                pos=stock_lbl.pos,
                size=stock_lbl.size
            )

        stock_lbl.bind(
            pos=lambda i, v: setattr(self.stock_bg, "pos", i.pos),
            size=lambda i, v: setattr(self.stock_bg, "size", i.size)
        )

        self.add_widget(left)
        self.add_widget(stock_lbl)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_open(self.product["id"])
            return True
        return super().on_touch_down(touch)

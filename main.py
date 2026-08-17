import json
import os
import threading
from time import strftime
from urllib.request import urlopen, Request

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Ellipse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD = "CSOI2026"
POLL_SECONDS = 0.8
DEFAULT_IP = ""
CAPACITY = 289


def normalize_ip(value):
    value = value.strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "http://" + value
    return value.rstrip("/")


def fetch_data(base_url):
    base = normalize_ip(base_url)
    if not base:
        raise ValueError("IP kosong")
    req = Request(base + "/data", headers={"User-Agent": "CSOI/2.0"})
    with urlopen(req, timeout=2.5) as response:
        return json.loads(response.read().decode("utf-8"))


def val(data, *keys, default="--"):
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return default


def fmt_num(value, digits=1):
    if value in (None, "--"):
        return "--"
    try:
        x = float(value)
        return str(int(x)) if x.is_integer() else f"{x:.{digits}f}"
    except Exception:
        return str(value)


ICON_DIR = os.path.join(BASE_DIR, "icons")


def icon_path(name):
    p = os.path.join(ICON_DIR, name + ".png")
    return p if os.path.exists(p) else None


class IconBadge(Widget):
    """Badge ikon digambar pakai grafis vektor (Ellipse/RoundedRectangle) + gambar
    PNG putih yang diberi warna (tint). Tidak memakai Line sama sekali supaya aman
    di semua perangkat, dan tidak memakai karakter font supaya ikon selalu tampil."""
    def __init__(self, icon=None, text=None, color=(1, 1, 1, 1), style="ring",
                 size_dp=64, ring_width=3, bg=(0.045, 0.065, 0.095, 1), icon_color=None, **kwargs):
        d = dp(size_dp)
        super().__init__(size_hint=(None, None), size=(d, d), **kwargs)
        icon_color = icon_color or color
        self._style = style
        self._d = d
        with self.canvas:
            if style == "ring":
                Color(*color)
                self.outer = Ellipse(pos=self.pos, size=self.size)
                Color(*bg)
                self._inset = dp(ring_width)
                self.inner = Ellipse(pos=(self.x + self._inset, self.y + self._inset),
                                      size=(self.width - 2 * self._inset, self.height - 2 * self._inset))
            elif style == "square":
                Color(*color)
                self.sq = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(size_dp * 0.24)])

        if text is not None:
            self.content = Label(text=text, font_size=dp(size_dp * 0.30), bold=True, color=icon_color,
                                  size=self.size, pos=self.pos, halign="center", valign="middle")
            self.content.text_size = self.size
        else:
            ratio = 0.5 if style == "ring" else (0.56 if style == "square" else 0.9)
            icon_d = d * ratio
            ip = icon_path(icon) if icon else None
            self.content = Image(source=ip, color=icon_color, size_hint=(None, None),
                                  size=(icon_d, icon_d), allow_stretch=True) if ip else Widget(size_hint=(None,None), size=(icon_d, icon_d))
        self.add_widget(self.content)
        self.bind(pos=self._sync)
        self._sync()

    def _sync(self, *_):
        if self._style == "ring":
            self.outer.pos = self.pos
            self.inner.pos = (self.x + self._inset, self.y + self._inset)
        elif self._style == "square":
            self.sq.pos = self.pos
        if isinstance(self.content, Label):
            self.content.pos = self.pos
            self.content.size = self.size
            self.content.text_size = self.size
        else:
            self.content.center = self.center


def icon_row_badge(icon_name, color, size_dp=30, style="square"):
    """Badge kecil untuk baris (status sistem / info kapasitas), rata kiri."""
    wrap = BoxLayout(size_hint_x=None, width=dp(size_dp + 12))
    wrap.add_widget(IconBadge(icon=icon_name, color=color, style=style, size_dp=size_dp))
    return wrap


class RoundedCard(BoxLayout):
    def __init__(self, title, value="--", subtitle="", accent=(0.15, 0.55, 1, 1), icon="", **kwargs):
        super().__init__(orientation="vertical", padding=[dp(10), dp(9)], spacing=dp(2), **kwargs)
        self.size_hint_y = None
        self.height = dp(150)
        self.accent = accent
        with self.canvas.before:
            Color(0.10, 0.14, 0.20, 1)
            self.bg_border = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])
            Color(0.045, 0.065, 0.095, 1)
            self.bg = RoundedRectangle(pos=(self.x+1, self.y+1), size=(self.width-2, self.height-2), radius=[dp(14)])
        self.bind(pos=self._sync, size=self._sync)

        self.add_widget(Label(text=title, font_size=dp(11), bold=True, color=(0.60,0.65,0.72,1),
                               size_hint_y=None, height=dp(18), halign="center"))
        icon_row = BoxLayout(size_hint_y=None, height=dp(46))
        icon_row.add_widget(Widget())
        if icon:
            icon_row.add_widget(IconBadge(icon=icon, color=accent, style="plain", size_dp=40))
        icon_row.add_widget(Widget())
        self.add_widget(icon_row)
        self.value_label = Label(text=value, font_size=dp(24), bold=True, color=(0.96,0.97,1,1), halign="center", valign="middle")
        self.add_widget(self.value_label)
        self.sub_label = Label(text=subtitle, font_size=dp(10), color=(0.55,0.60,0.68,1), size_hint_y=None, height=dp(18), halign="center")
        self.add_widget(self.sub_label)

    def _sync(self, *_):
        self.bg_border.pos = self.pos
        self.bg_border.size = self.size
        self.bg.pos = (self.x+1, self.y+1)
        self.bg.size = (self.width-2, self.height-2)


class ClickCard(Button):
    def __init__(self, title, value, subtitle, accent=(0.15,0.55,1,1), icon="", ring_value=False, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0,0,0,0)
        self.size_hint_y = None
        self.height = dp(150)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.accent = accent
        self.icon = icon
        with self.canvas.before:
            Color(0.10,0.14,0.20,1)
            self.bg_border = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])
            Color(0.045,0.065,0.095,1)
            self.bg = RoundedRectangle(pos=(self.x+1, self.y+1), size=(self.width-2, self.height-2), radius=[dp(14)])

        self.col = BoxLayout(orientation="vertical", padding=[dp(6),dp(9)], spacing=dp(2),
                              size_hint=(None, None))
        self.col.add_widget(Label(text=title, font_size=dp(11), bold=True, color=(0.60,0.65,0.72,1),
                                   size_hint_y=None, height=dp(18), halign="center"))
        badge_row = BoxLayout(size_hint_y=None, height=dp(66))
        badge_row.add_widget(Widget())
        if ring_value:
            self.badge = IconBadge(text=value, color=accent, style="ring", size_dp=66)
        else:
            self.badge = IconBadge(icon=icon, color=accent, style="ring", size_dp=66)
        badge_row.add_widget(self.badge)
        badge_row.add_widget(Widget())
        self.col.add_widget(badge_row)
        if ring_value:
            self.value_label = self.badge.content
            self.col.add_widget(Widget(size_hint_y=None, height=dp(2)))
        else:
            self.value_label = Label(text=value, font_size=dp(22), bold=True, color=(0.96,0.97,1,1),
                                      size_hint_y=None, height=dp(28), halign="center")
            self.col.add_widget(self.value_label)
        self.col.add_widget(Label(text=subtitle, font_size=dp(9.5), color=(0.55,0.60,0.68,1),
                                   size_hint_y=None, height=dp(16), halign="center"))
        self.add_widget(self.col)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.bg_border.pos=self.pos; self.bg_border.size=self.size
        self.bg.pos=(self.x+1, self.y+1); self.bg.size=(self.width-2, self.height-2)
        self.col.pos = self.pos
        self.col.size = self.size


class SplashScreen(Screen):
    progress = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=[dp(30),dp(65),dp(30),dp(45)], spacing=dp(12))
        root.add_widget(Widget())
        self.logo = Image(source=os.path.join(BASE_DIR, "csoi_logo.png"), size_hint_y=None, height=dp(155), opacity=0)
        root.add_widget(self.logo)
        self.tag = Label(text="Commuter Smart Intelligence System", font_size=dp(15), bold=True, color=(0.82,0.85,0.92,1), size_hint_y=None, height=dp(35), opacity=0)
        root.add_widget(self.tag)
        root.add_widget(Widget())
        self.bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        root.add_widget(self.bar)
        self.loading = Label(text="CSOI SYSTEM LOADING...", font_size=dp(12), color=(0.68,0.72,0.80,1), size_hint_y=None, height=dp(28))
        root.add_widget(self.loading)
        self.add_widget(root)

    def on_enter(self, *_):
        self.progress = 0
        self.bar.value = 0
        Animation(opacity=1, duration=.55).start(self.logo)
        Animation(opacity=1, duration=.7).start(self.tag)
        Animation(progress=100, duration=2.6, t="in_out_quad").start(self)
        Clock.schedule_interval(self.animate_bar, 0.04)
        Clock.schedule_once(lambda dt: self.finish(), 2.9)

    def animate_bar(self, dt):
        self.bar.value = self.progress
        if self.progress >= 100:
            return False

    def finish(self):
        self.manager.current = "login"


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=[dp(28),dp(45),dp(28),dp(28)], spacing=dp(12))
        root.add_widget(Widget())
        root.add_widget(Image(source=os.path.join(BASE_DIR, "csoi_logo.png"), size_hint_y=None, height=dp(125)))
        root.add_widget(Label(text="COMMUTER SMART ONBOARD INTELLIGENCE", font_size=dp(12), color=(0.68,0.72,0.80,1), size_hint_y=None, height=dp(32)))
        self.password = TextInput(hint_text="Password CSOI", password=True, multiline=False, size_hint_y=None, height=dp(52), padding=[dp(15),dp(12)])
        root.add_widget(self.password)
        self.msg = Label(text="", color=(1,.25,.25,1), size_hint_y=None, height=dp(28))
        root.add_widget(self.msg)
        btn = Button(text="MASUK", size_hint_y=None, height=dp(54), background_normal="", background_color=(.08,.42,.90,1), bold=True)
        btn.bind(on_release=self.login)
        root.add_widget(btn)
        root.add_widget(Label(text="CSOI V2 • ESP32-S3-CAM", color=(.38,.42,.48,1), font_size=dp(10)))
        root.add_widget(Widget())
        self.add_widget(root)

    def login(self, *_):
        if self.password.text == PASSWORD:
            self.password.text = ""
            self.msg.text = ""
            self.manager.current = "dashboard"
        else:
            self.msg.text = "Password salah"


class StatusDot(Widget):
    """Titik indikator status (online/offline/connecting) - digambar vektor,
    warnanya bisa diubah lewat set_color()."""
    def __init__(self, color=(1,1,1,1), diameter=10, **kwargs):
        d = dp(diameter)
        super().__init__(size_hint=(None, None), size=(d, d), **kwargs)
        with self.canvas:
            self._c = Color(*color)
            self.dot = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._sync)

    def _sync(self, *_):
        self.dot.pos = self.pos

    def set_color(self, color):
        self._c.rgba = color


class NavButton(Button):
    def __init__(self, icon, text, color=(0.55,0.60,0.68,1), **kwargs):
        super().__init__(**kwargs)
        self.text = ""
        self.col = BoxLayout(orientation="vertical", spacing=dp(2), size_hint=(None, None))
        icon_wrap = BoxLayout(size_hint_y=None, height=dp(24))
        icon_wrap.add_widget(Widget())
        icon_wrap.add_widget(IconBadge(icon=icon, color=color, style="plain", size_dp=22))
        icon_wrap.add_widget(Widget())
        self.col.add_widget(icon_wrap)
        self.label = Label(text=text, font_size=dp(10.5), bold=True, color=color,
                            size_hint_y=None, height=dp(16), halign="center")
        self.col.add_widget(self.label)
        self.add_widget(self.col)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.col.pos = self.pos
        self.col.size = self.size


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = DEFAULT_IP
        self.poll_event = None
        self.train_no = "--"
        self.data_visible = False
        self.connected = False
        app = App.get_running_app()
        try:
            self.store_file = os.path.join(app.user_data_dir if app else BASE_DIR, "csoi_settings.json")
        except Exception:
            self.store_file = os.path.join(BASE_DIR, "csoi_settings.json")

        root = BoxLayout(orientation="vertical")
        body = ScrollView(do_scroll_x=False, bar_width=dp(3))
        content = BoxLayout(orientation="vertical", padding=[dp(12),dp(10),dp(12),dp(14)], spacing=dp(9), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        header = BoxLayout(size_hint_y=None, height=dp(57), spacing=dp(8))
        header.add_widget(Label(text="CSOI [color=#2D8CFF]LIVE INDICATOR[/color]", markup=True, font_size=dp(20), bold=True, halign="left", valign="middle"))
        online_wrap = BoxLayout(size_hint_x=None, width=dp(130), spacing=dp(5))
        self.online_dot = StatusDot(color=(1,.3,.3,1), diameter=10)
        dot_pad = BoxLayout(size_hint_x=None, width=dp(14))
        dot_pad.add_widget(self.online_dot)
        online_wrap.add_widget(dot_pad)
        self.online = Label(text="OFFLINE\nESP32-S3-CAM", font_size=dp(11), color=(1,.3,.3,1), halign="left")
        online_wrap.add_widget(self.online)
        header.add_widget(online_wrap)
        content.add_widget(header)
        content.add_widget(Label(text="COMMUTER SMART ONBOARD INTELLIGENCE", color=(.48,.53,.62,1), font_size=dp(10), size_hint_y=None, height=dp(20), halign="left"))

        # Main 3-column area matching the reference dashboard.
        grid1 = GridLayout(cols=3, spacing=dp(7), size_hint_y=None, height=dp(150))
        self.card_pass = ClickCard("PENUMPANG", "--", "TERDETEKSI", (.15,.55,1,1), "people")
        self.card_occ = ClickCard("OKUPANSI", "-- %", "DARI KAPASITAS 289", (.18,.75,.48,1), ring_value=True)
        self.card_status = ClickCard("STATUS", "--", "KEPADATAN", (1,.62,.10,1), "people")
        self.card_pass.bind(on_release=lambda *_: self.show_detail("PENUMPANG", self.card_pass.value_label.text))
        self.card_occ.bind(on_release=lambda *_: self.show_detail("OKUPANSI", self.card_occ.value_label.text))
        self.card_status.bind(on_release=lambda *_: self.show_detail("STATUS", self.card_status.value_label.text))
        for c in (self.card_pass,self.card_occ,self.card_status): grid1.add_widget(c)
        content.add_widget(grid1)

        grid2 = GridLayout(cols=3, spacing=dp(7), size_hint_y=None, height=dp(150))
        self.card_temp = RoundedCard("SUHU", "-- °C", "BME280", (.20,.55,1,1), "thermometer")
        self.card_hum = RoundedCard("KELEMBAPAN", "-- %", "BME280", (.20,.55,1,1), "droplet")
        self.card_press = RoundedCard("TEKANAN", "-- hPa", "BME280", (.58,.25,1,1), "gauge")
        for c in (self.card_temp,self.card_hum,self.card_press): grid2.add_widget(c)
        content.add_widget(grid2)

        # System status panel.
        system_box = BoxLayout(orientation="vertical", padding=[dp(12),dp(8)], spacing=dp(6), size_hint_y=None, height=dp(120))
        with system_box.canvas.before:
            Color(.10,.14,.20,1); system_box_border=RoundedRectangle(pos=system_box.pos,size=system_box.size,radius=[dp(15)])
            Color(.045,.065,.095,1); system_box_bg=RoundedRectangle(pos=(system_box.x+1,system_box.y+1),size=(system_box.width-2,system_box.height-2),radius=[dp(14)])
        def _sync_system_box(w,*a):
            system_box_border.pos=w.pos; system_box_border.size=w.size
            system_box_bg.pos=(w.x+1,w.y+1); system_box_bg.size=(w.width-2,w.height-2)
        system_box.bind(pos=_sync_system_box, size=_sync_system_box)
        system_box.add_widget(Label(text="STATUS SISTEM", font_size=dp(13), bold=True, color=(.9,.92,.96,1), size_hint_y=None, height=dp(22), halign="left"))

        def make_status_item(icon_name, label_text):
            item = BoxLayout(spacing=dp(6), padding=[dp(4),dp(2)])
            item.add_widget(IconBadge(icon=icon_name, color=(.20,.85,.45,1), style="square", size_dp=30))
            txt_col = BoxLayout(orientation="vertical")
            txt_col.add_widget(Label(text=label_text, font_size=dp(10), color=(.62,.66,.72,1), size_hint_y=None, height=dp(16), halign="left"))
            status_lbl = Label(text="--", font_size=dp(11), bold=True, color=(.55,.62,.70,1), size_hint_y=None, height=dp(18), halign="left")
            txt_col.add_widget(status_lbl)
            item.add_widget(txt_col)
            return item, status_lbl

        status_row = BoxLayout(spacing=dp(6), size_hint_y=None, height=dp(56))
        item_kamera, self.sys_kamera = make_status_item("camera", "KAMERA")
        item_bme, self.sys_bme = make_status_item("chip", "BME280")
        item_max, self.sys_max = make_status_item("grid", "MAX7219")
        status_row.add_widget(item_kamera)
        status_row.add_widget(item_bme)
        status_row.add_widget(item_max)
        system_box.add_widget(status_row)
        content.add_widget(system_box)

        # Rollingstock management: replaces train image.
        roll = Button(text="ROLLINGSTOCK MANAGEMENT\nNO KERETA: --\nTap icon untuk membuka", size_hint_y=None, height=dp(80), background_normal="", background_color=(.045,.065,.095,1), bold=False)
        roll.bind(on_release=self.open_train_popup)
        self.roll_button = roll
        content.add_widget(roll)

        # Capacity and last update row.
        info = BoxLayout(size_hint_y=None, height=dp(68), spacing=dp(8), padding=[dp(10),dp(7)])
        with info.canvas.before:
            Color(.10,.14,.20,1); iborder=RoundedRectangle(pos=info.pos,size=info.size,radius=[dp(15)])
            Color(.045,.065,.095,1); ibg=RoundedRectangle(pos=(info.x+1,info.y+1),size=(info.width-2,info.height-2),radius=[dp(14)])
        def _sync_info(w,*a):
            iborder.pos=w.pos; iborder.size=w.size
            ibg.pos=(w.x+1,w.y+1); ibg.size=(w.width-2,w.height-2)
        info.bind(pos=_sync_info, size=_sync_info)

        def make_info_item(icon_name, title_text, value_text, color):
            item = BoxLayout(spacing=dp(8))
            item.add_widget(IconBadge(icon=icon_name, color=color, style="square", size_dp=30))
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=title_text, font_size=dp(10), color=(.55,.60,.68,1), size_hint_y=None, height=dp(16), halign="left"))
            val_lbl = Label(text=value_text, font_size=dp(12), bold=True, color=color, size_hint_y=None, height=dp(18), halign="left")
            col.add_widget(val_lbl)
            item.add_widget(col)
            return item, val_lbl

        item_cap, self.cap_label = make_info_item("train", "KAPASITAS KERETA", "289 PENUMPANG", (.28,.58,1,1))
        item_upd, self.upd_label = make_info_item("clock", "UPDATE TERAKHIR", "--:--:--", (.32,.62,1,1))
        info.add_widget(item_cap)
        info.add_widget(item_upd)
        content.add_widget(info)

        # Hidden connection/data menu, opened by icon/menu only.
        self.live_btn = Button(text="LIVE INDICATOR\nTap untuk menampilkan data", size_hint_y=None, height=dp(62), background_normal="", background_color=(.05,.10,.16,1), bold=True)
        self.live_btn.bind(on_release=self.toggle_data)
        content.add_widget(self.live_btn)
        self.data_box = BoxLayout(orientation="vertical", size_hint_y=None, height=0, opacity=0)
        content.add_widget(self.data_box)

        body.add_widget(content)
        root.add_widget(body)

        nav = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(3), padding=[dp(7),dp(4)])
        home = NavButton("home", "DASHBOARD", color=(.28,.58,1,1))
        home.background_normal = ""; home.background_color = (.05,.14,.24,1)
        settings = NavButton("gear", "PENGATURAN", color=(.55,.60,.68,1))
        settings.background_normal = ""; settings.background_color = (.04,.07,.11,1)
        about = NavButton("info", "ABOUT", color=(.55,.60,.68,1))
        about.background_normal = ""; about.background_color = (.04,.07,.11,1)
        settings.bind(on_release=self.open_settings)
        about.bind(on_release=self.open_about)
        nav.add_widget(home); nav.add_widget(settings); nav.add_widget(about)
        root.add_widget(nav)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.load_settings(), 0)

    def load_settings(self):
        try:
            if os.path.exists(self.store_file):
                with open(self.store_file,"r",encoding="utf-8") as f: d=json.load(f)
                self.train_no=d.get("train_no","--")
                self.base_url=d.get("ip","")
                if self.train_no != "--": self.roll_button.text=f"ROLLINGSTOCK MANAGEMENT\nNO KERETA: {self.train_no}\nTap icon untuk mengubah"
        except Exception:
            pass

    def save_settings(self):
        try:
            with open(self.store_file,"w",encoding="utf-8") as f: json.dump({"train_no":self.train_no,"ip":self.base_url},f)
        except Exception: pass

    def open_train_popup(self, *_):
        box=BoxLayout(orientation="vertical",padding=dp(14),spacing=dp(9))
        box.add_widget(Label(text="ROLLINGSTOCK MANAGEMENT",font_size=dp(18),bold=True,size_hint_y=None,height=dp(35)))
        inp=TextInput(text="" if self.train_no=="--" else self.train_no,hint_text="Contoh: 205JR51",multiline=False,size_hint_y=None,height=dp(50))
        box.add_widget(inp)
        save=Button(text="SIMPAN NO KERETA",size_hint_y=None,height=dp(50),background_normal="",background_color=(.08,.55,.35,1))
        box.add_widget(save)
        pop=Popup(title="CSOI",content=box,size_hint=(.88,.38),separator_color=(.15,.55,1,1))
        save.bind(on_release=lambda *_: self.save_train_popup(inp,pop))
        pop.open()

    def save_train_popup(self, inp, pop):
        v=inp.text.strip().upper()
        if v:
            self.train_no=v; self.roll_button.text=f"ROLLINGSTOCK MANAGEMENT\nNO KERETA: {v}\nTap icon untuk mengubah"; self.save_settings()
        pop.dismiss()

    def open_settings(self, *_):
        box=BoxLayout(orientation="vertical",padding=dp(14),spacing=dp(9))
        box.add_widget(Label(text="PENGATURAN KONEKSI",font_size=dp(18),bold=True,size_hint_y=None,height=dp(35)))
        inp=TextInput(text=self.base_url,hint_text="IP ESP32-S3-CAM, contoh 192.168.x.x",multiline=False,size_hint_y=None,height=dp(50))
        box.add_widget(inp)
        b=Button(text="SIMPAN & HUBUNGKAN",size_hint_y=None,height=dp(50),background_normal="",background_color=(.08,.42,.90,1))
        box.add_widget(b)
        pop=Popup(title="CSOI",content=box,size_hint=(.9,.35),separator_color=(.15,.55,1,1))
        b.bind(on_release=lambda *_: self.save_ip_popup(inp,pop))
        pop.open()

    def save_ip_popup(self,inp,pop):
        self.base_url=inp.text.strip(); self.save_settings(); self.connect(); pop.dismiss()

    def open_about(self, *_):
        Popup(title="ABOUT CSOI",content=Label(text="CSOI\nCommuter Smart Onboard Intelligence\n\nESP32-S3-CAM + BME280 + OLED + MAX7219\nLIVE INDICATOR SYSTEM",font_size=dp(14),halign="center"),size_hint=(.86,.35)).open()

    def show_detail(self,title,value):
        Popup(title=title,content=Label(text=f"{title}\n\n{value}",font_size=dp(26),halign="center"),size_hint=(.72,.30)).open()

    def toggle_data(self,*_):
        self.data_visible=not self.data_visible
        self.data_box.height=dp(170) if self.data_visible else 0
        self.data_box.opacity=1 if self.data_visible else 0
        self.live_btn.text="LIVE INDICATOR\nTap untuk menyembunyikan data" if self.data_visible else "LIVE INDICATOR\nTap untuk menampilkan data"
        if self.data_visible:
            self.connect()

    def on_pre_enter(self,*_):
        if self.poll_event is None: self.poll_event=Clock.schedule_interval(self.poll,POLL_SECONDS)

    def on_leave(self,*_):
        if self.poll_event is not None: self.poll_event.cancel(); self.poll_event=None

    def connect(self,*_):
        if not self.ip_input_value():
            return
        self.online.text="CONNECTING...\nESP32-S3-CAM"; self.online.color=(1,.7,.15,1); self.online_dot.set_color((1,.7,.15,1))
        threading.Thread(target=self._fetch_once,daemon=True).start()

    def ip_input_value(self):
        return self.base_url.strip()

    def poll(self,*_):
        if self.data_visible and self.base_url.strip(): threading.Thread(target=self._fetch_once,daemon=True).start()

    def _fetch_once(self):
        try:
            data=fetch_data(self.base_url)
            Clock.schedule_once(lambda dt,d=data:self.update_ui(d),0)
        except Exception:
            Clock.schedule_once(lambda dt:self.connection_error(),0)

    def update_ui(self,data):
        self.connected=True
        self.online.text="ONLINE\nESP32-S3-CAM"; self.online.color=(.2,1,.45,1); self.online_dot.set_color((.2,1,.45,1))
        p=fmt_num(val(data,"penumpang","passengers","count"),0)
        o=fmt_num(val(data,"okupansi","occupancy","percentage"),1)
        s=str(val(data,"status","density","kepadatan"))
        t=fmt_num(val(data,"suhu","temperature","temp"),1)
        h=fmt_num(val(data,"kelembapan","humidity"),1)
        pr=fmt_num(val(data,"tekanan","pressure","pressure_hpa"),1)
        self.card_pass.value_label.text=p
        self.card_occ.value_label.text=o+"%"
        self.card_status.value_label.text=s
        self.card_temp.value_label.text=t+" °C"
        self.card_hum.value_label.text=h+" %"
        self.card_press.value_label.text=pr+" hPa"
        self.sys_kamera.text="OK"; self.sys_kamera.color=(.35,.95,.55,1)
        self.sys_bme.text="OK"; self.sys_bme.color=(.35,.95,.55,1)
        self.sys_max.text="OK"; self.sys_max.color=(.35,.95,.55,1)
        self.upd_label.text=strftime("%H:%M:%S")

    def connection_error(self):
        self.connected=False
        self.online.text="OFFLINE\nESP32-S3-CAM"; self.online.color=(1,.3,.3,1); self.online_dot.set_color((1,.3,.3,1))
        self.sys_kamera.text="--"; self.sys_kamera.color=(.55,.62,.70,1)
        self.sys_bme.text="--"; self.sys_bme.color=(.55,.62,.70,1)
        self.sys_max.text="--"; self.sys_max.color=(.55,.62,.70,1)


class CSOIApp(App):
    def build(self):
        self.title="CSOI Live Indicator V2"
        try:
            sm=ScreenManager(transition=FadeTransition(duration=.25))
            sm.add_widget(SplashScreen(name="splash"))
            sm.add_widget(LoginScreen(name="login"))
            sm.add_widget(DashboardScreen(name="dashboard"))
            sm.current="splash"
            return sm
        except Exception:
            # Jaring pengaman: kalau ada error saat membuat layar,
            # tampilkan pesan errornya langsung di layar HP (tidak crash diam-diam).
            import traceback
            err_text = traceback.format_exc()
            try:
                with open(os.path.join(BASE_DIR, "csoi_error.log"), "w", encoding="utf-8") as f:
                    f.write(err_text)
            except Exception:
                pass
            box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
            box.add_widget(Label(text="CSOI GAGAL DIMUAT - DETAIL ERROR:", bold=True,
                                  color=(1,.3,.3,1), size_hint_y=None, height=dp(30), font_size=dp(14)))
            scroll = ScrollView(do_scroll_x=False)
            err_label = Label(text=err_text, font_size=dp(11), color=(1,1,1,1),
                               size_hint_y=None, halign="left", valign="top")
            err_label.bind(texture_size=lambda w,*a: setattr(w, "height", w.texture_size[1]))
            err_label.bind(width=lambda w,*a: w.setter("text_size")(w, (w.width, None)))
            scroll.add_widget(err_label)
            box.add_widget(scroll)
            return box


if __name__ == "__main__":
    _app = CSOIApp()
    try:
        _app.run()
    except Exception as exc:
        # Pydroid 3: save a readable crash log.
        # Coba folder data aplikasi dulu (pasti bisa ditulis di Android),
        # baru folder BASE_DIR sebagai cadangan.
        log_dirs = []
        try:
            if _app.user_data_dir:
                log_dirs.append(_app.user_data_dir)
        except Exception:
            pass
        log_dirs.append(BASE_DIR)
        for d in log_dirs:
            try:
                with open(os.path.join(d, "csoi_error.log"), "w", encoding="utf-8") as f:
                    import traceback
                    traceback.print_exc(file=f)
                break
            except Exception:
                continue
        raise

import math
import tkinter as tk
from tkinter import font as tkfont


# ----- Visual theme (ink + mint + coral) -----
C = {
    "bg0": "#07161A",
    "bg1": "#0E2A30",
    "bg2": "#143840",
    "panel": "#0B2228",
    "panel_edge": "#1E4A52",
    "display": "#041014",
    "display_edge": "#2A6B74",
    "mint": "#7EF0D8",
    "mint_dim": "#3A9E8E",
    "coral": "#FF6B4A",
    "coral_hot": "#FF8A70",
    "ink": "#E7F6F4",
    "muted": "#6A9AA0",
    "key": "#164048",
    "key_top": "#1C5560",
    "key_edge": "#0A2A30",
    "func": "#243B42",
    "func_top": "#2F4E56",
    "op": "#1A5C58",
    "op_top": "#227870",
    "op_on": "#7EF0D8",
    "op_on_fg": "#06201C",
}


class Calculator(tk.Tk):
    W, H = 380, 640

    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(320, 540)
        self.configure(bg=C["bg0"])
        self.resizable(True, True)

        # Logic state (unchanged behavior)
        self.expression = ""
        self.current = "0"
        self.operator = None
        self.left = None
        self.reset_next = False

        self.keys = {}          # label -> geometry + meta
        self._pulse = 0.0
        self._press_anim = {}   # label -> remaining frames

        self.expr_font = tkfont.Font(family="Cascadia Mono", size=12)
        self.value_font = tkfont.Font(family="Bahnschrift", size=42, weight="bold")
        self.key_font = tkfont.Font(family="Bahnschrift", size=16, weight="bold")

        self.canvas = tk.Canvas(self, highlightthickness=0, bg=C["bg0"])
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self._bind_keys()

        self.after(40, self._animate)
        self._draw()

    # ---------- input ----------
    def _bind_keys(self):
        mapping = {
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            ".": ".", "+": "+", "-": "-", "*": "*", "/": "/",
            "=": "=", "%": "%",
            "Return": "=", "KP_Enter": "=",
            "Escape": "A/C",
            "BackSpace": "DEL", "Delete": "DEL",
            "KP_Add": "+", "KP_Subtract": "-",
            "KP_Multiply": "*", "KP_Divide": "/",
            "KP_Decimal": ".",
        }

        def handle(event):
            key = event.keysym
            ch = event.char
            if key in mapping:
                self.on_press(mapping[key])
            elif ch in mapping:
                self.on_press(mapping[ch])

        self.bind_all("<Key>", handle)

    def _hit(self, x, y):
        for label, k in self.keys.items():
            if k["x0"] <= x <= k["x1"] and k["y0"] <= y <= k["y1"]:
                return label
        return None

    def _on_click(self, event):
        label = self._hit(event.x, event.y)
        if label:
            self._press_anim[label] = 6
            self.on_press(label)
            self._draw()

    def _on_release(self, _event):
        pass

    def _on_resize(self, _event):
        self._draw()

    # ---------- animation ----------
    def _animate(self):
        self._pulse = (self._pulse + 0.045) % (math.pi * 2)
        dead = []
        for label, frames in self._press_anim.items():
            if frames <= 1:
                dead.append(label)
            else:
                self._press_anim[label] = frames - 1
        for label in dead:
            self._press_anim.pop(label, None)
        self._draw()
        self.after(40, self._animate)

    # ---------- drawing helpers ----------
    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def _hex_lerp(self, c1, c2, t):
        def p(h):
            return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        r1, g1, b1 = p(c1)
        r2, g2, b2 = p(c2)
        return "#%02x%02x%02x" % (
            int(self._lerp(r1, r2, t)),
            int(self._lerp(g1, g2, t)),
            int(self._lerp(b1, b2, t)),
        )

    def _round_rect(self, x0, y0, x1, y1, r, fill, outline="", width=1):
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        pts = [
            x0 + r, y0,
            x1 - r, y0,
            x1, y0,
            x1, y0 + r,
            x1, y1 - r,
            x1, y1,
            x1 - r, y1,
            x0 + r, y1,
            x0, y1,
            x0, y1 - r,
            x0, y0 + r,
            x0, y0,
        ]
        return self.canvas.create_polygon(
            pts, smooth=True, splinesteps=20,
            fill=fill, outline=outline, width=width,
        )

    def _draw_key(self, label, x0, y0, x1, y1, kind):
        pressed = self._press_anim.get(label, 0)
        sink = pressed * 1.2
        y0 += sink
        y1 += sink

        active = self.operator == label
        if kind == "eq":
            fill, top, fg = C["coral"], C["coral_hot"], C["ink"]
            radius = 28
        elif kind == "op":
            if active:
                fill, top, fg = C["op_on"], C["mint"], C["op_on_fg"]
            else:
                fill, top, fg = C["op"], C["op_top"], C["mint"]
            radius = 999  # circle-ish via equal box
        elif kind == "func":
            fill, top, fg = C["func"], C["func_top"], C["ink"]
            radius = 22
        else:
            fill, top, fg = C["key"], C["key_top"], C["ink"]
            radius = 22

        # shadow
        self._round_rect(x0 + 2, y0 + 4, x1 + 2, y1 + 4, radius, C["key_edge"], "")
        # body
        self._round_rect(x0, y0, x1, y1, radius, fill, C["panel_edge"], 1)
        # glossy top band
        mid = y0 + (y1 - y0) * 0.42
        self._round_rect(x0 + 3, y0 + 3, x1 - 3, mid, radius * 0.7, top, "")

        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2 + 2
        show = {"*": "×", "/": "÷", "-": "−", "x2": "x²"}.get(label, label)
        self.canvas.create_text(cx, cy, text=show, fill=fg, font=self.key_font)

        self.keys[label] = {"x0": x0, "y0": y0 - sink, "x1": x1, "y1": y1 - sink, "kind": kind}

    def _draw(self):
        cv = self.canvas
        cv.delete("all")
        self.keys.clear()

        w = max(cv.winfo_width(), self.W)
        h = max(cv.winfo_height(), self.H)

        # Atmospheric gradient bands
        bands = 48
        for i in range(bands):
            t = i / bands
            wave = 0.5 + 0.5 * math.sin(self._pulse + t * 3)
            col = self._hex_lerp(C["bg0"], C["bg2"], t * 0.85 + wave * 0.08)
            y0 = h * i / bands
            y1 = h * (i + 1) / bands + 1
            cv.create_rectangle(0, y0, w, y1, fill=col, outline="")

        # Soft orb lights (atmosphere, not cheap glow spam)
        ox = w * (0.2 + 0.03 * math.sin(self._pulse))
        oy = h * (0.18 + 0.02 * math.cos(self._pulse * 0.7))
        for rad, alpha_t in ((120, 0.18), (80, 0.28), (45, 0.4)):
            col = self._hex_lerp(C["bg1"], C["mint_dim"], alpha_t)
            cv.create_oval(ox - rad, oy - rad, ox + rad, oy + rad, fill=col, outline="")

        ox2 = w * (0.82 + 0.02 * math.cos(self._pulse))
        oy2 = h * (0.72 + 0.02 * math.sin(self._pulse * 0.9))
        for rad, alpha_t in ((100, 0.15), (55, 0.25)):
            col = self._hex_lerp(C["bg1"], C["coral"], alpha_t * 0.55)
            cv.create_oval(ox2 - rad, oy2 - rad, ox2 + rad, oy2 + rad, fill=col, outline="")

        # Outer sculpted body
        m = 18
        self._round_rect(m, m, w - m, h - m, 36, C["panel"], C["panel_edge"], 2)

        # Inner rim
        self._round_rect(m + 8, m + 8, w - m - 8, h - m - 8, 30, C["bg1"], C["display_edge"], 1)

        # Display capsule
        dx0, dy0 = m + 22, m + 36
        dx1, dy1 = w - m - 22, m + 150
        self._round_rect(dx0 + 3, dy0 + 5, dx1 + 3, dy1 + 5, 26, "#02080A", "")
        self._round_rect(dx0, dy0, dx1, dy1, 26, C["display"], C["display_edge"], 2)

        # Scan-line shimmer across display
        shimmer_y = dy0 + 12 + (dy1 - dy0 - 24) * (0.5 + 0.5 * math.sin(self._pulse))
        cv.create_line(dx0 + 16, shimmer_y, dx1 - 16, shimmer_y, fill=C["mint_dim"], width=1)

        cv.create_text(
            dx1 - 22, dy0 + 28,
            text=self.expression or "ready",
            anchor="e",
            fill=C["muted"],
            font=self.expr_font,
        )

        # Adaptive value size
        val = self.current
        size = 42 if len(val) <= 9 else max(20, 42 - (len(val) - 9) * 3)
        self.value_font.configure(size=size)
        cv.create_text(
            dx1 - 22, dy1 - 28,
            text=val,
            anchor="e",
            fill=C["mint"],
            font=self.value_font,
        )

        # Keypad geometry — asymmetric “wow” layout:
        # left 3 cols digits/funcs, right column round operators + tall equals
        pad_l, pad_r = m + 22, w - m - 22
        pad_t, pad_b = dy1 + 22, h - m - 22
        gap = 10

        rows = 5
        cols = 4
        cell_w = (pad_r - pad_l - gap * (cols - 1)) / cols
        cell_h = (pad_b - pad_t - gap * (rows - 1)) / rows

        layout = [
            [("A/C", "func"), ("DEL", "func"), ("%", "func"), ("/", "op")],
            [("7", "num"), ("8", "num"), ("9", "num"), ("*", "op")],
            [("4", "num"), ("5", "num"), ("6", "num"), ("-", "op")],
            [("1", "num"), ("2", "num"), ("3", "num"), ("+", "op")],
            [("0", "num"), (".", "num"), ("x2", "num"), ("=", "eq")],
        ]

        for r, row in enumerate(layout):
            for c, (label, kind) in enumerate(row):
                x0 = pad_l + c * (cell_w + gap)
                y0 = pad_t + r * (cell_h + gap)
                x1 = x0 + cell_w
                y1 = y0 + cell_h

                # Make operators circular by equalizing inset
                if kind == "op":
                    side = min(cell_w, cell_h) - 2
                    cx = (x0 + x1) / 2
                    cy = (y0 + y1) / 2
                    x0, x1 = cx - side / 2, cx + side / 2
                    y0, y1 = cy - side / 2, cy + side / 2

                # Zero stretches slightly wider feel via radius only; keep grid
                self._draw_key(label, x0, y0, x1, y1, kind)

    # ---------- logic (same behavior) ----------
    def _fmt(self, num):
        if abs(num - int(num)) < 1e-12:
            return str(int(num))
        return f"{num:.10g}"

    def _calc(self, left, right, op):
        a, b = float(left), float(right)
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise ZeroDivisionError
            return a / b
        raise ValueError(op)

    def _clear(self):
        self.expression = ""
        self.current = "0"
        self.operator = None
        self.left = None
        self.reset_next = False

    def _error(self):
        self.expression = ""
        self.current = "Error"
        self.operator = None
        self.left = None
        self.reset_next = True

    def _delete_one(self):
        text = self.current
        if text in ("0", "Error", "") or len(text) == 1:
            self.current = "0"
            return
        if text.startswith("-") and len(text) == 2:
            self.current = "0"
            return
        self.current = text[:-1]
        if self.current in ("", "-"):
            self.current = "0"

    def on_press(self, key):
        if self.current == "Error" and key != "A/C":
            self._clear()
            if key == "A/C":
                return

        if key == "A/C":
            self._clear()
            return

        if key == "DEL":
            if self.reset_next and self.operator is not None:
                self.current = self.left if self.left is not None else "0"
                self.left = None
                self.operator = None
                self.expression = ""
                self.reset_next = False
                return
            if self.reset_next:
                self.reset_next = False
                self.expression = ""
            self._delete_one()
            return

        if key == "%":
            try:
                self.current = self._fmt(float(self.current) / 100)
                self.reset_next = True
            except ValueError:
                self._error()
            return

        if key == "x2":
            try:
                self.current = self._fmt(float(self.current) ** 2)
                self.reset_next = True
            except ValueError:
                self._error()
            return

        if key in ("+", "-", "*", "/"):
            if self.left is not None and self.operator is not None and not self.reset_next:
                try:
                    self.current = self._fmt(self._calc(self.left, self.current, self.operator))
                except ZeroDivisionError:
                    self._error()
                    return
            self.left = self.current
            self.operator = key
            self.expression = f"{self.current} {key}"
            self.reset_next = True
            return

        if key == "=":
            if self.operator is None or self.left is None:
                return
            try:
                right = self.current
                result = self._calc(self.left, right, self.operator)
                self.expression = f"{self.left} {self.operator} {right} ="
                self.current = self._fmt(result)
                self.left = None
                self.operator = None
                self.reset_next = True
            except ZeroDivisionError:
                self._error()
            return

        if key == ".":
            if self.reset_next:
                self.current = "0."
                self.reset_next = False
            elif "." not in self.current:
                self.current += "."
            return

        if key in "0123456789":
            if self.reset_next or self.current == "0":
                self.current = key
                self.reset_next = False
            else:
                digits = self.current.replace("-", "").replace(".", "")
                if len(digits) < 14:
                    self.current += key


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()

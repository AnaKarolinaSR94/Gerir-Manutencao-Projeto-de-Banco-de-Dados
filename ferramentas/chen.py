# -*- coding: utf-8 -*-
"""Mini renderizador de DER em notacao Chen/Elmasri -> SVG/PNG."""
import math
import pymupdf


class Chen:
    def __init__(self, W, H, title=""):
        self.W, self.H, self.title = W, H, title
        self.ents, self.rels, self.edges, self.specs, self.attrs = {}, {}, [], [], []
        self.notes = []

    def entity(self, name, x, y, attrs=(), side="top", weak=False, w=None, spread=None, rows=2,
               gap=None, label=None, dist=70, off=0):
        w = w or max(120, 10.5 * len(name) + 30)
        self.ents[name] = dict(x=x, y=y, w=w, h=44, weak=weak, label=label or name)
        self._fan(name, attrs, side, spread, rows, gap, dist, off)

    def rel(self, name, x, y, attrs=(), identifying=False, side="top", spread=None, rows=1,
            gap=None, dist=70, off=0):
        w = max(110, 8.5 * len(name) + 44)
        self.rels[name] = dict(x=x, y=y, w=w, h=54, ident=identifying, label=name)
        self._fan(name, attrs, side, spread, rows, gap, dist, off)

    def _fan(self, owner, attrs, side, spread, rows, gap, dist=70, off=0):
        n = len(attrs)
        if not n:
            return
        o = self.ents.get(owner) or self.rels[owner]
        aw = 7.6 * max(len(a[0]) for a in attrs) + 26
        gap = gap or (aw * 0.62 if rows == 2 else aw + 10)
        spread = spread if spread is not None else gap * (n - 1)
        for i, a in enumerate(attrs):
            t = i / (n - 1) if n > 1 else 0.5
            if side in ("top", "bottom"):
                x = o["x"] + off - spread / 2 + t * spread
                d = dist + (i % rows) * 50
                y = o["y"] - d if side == "top" else o["y"] + d
            else:
                y = o["y"] + off - spread / 2 + t * spread
                d = o["w"] / 2 + (dist - 40) + aw / 2 + (i % rows) * (aw * 0.8)
                x = o["x"] - d if side == "left" else o["x"] + d
            self.attrs.append(dict(owner=owner, name=a[0], kind=a[1] if len(a) > 1 else "", x=x, y=y, w=aw))

    def edge(self, a, b, card="", total=False, via=(), lab_off=(0, 0)):
        self.edges.append(dict(a=a, b=b, card=card, total=total, via=list(via), lo=lab_off))

    def spec(self, sup, cx, cy, subs, kind="d", total=True, label=""):
        self.specs.append(dict(sup=sup, x=cx, y=cy, subs=subs, kind=kind, total=total, label=label))

    def note(self, x, y, text, size=13, anchor="start", weight="normal"):
        self.notes.append((x, y, text, size, anchor, weight))

    def _pos(self, n):
        o = self.ents.get(n) or self.rels.get(n)
        return o["x"], o["y"]

    def _poly(self, pts, total):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        if total:
            return (f'<polyline points="{d}" fill="none" stroke="#000" stroke-width="5"/>'
                    f'<polyline points="{d}" fill="none" stroke="#fff" stroke-width="2.2"/>')
        return f'<polyline points="{d}" fill="none" stroke="#000" stroke-width="1.6"/>'

    def _edge_exit(self, ent, ux, uy):
        dx = abs(ent["w"] / 2 / ux) if abs(ux) > 1e-6 else 1e9
        dy = abs(ent["h"] / 2 / uy) if abs(uy) > 1e-6 else 1e9
        return min(dx, dy)

    def svg(self):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
               f'viewBox="0 0 {self.W} {self.H}" font-family="sans-serif">',
               f'<rect width="{self.W}" height="{self.H}" fill="#fff"/>']
        if self.title:
            out.append(f'<text x="{self.W / 2}" y="34" font-size="22" font-weight="bold" '
                       f'text-anchor="middle">{self.title}</text>')
        # 1) attribute lines
        for a in self.attrs:
            ox, oy = self._pos(a["owner"])
            out.append(f'<line x1="{a["x"]:.1f}" y1="{a["y"]:.1f}" x2="{ox}" y2="{oy}" '
                       f'stroke="#000" stroke-width="1.3"/>')
        # 2) edges entity -- relationship
        for e in self.edges:
            pa, pb = self._pos(e["a"]), self._pos(e["b"])
            pts = [pa] + [tuple(v) for v in e["via"]] + [pb]
            out.append(self._poly(pts, e["total"]))
            if e["card"]:
                (x1, y1), (x2, y2) = pts[0], pts[1]
                L = math.hypot(x2 - x1, y2 - y1) or 1
                ux, uy = (x2 - x1) / L, (y2 - y1) / L
                ent = self.ents[e["a"]]
                dist = self._edge_exit(ent, ux, uy) + 22
                lx = x1 + ux * dist - uy * 13 + e["lo"][0]
                ly = y1 + uy * dist + ux * 13 + e["lo"][1]
                out.append(f'<text x="{lx:.1f}" y="{ly + 5:.1f}" font-size="15" font-weight="bold" '
                           f'text-anchor="middle">{e["card"]}</text>')
        # 3) specializations
        for s in self.specs:
            sx, sy = self._pos(s["sup"])
            out.append(self._poly([(sx, sy), (s["x"], s["y"])], s["total"]))
            if s["label"]:
                out.append(f'<text x="{(sx + s["x"]) / 2 + 10:.1f}" y="{(sy + s["y"]) / 2 + 4:.1f}" '
                           f'font-size="13" font-style="italic">{s["label"]}</text>')
            for sub in s["subs"]:
                bx, by = self._pos(sub)
                out.append(self._poly([(s["x"], s["y"]), (bx, by)], False))
                L = math.hypot(bx - s["x"], by - s["y"]) or 1
                ux, uy = (bx - s["x"]) / L, (by - s["y"]) / L
                ent = self.ents[sub]
                dist = self._edge_exit(ent, ux, uy) + 24
                cx, cy = bx - ux * dist, by - uy * dist
                ang = math.degrees(math.atan2(uy, ux))
                out.append(f'<path d="M -9 -7 A 9 9 0 0 0 9 -7" fill="none" stroke="#000" stroke-width="1.6" '
                           f'transform="translate({cx:.1f},{cy:.1f}) rotate({ang - 90:.1f})"/>')
            out.append(f'<circle cx="{s["x"]}" cy="{s["y"]}" r="15" fill="#fff" stroke="#000" stroke-width="1.6"/>')
            out.append(f'<text x="{s["x"]}" y="{s["y"] + 5}" font-size="15" text-anchor="middle">{s["kind"]}</text>')
        # 4) relationships
        for r in self.rels.values():
            x, y, w, h = r["x"], r["y"], r["w"], r["h"]
            d = f'M {x - w / 2} {y} L {x} {y - h / 2} L {x + w / 2} {y} L {x} {y + h / 2} Z'
            out.append(f'<path d="{d}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
            if r["ident"]:
                w2, h2 = w - 16, h - 10
                d2 = f'M {x - w2 / 2} {y} L {x} {y - h2 / 2} L {x + w2 / 2} {y} L {x} {y + h2 / 2} Z'
                out.append(f'<path d="{d2}" fill="none" stroke="#000" stroke-width="1.6"/>')
            out.append(f'<text x="{x}" y="{y + 5}" font-size="14" text-anchor="middle">{r["label"]}</text>')
        # 5) entities
        for e in self.ents.values():
            x, y, w, h = e["x"], e["y"], e["w"], e["h"]
            out.append(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" fill="#fff" '
                       f'stroke="#000" stroke-width="1.8"/>')
            if e["weak"]:
                out.append(f'<rect x="{x - w / 2 + 5}" y="{y - h / 2 + 5}" width="{w - 10}" height="{h - 10}" '
                           f'fill="none" stroke="#000" stroke-width="1.6"/>')
            out.append(f'<text x="{x}" y="{y + 5}" font-size="15" font-weight="bold" '
                       f'text-anchor="middle">{e["label"]}</text>')
        # 6) attributes
        for a in self.attrs:
            x, y, w, k = a["x"], a["y"], a["w"], a["kind"]
            dash = ' stroke-dasharray="6,4"' if k == "derived" else ""
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w / 2}" ry="18" fill="#fff" '
                       f'stroke="#000" stroke-width="1.4"{dash}/>')
            if k == "multi":
                out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w / 2 - 5}" ry="13" fill="none" '
                           f'stroke="#000" stroke-width="1.4"/>')
            out.append(f'<text x="{x:.1f}" y="{y + 5:.1f}" font-size="13" text-anchor="middle">{a["name"]}</text>')
            tw = 7.0 * len(a["name"])
            if k == "key":
                out.append(f'<line x1="{x - tw / 2:.1f}" y1="{y + 8:.1f}" x2="{x + tw / 2:.1f}" y2="{y + 8:.1f}" '
                           f'stroke="#000" stroke-width="1.3"/>')
            if k == "pkey":
                out.append(f'<line x1="{x - tw / 2:.1f}" y1="{y + 8:.1f}" x2="{x + tw / 2:.1f}" y2="{y + 8:.1f}" '
                           f'stroke="#000" stroke-width="1.3" stroke-dasharray="4,3"/>')
        for (x, y, t, sz, an, wt) in self.notes:
            out.append(f'<text x="{x}" y="{y}" font-size="{sz}" text-anchor="{an}" font-weight="{wt}" '
                       f'fill="#333">{t}</text>')
        out.append('</svg>')
        return "\n".join(out)

    def save(self, path_svg, path_png=None, scale=2):
        open(path_svg, "w", encoding="utf-8").write(self.svg())
        if path_png:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF
            drawing = svg2rlg(path_svg)
            import os
            pdf_path = os.path.join(os.path.dirname(path_svg), os.path.basename(path_png)[:-4] + ".pdf")
            renderPDF.drawToFile(drawing, pdf_path)
            doc = pymupdf.open(pdf_path)
            pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
            pix.save(path_png)

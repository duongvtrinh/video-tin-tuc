#!/usr/bin/env python3
"""Unit test cho bin/meta_check.py + các bản vá liên quan. Chạy: python3 tests/test_meta_check.py"""
import json, re, subprocess, sys, tempfile, unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FACTORY / "bin"))
import meta_check as mc  # noqa: E402


def meta(tid):
    return json.loads((FACTORY / "templates" / tid / "meta.json").read_text(encoding="utf-8"))


class TestInputValue(unittest.TestCase):
    def test_items_maxlength_is_per_line_not_whole_block(self):
        # Hồi quy: ví dụ chuẩn của checklist (73 ký tự cả khối) từng bị preflight chặn oan
        m = meta("checklist")
        ex = m["exampleInputs"]["items"]
        self.assertGreater(len(ex), m["inputs"]["items"]["maxLength"])  # cả khối > 56
        self.assertEqual(mc.check_input_value("items", m["inputs"]["items"], ex), [])

    def test_items_line_too_long_and_too_many(self):
        d = {"type": "string", "maxItems": 3, "maxLength": 10}
        self.assertTrue(mc.check_input_value("items", d, "a\nb\nc\nd"))
        self.assertTrue(mc.check_input_value("items", d, "x" * 11))
        self.assertEqual(mc.check_input_value("items", d, ["a", "b"]), [])

    def test_enum(self):
        d = {"type": "enum", "values": ["up", "down"]}
        self.assertEqual(mc.check_input_value("dir", d, "up"), [])
        self.assertTrue(mc.check_input_value("dir", d, "sideways"))

    def test_numeric_range(self):
        d = {"type": "string", "min": 0, "max": 100, "integer": True}
        for ok in ("0", "55", "100"):
            self.assertEqual(mc.check_input_value("w1", d, ok), [], ok)
        for bad in ("-1", "101", "5.5", "abc"):
            self.assertTrue(mc.check_input_value("w1", d, bad), bad)

    def test_poll_vote_requires_percent_suffix(self):
        d = meta("poll-vote")["inputs"]["pct1"]
        self.assertEqual(mc.check_input_value("pct1", d, "68%"), [])
        self.assertTrue(mc.check_input_value("pct1", d, "68"))   # thiếu % -> width CSS vô hiệu
        self.assertTrue(mc.check_input_value("pct1", d, "101%"))

    def test_empty_is_not_checked_here(self):
        self.assertEqual(mc.check_input_value("x", {"type": "enum", "values": ["a"]}, ""), [])


class TestConstraints(unittest.TestCase):
    def test_share_bar_sum(self):
        m = meta("share-bar")
        good = {"count": "3", "label3": "c", "pct1": "48", "pct2": "32", "pct3": "20"}
        self.assertEqual(mc.check_constraints(m, good), [])
        bad = {"count": "3", "label3": "c", "pct1": "50", "pct2": "32", "pct3": "20"}
        self.assertTrue(mc.check_constraints(m, bad))
        self.assertEqual(mc.check_constraints(m, {**bad, "pct1": "49"}), [])  # ±1

    def test_share_bar_missing_count_uses_default(self):
        m = meta("share-bar")  # default count = 3 -> cần label3/pct3
        errs = mc.check_constraints(m, {"label1": "a", "pct1": "50", "label2": "b", "pct2": "50"})
        self.assertTrue(any("label3" in e or "pct3" in e for e in errs))

    def test_compare_bars_required_when(self):
        m = meta("compare-bars")
        self.assertTrue(mc.check_constraints(m, {"count": "3"}))
        self.assertEqual(mc.check_constraints(m, {"count": "2"}), [])


class TestAllCatalog(unittest.TestCase):
    def test_every_example_passes(self):
        for d in sorted((FACTORY / "templates").iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                m = meta(d.name)
                self.assertEqual(mc.check_all_inputs(m, m["exampleInputs"]), [], d.name)
                for vn, v in (m.get("exampleVariants") or {}).items():
                    self.assertEqual(mc.check_all_inputs(m, v), [], f"{d.name}.{vn}")


class TestEngineFixes(unittest.TestCase):
    def test_accent_violet_and_white(self):
        sys.path.insert(0, str(FACTORY / "bin"))
        import render_template as rt
        self.assertEqual(rt.resolve_accent("typewriter-reveal", {"accent": "violet"}), "#A78BFA")
        self.assertEqual(rt.resolve_accent("typewriter-reveal", {"accent": "white"}), "#FFFFFF")
        self.assertEqual(rt.resolve_accent("typewriter-reveal", {"accent": "nonsense"}),
                         rt.resolve_accent("typewriter-reveal", {}))

    def test_theme_vars(self):
        import render_template as rt
        self.assertIn("--broll-bg:#1C372A", rt.resolve_theme_vars({}))            # mặc định = rêu cũ
        self.assertIn("--broll-bg:#14181F", rt.resolve_theme_vars({"theme": "war"}))
        self.assertIn("--broll-bg:#1C372A", rt.resolve_theme_vars({"theme": "khong-co"}))

    def test_sfx_offset_never_negative_in_render_draft(self):
        src = (FACTORY / "bin" / "render_draft.py").read_text(encoding="utf-8")
        raw = re.findall(r'\(at \+ float\(sfx\.get\("offsetSec", 0\)\)\) \* 1000', src)
        self.assertEqual(raw, [], "còn chỗ at+offsetSec chưa kẹp max(0.0, …)")

    def test_ffmpeg_accepts_zero_but_rejects_negative_adelay(self):
        # Chứng minh gốc rễ: adelay âm làm ffmpeg lỗi; bản vá đưa về 0
        if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
            self.skipTest("không có ffmpeg")
        def run(ms):
            with tempfile.TemporaryDirectory() as t:
                return subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=d=0.3",
                                       "-af", f"adelay={ms}|{ms}", f"{t}/o.wav"], capture_output=True).returncode
        self.assertNotEqual(run(-200), 0)
        at, off = 0.0, -0.2
        self.assertEqual(run(int(max(0.0, at + off) * 1000)), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

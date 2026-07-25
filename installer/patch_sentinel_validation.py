"""Allow dotted permission codes (users.view, customer.manage) in
sentinel-auth's permission-name validator. Idempotent."""
import pathlib
import sys

p = pathlib.Path(sys.argv[1]) / "sentinel" / "validation.py"
if not p.exists():
    print(f"[WARN] {p} not found, skipping patch.")
    sys.exit(0)

text = p.read_text(encoding="utf-8")
old = 'pattern = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")'
new = 'pattern = re.compile(r"^[a-zA-Z0-9_.-]{1,128}$")'
if old in text:
    p.write_text(text.replace(old, new), encoding="utf-8")
    print("[OK] patched validation.py to allow dots in permission names.")
else:
    print("[OK] validation.py already patched (or upstream changed).")

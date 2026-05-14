"""Quick verification that all 5 fixes are in place."""
import pathlib

def check(cond, msg):
    print(("[OK]  " if cond else "[FAIL]"), msg)

print("=" * 55)
print("  VERIFYING ALL BUG FIXES")
print("=" * 55)

# FIX 1 — JWT: /auth/token endpoint added
auth = pathlib.Path("app/routes/auth.py").read_text(encoding="utf-8")
check("OAuth2PasswordRequestForm" in auth,      "Fix 1a: OAuth2PasswordRequestForm imported")
check('"/token"' in auth,                        "Fix 1b: /auth/token endpoint exists")
check("include_in_schema=False" in auth,         "Fix 1c: /auth/token hidden from Swagger docs")
check("form_data.username" in auth,              "Fix 1d: accepts email OR username in username field")

# FIX 1 — JWT: tokenUrl updated in security.py
sec = pathlib.Path("app/core/security.py").read_text(encoding="utf-8")
check("/auth/token" in sec,                      "Fix 1e: tokenUrl points to /auth/token")
check("/auth/login" not in sec,                  "Fix 1f: old tokenUrl /auth/login removed")

# FIX 2 — Cart route ordering
cart = pathlib.Path("app/routes/cart.py").read_text(encoding="utf-8")
clear_pos  = cart.find("def clear_cart")
remove_pos = cart.find("def remove_from_cart")
check(clear_pos < remove_pos,                    "Fix 2:  DELETE / (clear) registered BEFORE DELETE /{item_id}")

# FIX 3 — Frontend mount at /frontend
main = pathlib.Path("app/main.py").read_text(encoding="utf-8")
check('"/frontend"' in main,                     "Fix 3a: Frontend mounted at /frontend (for cover_sheet_test)")
check('"/static"' in main,                       "Fix 3b: Frontend also at /static (backwards compat)")

# FIX 4 — Admin product form: category required
admin_html = pathlib.Path("frontend/admin.html").read_text(encoding="utf-8")
check("Select Category" in admin_html,           "Fix 4a: Category has placeholder (no None option)")
check("Please select a category" in admin_html,  "Fix 4b: JS validation blocks submit without category")
check("disabled selected" in admin_html,         "Fix 4c: Placeholder option is disabled")

# FIX 5 — cart.html uses correct endpoint
cart_html = pathlib.Path("frontend/cart.html").read_text(encoding="utf-8")
check('"/cart/"' in cart_html,                   "Fix 5a: cart.html clearCart uses DELETE /cart/")
check("/cart/clear" not in cart_html,            "Fix 5b: No stale /cart/clear URL in cart.html")

print("=" * 55)
print("  Run tests: python -m pytest tests/ -v")
print("=" * 55)

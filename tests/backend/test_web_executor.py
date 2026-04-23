from app.services.web_executor import _resolve_locator


class _FakeLocator:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


class _FakePage:
    def locator(self, value):
        return _FakeLocator("locator", value)

    def get_by_text(self, value):
        return _FakeLocator("text", value)

    def get_by_test_id(self, value):
        return _FakeLocator("testid", value)

    def get_by_role(self, role, name=None):
        return _FakeLocator("role", (role, name))


def test_resolve_locator_supports_css():
    page = _FakePage()
    locator = _resolve_locator(page, {"locator_type": "css", "locator": "#submit"})
    assert locator.kind == "locator"
    assert locator.value == "#submit"


def test_resolve_locator_supports_xpath():
    page = _FakePage()
    locator = _resolve_locator(page, {"locator_type": "xpath", "locator": "//button[@id='submit']"})
    assert locator.kind == "locator"
    assert locator.value == "xpath=//button[@id='submit']"


def test_resolve_locator_supports_text_and_testid():
    page = _FakePage()
    text_locator = _resolve_locator(page, {"locator_type": "text", "locator": "登录"})
    testid_locator = _resolve_locator(page, {"locator_type": "testid", "locator": "submit-button"})
    assert text_locator.kind == "text"
    assert text_locator.value == "登录"
    assert testid_locator.kind == "testid"
    assert testid_locator.value == "submit-button"


def test_resolve_locator_supports_role_with_optional_name():
    page = _FakePage()
    named = _resolve_locator(page, {"locator_type": "role", "locator": "button|登录"})
    plain = _resolve_locator(page, {"locator_type": "role", "locator": "dialog"})
    assert named.kind == "role"
    assert named.value == ("button", "登录")
    assert plain.value == ("dialog", None)

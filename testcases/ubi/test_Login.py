import pytest
from product.ubi.pages.Login import LoginPage

class TestLogin:
    @pytest.fixture(scope="module")
    def load_page(self, request_session,config):
        # 将 request_session 传入 LoginPage
        yield LoginPage(request_session,config)
    # def test_login_success(self,load_page):
    #     load_page.login_success()
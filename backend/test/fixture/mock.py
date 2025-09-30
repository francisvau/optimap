from typing import Any

import pytest

"""Mailing"""


class MockMailer:
    def __init__(self):
        self.sent: list[dict[str, Any]] = []

    async def send_mail(self, recipients, subject, template, replacements=None):
        self.sent.append(
            dict(to=recipients, subj=subject, tpl=template, repl=replacements)
        )


@pytest.fixture
def mock_mailer():
    return MockMailer()

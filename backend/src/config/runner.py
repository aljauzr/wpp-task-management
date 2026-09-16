# pyrefly: ignore [missing-import]
from django.test.runner import DiscoverRunner


class ProjectTestRunner(DiscoverRunner):
    """
    Ensures that running `python manage.py test` with no arguments
    automatically discovers and runs tests in the `tests/` directory.
    """

    def build_suite(self, test_labels=None, **kwargs):
        if not test_labels:
            test_labels = ['tests']
        return super().build_suite(test_labels=test_labels, **kwargs)

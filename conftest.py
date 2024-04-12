import pytest


############################################################################
# This setup ensures that all tests will have access to the Django database
# without needing to explicitly apply the pytest.mark.django_db marker to
# each individual test function.
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


pytestmark = pytest.mark.django_db

#############################################################################


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client

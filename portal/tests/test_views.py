import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_articles_view_post_empty_selection(client):
    """If no items are selected, should redirect back to articles."""
    session = client.session
    session["order_number"] = "RMA-1001"
    session.save()

    url = reverse("articles", kwargs={"order_number": "RMA-1001"})
    # POST without selected_article
    response = client.post(url, {})

    assert response.status_code == 302
    assert response.url == url
    assert "return_selection" not in client.session


def test_articles_view_post_valid_selection(client):
    """Valid selection should be saved in session and redirect to confirmation."""
    session = client.session
    session["order_number"] = "RMA-1001"
    session.save()

    url = reverse("articles", kwargs={"order_number": "RMA-1001"})
    response = client.post(
        url,
        {
            "selected_article": ["TSHIRT-BLK-M"],
            "qty_TSHIRT-BLK-M": "1",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("return_confirmation", kwargs={"order_number": "RMA-1001"})
    
    saved_selection = client.session.get("return_selection")
    assert saved_selection is not None
    assert len(saved_selection) == 1
    assert {"sku": "TSHIRT-BLK-M", "qty": 1} in saved_selection


def test_confirmation_view_get_missing_session(client):
    """Should redirect to articles if no return selection is active."""
    session = client.session
    session["order_number"] = "RMA-1001"
    session.save()

    url = reverse("return_confirmation", kwargs={"order_number": "RMA-1001"})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse("articles", kwargs={"order_number": "RMA-1001"})


def test_confirmation_view_get_valid(client):
    """Should render the confirmation page with valid items."""
    session = client.session
    session["order_number"] = "RMA-1001"
    session["return_selection"] = [{"sku": "TSHIRT-BLK-M", "qty": 1}]
    session.save()

    url = reverse("return_confirmation", kwargs={"order_number": "RMA-1001"})
    response = client.get(url)

    assert response.status_code == 200
    assert "Confirm Your Return" in response.content.decode()


def test_confirmation_view_post(client):
    """Confirming return should clear session and redirect to success."""
    session = client.session
    session["order_number"] = "RMA-1001"
    session["return_selection"] = [{"sku": "TSHIRT-BLK-M", "qty": 1}]
    session.save()

    url = reverse("return_confirmation", kwargs={"order_number": "RMA-1001"})
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("return_success", kwargs={"order_number": "RMA-1001"})
    
    # Session should be wiped
    assert "return_selection" not in client.session
    assert "order_number" not in client.session


def test_success_view(client):
    """Should render success template."""
    url = reverse("return_success", kwargs={"order_number": "RMA-1001"})
    response = client.get(url)

    assert response.status_code == 200
    assert "Return Created Successfully" in response.content.decode()

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from portal.forms import LookupForm
from portal.services.eligibility import evaluate_eligibility
from portal.services.order_store import find_order, get_order


class LookupView(View):
    """Order lookup page – validates order number + email / zip."""

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "returns/lookup.html", {"form": LookupForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LookupForm(request.POST)
        if form.is_valid():
            order = find_order(
                form.cleaned_data["order_number"],
                form.cleaned_data["identifier"],
            )
            if order is None:
                form.add_error(None, "Order not found or credentials do not match.")
            else:
                request.session["order_number"] = order.order_number
                return redirect("articles", order_number=order.order_number)

        return render(request, "returns/lookup.html", {"form": form})


class ArticlesView(View):
    """Articles page – shows items in the order with eligibility info."""

    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        order = get_order(order_number)
        if order is None:
            return redirect("lookup")

        results = evaluate_eligibility(order)
        article_rows = []
        for i, result in enumerate(results, 1):
            remaining_qty = max(
                result.article.quantity - result.article.quantity_returned,
                0,
            )
            article_rows.append(
                {
                    "id": f"item_{i}",
                    "result": result,
                    "remaining_qty": remaining_qty,
                    "quantity_options": list(range(1, remaining_qty + 1)),
                    "selectable": result.returnable and remaining_qty > 0,
                }
            )

        if request.GET.get("returnable_only") == "true":
            article_rows = [row for row in article_rows if row["selectable"]]

        return render(
            request,
            "returns/articles.html",
            {
                "order": order,
                "results": results,
                "article_rows": article_rows,
            },
        )

    def post(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        selected_skus = request.POST.getlist("selected_article")
        if not selected_skus:
            return redirect("articles", order_number=order_number)

        selection = []
        for sku in selected_skus:
            qty_str = request.POST.get(f"qty_{sku}")
            try:
                qty = int(qty_str) if qty_str else 0
            except ValueError:
                qty = 0
            if qty > 0:
                selection.append({"sku": sku, "qty": qty})

        if not selection:
            return redirect("articles", order_number=order_number)

        request.session["return_selection"] = selection
        return redirect("return_confirmation", order_number=order_number)


class ReturnConfirmationView(View):
    """Confirmation page"""

    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        selection = request.session.get("return_selection")
        if not selection:
            return redirect("articles", order_number=order_number)

        order = get_order(order_number)
        if order is None:
            return redirect("lookup")

        results_by_sku = {r.article.sku: r for r in evaluate_eligibility(order)}
        
        confirm_items = []
        total_refund = 0.0

        for item in selection:
            sku = item["sku"]
            qty = item["qty"]
            result = results_by_sku.get(sku)
            
            if result and result.returnable:
                allowed_qty = max(result.article.quantity - result.article.quantity_returned, 0)
                actual_qty = min(qty, allowed_qty)
                if actual_qty > 0:
                    item_total = actual_qty * result.article.price
                    total_refund += item_total
                    confirm_items.append({
                        "article": result.article,
                        "qty": actual_qty,
                        "item_total": item_total,
                    })

        if not confirm_items:
            return redirect("articles", order_number=order_number)

        return render(
            request,
            "returns/confirmation.html",
            {
                "order": order,
                "confirm_items": confirm_items,
                "total_refund": total_refund,
            },
        )

    def post(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        order = get_order(order_number)
        if order is None:
            return redirect("lookup")
        
        request.session.pop("return_selection", None)
        request.session.pop("order_number", None)

        return redirect("return_success", order_number=order_number)


class ReturnSuccessView(View):
    """Success Page"""
    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        return render(request, "returns/success.html", {"order_number": order_number})


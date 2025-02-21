from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from django.http import HttpResponse

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    context_object_name = "transactions"
    template_name = "index.html"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-created_at')
        search_query = self.request.GET.get('search', '').strip()
        status_filter = self.request.GET.get('status', '')
        flag_filter = self.request.GET.get('flag', 'all')
        # Apply search filter on merchant
        if search_query:
            queryset = queryset.filter(merchant__icontains=search_query)
        # Apply status filter
        if status_filter in dict(Transaction.STATUS_CHOICES):
            queryset = queryset.filter(status=status_filter)
        # Apply flag filter
        if flag_filter != 'all':
            queryset = queryset.filter(is_flagged=flag_filter)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_statuses"] = Transaction.STATUS_CHOICES
        context["search_input"] = self.request.GET.get('search', '')
        context["selected_status"] = self.request.GET.get('status', '')
        context["selected_flag"] = self.request.GET.get('flag', '')
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            return render(self.request, "partials/audit_table.html", context)
        return super().render_to_response(context, **response_kwargs)

def approve_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        if not request.user.is_authenticated or not request.user.is_staff:
            response = HttpResponse(status=403)
            response['HX-Trigger'] = '{"showNotification": {"message": "You must be a staff member to approve transactions."}}'
            return response
        if transaction.status == Transaction.PENDING_STATUS:
            transaction.status = Transaction.COMPLETE_STATUS
            transaction.approved_by = request.user
            transaction.save()
    context = {"transaction": transaction}
    return render(request, "partials/audit_row.html", context)

def fail_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        if not request.user.is_authenticated or not request.user.is_staff:
            response = HttpResponse(status=403)
            response['HX-Trigger'] = '{"showNotification": {"message": "You must be a staff member to fail transactions."}}'
            return response
        if transaction.status == Transaction.PENDING_STATUS:
            transaction.status = Transaction.FAILED_STATUS
            transaction.save()
    context = {"transaction": transaction}
    return render(request, "partials/audit_row.html", context)

def toggle_flag(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        if not request.user.is_authenticated or not request.user.is_staff:
            response = HttpResponse(status=403)
            response['HX-Trigger'] = '{"showNotification": {"message": "You must be a staff member to toggle flags."}}'
            return response
        transaction.is_flagged = not transaction.is_flagged
        transaction.save()
    context = {"transaction": transaction}
    return render(request, "partials/audit_row.html", context)
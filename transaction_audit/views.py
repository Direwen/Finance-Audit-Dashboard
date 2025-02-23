from django.views.generic import ListView, TemplateView, DetailView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from .models import Transaction
from .serializers import TransactionSerializer


# TRANSACTION AUDIT DASHBOARD PAGE
class TransactionListView(LoginRequiredMixin, ListView):
    
    '''Display the dashboard page along with the paginated list of transaction records'''
    
    model = Transaction
    context_object_name = "transactions"
    template_name = "index.html"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        #get search input value
        search_query = self.request.GET.get('search', '').strip()
        #get status filter value
        status_filter = self.request.GET.get('status', '')
        #get flag filter value
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
        #Pass pre-defined statuses
        context["available_statuses"] = Transaction.STATUS_CHOICES
        #Pass searched input, selected status, selected flag
        context["search_input"] = self.request.GET.get('search', '')
        context["selected_status"] = self.request.GET.get('status', '')
        context["selected_flag"] = self.request.GET.get('flag', '')
        return context
    
    def render_to_response(self, context, **response_kwargs):
        #if the request is from htmx, perform partial rendering for table
        if self.request.htmx:
            return render(self.request, "partials/audit_table.html", context)
        return super().render_to_response(context, **response_kwargs)

def approve_transaction(request, pk):
    
    '''To Apporve Transactions'''
    
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        # if the user is not authenticated or a staff
        if not request.user.is_authenticated or not request.user.is_staff:
            #return response error along with the custom header to trigger the notification
            response = HttpResponse(status=403)
            response['HX-Trigger'] = '{"showNotification": {"message": "You must be a staff member to approve transactions."}}'
            return response
        # if transaction is currently pending, it should only allow approval or failure of record status
        if transaction.status == Transaction.PENDING_STATUS:
            transaction.status = Transaction.COMPLETE_STATUS
            transaction.approved_by = request.user
            transaction.save()
    context = {"transaction": transaction}
    return render(request, "partials/audit_row.html", context)

def fail_transaction(request, pk):
    
    '''To Falil Transaction'''
    
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        # if the user is not authenticated or a staff
        if not request.user.is_authenticated or not request.user.is_staff:
            response = HttpResponse(status=403)
            response['HX-Trigger'] = '{"showNotification": {"message": "You must be a staff member to fail transactions."}}'
            return response
        # if transaction is currently pending, it should only allow approval or failure of record status
        if transaction.status == Transaction.PENDING_STATUS:
            transaction.status = Transaction.FAILED_STATUS
            transaction.save()
    context = {"transaction": transaction}
    return render(request, "partials/audit_row.html", context)

def toggle_flag(request, pk):
    
    '''To toggle flagging of the record'''
    
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        # if the user is not authenticated or a staff
        if not request.user.is_authenticated or not request.user.is_staff:
            response = HttpResponse(status=403)
            response['HX-Trigger'] = '{"showNotification": {"message": "You must be a staff member to toggle flags."}}'
            return response
        transaction.is_flagged = not transaction.is_flagged
        transaction.save()
    context = {"transaction": transaction}
    return render(request, "partials/audit_row.html", context)

# History
class TransactionHistoryView(LoginRequiredMixin, DetailView):
    
    '''To view the history records of a certain transaction record using DetailView'''
    
    model = Transaction
    template_name = "history.html"
    context_object_name = "transaction"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history_records"] = self.object.history.all().order_by('-history_date')
        return context

# REPORT PAGE
class TransactionReportView(LoginRequiredMixin, TemplateView):
    
    '''To display reports using TemplateView as it doesn't require model specifically'''
    
    template_name = "report.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Total Amount by Transaction Status
        context['status_totals'] = {
            Transaction.COMPLETE_STATUS : Transaction.objects.filter(status=Transaction.COMPLETE_STATUS).aggregate(total=Sum("amount"))["total"],
            Transaction.FAILED_STATUS : Transaction.objects.filter(status=Transaction.FAILED_STATUS).aggregate(total=Sum("amount"))["total"],
            Transaction.PENDING_STATUS : Transaction.objects.filter(status=Transaction.PENDING_STATUS).aggregate(total=Sum("amount"))["total"]
        }
        #Total Amount by each merchant
        merchant_totals = Transaction.objects.values("merchant").filter(status=Transaction.COMPLETE_STATUS).annotate(total=Sum("amount"))
        context["merchant_totals"] = list(merchant_totals)
        return context
    
#API VIEWSETS
class TransactionViewSet(ListAPIView):
    queryset = Transaction.objects.select_related("approved_by").all()
    serializer_class = TransactionSerializer
    
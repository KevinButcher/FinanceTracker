from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, Category, Month
from .forms import TransactionForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.utils import timezone
from calendar import month_name
from django.contrib import messages

# Create your views here.

@login_required
def home(request):
    current_date = timezone.now() # retrieves current dat
    current_month = current_date.strftime('%B') # pulls the full month name from current_date (ie: November instead of Nov)
    current_year = current_date.year # pulls the current year from the current_date

    # fetch transactions for current month
    current_month_transactions = Transaction.objects.filter(
        # = is used instead of == to specify a condition in django query
        user=request.user, # pulls the current user
        month__month=current_month, # pulls all transactions who's month instace has month field set to current_month
        month__year=current_year # pulls all transactions who's month instance has year field set to current_year
    )

    #fetch transactions for the entire year
    annual_transactions = Transaction.objects.filter(
        user=request.user, # pulls the current user
        month__year = current_year # pulls all transactions who's month instance has year field set to current_year
    )

    # initialize data structures
    current_month_income_data = [] # create an empty list to store all income transactions (list because there is only one income category (salary))
    current_month_expense_data = {} # create an empty dictionary to store all expense transactions (dictionary because there is more than one expense category)
    current_month_total_expenses = 0

    # iterate through current month transactions and seperate into income and expense
    for transaction in current_month_transactions:
        # retrieve current transactions category
        category = transaction.category.category
        # if category is == to salary than add it to income list
        if category.lower() == 'salary':
            current_month_income_data.append(float(transaction.amount))
        # if category is != to salary than check if category exists in dict, add if not, and add expenses to appropriate category
        else:
            # add category to dict as a list if not present
            if category not in current_month_expense_data:
                current_month_expense_data[category] = []
            # add expense to appropriate category list
            current_month_expense_data[category].append(float(transaction.amount))
            # add the amount to total expenses
            current_month_total_expenses += float(transaction.amount)
    
    # prepare data for current month graph
    current_month_labels = [current_month]
    # adds all income entries in the income list
    total_income = sum(current_month_income_data)

    # different colors for expense categories to utilize
    expense_colors = [
        "rgb(255, 159, 64)",   # Orange
        "rgb(255, 205, 86)",   # Yellow
        "rgb(153, 102, 255)",  # Purple
        "rgb(169, 169, 169)",  # Gray
        "rgb(144, 238, 144)"   # Light Green
    ]

    # set up income bar in it's own bar labeled income
    current_month_datasets = [
        {
            "label": "Income",
            "data": [total_income],
            "backgroundColor": "rgb(75, 192, 192)", # Teal
            "borderColor": "rgb(75, 192, 192)",
            "borderWidth": 1,
            "order": 1,
            "stack": "income"
        }
    ]

    # set up expense stacked bar that enumerates through the color options by category
    for idx, (category, data) in enumerate(current_month_expense_data.items()):
        current_month_datasets.append({
            "label": category,
            "data": data,
            "backgroundColor": expense_colors[idx % len(expense_colors)],  # Cycle through the colors
            "borderColor": expense_colors[idx % len(expense_colors)],  # Same color for border
            "borderWidth": 1,
            "stack": "expenses"
        })

    #generate list of month names
    ordered_months = [month_name[i] for i in range(1,13)]

    # prepare data for annual graph
    annual_expense = 0
    annual_labels = [f"{month} {current_year}" for month in ordered_months] # create labels for each month/year pair for the current year
    annual_income_data = [0] * 12 # creates a list with twelves '0's (one for each month)
    # creates a dictionary where each category is a key and corresponding value is a list of 12 zeros
    annual_expense_data = {category: [0]*12 for category in Category.objects.values_list('category', flat=True)} # flat=True ensures a simple list instead of tuples
    # examples:
    # "salary": [0,0,0,0,0,0,0,0,0,0,0,0]
    # "mortgage/rent": [0,0,0,0,0,0,0,0,0,0,0,0]

    # organize income and expense by month
    for transaction in annual_transactions:
        # accesses the month of the transaction and places it's index (ie 1 for January will be 0) in month_index
        month_index = ordered_months.index(transaction.month.month)
        # extracts category name for current transaction
        category = transaction.category.category

        if category.lower() == 'salary':
            # places salary into appropriate month for each transaction
            # so if transaction was in january it accesses the index 0 and adds it
            annual_income_data[month_index] += float(transaction.amount)
        else:
            if category not in annual_expense_data:
                annual_expense_data[category] = [0] * 12
            # adds expense to the appropriate categories month index
            annual_expense_data[category][month_index] += float(transaction.amount)
            annual_expense += float(transaction.amount)
    
    annual_income = sum(annual_income_data)

    annual_datasets = [
        {
            "label": "Income",
            "data": annual_income_data,
            "backgroundColor": "rgb(75, 192, 192)", # teal
            "borderColor": "rgb(75, 192, 192)",
            "borderWidth": 1,
            "order": 1,
            "stack": "income"
        }
    ]

    for idx, (category, data) in enumerate(annual_expense_data.items()):
        annual_datasets.append({
            "label": category,
            "data": data,
            "backgroundColor": expense_colors[idx % len(expense_colors)],  # Cycle through the colors
            "borderColor": expense_colors[idx % len(expense_colors)],  # Same color for border
            "borderWidth": 1,
            "stack": "expenses"
        })

    context = {
        'current_month_labels': current_month_labels,
        'current_month_datasets': current_month_datasets,
        'annual_labels': annual_labels,
        'annual_datasets': annual_datasets,
        'current_month_income': round(total_income,2),
        'current_month_expenses': round(current_month_total_expenses,2),
        'current_month_balance': round(total_income - current_month_total_expenses,2),
        'annual_income': round(annual_income,2),
        'annual_expense': round(annual_expense,2),
        'annual_balance': round(annual_income - annual_expense,2)
    }

    return render(request, 'finances/home.html', context)

@login_required
def create_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, f'Your transaction was saved successfully!')
            return redirect('finances:home')
    else:
        form = TransactionForm()
    
    return render(request, 'finances/transaction-form.html', {'form': form})

@login_required
def update_transaction(request, id):
    trans = get_object_or_404(Transaction, id=id, user=request.user)
    form = TransactionForm(request.POST or None, instance=trans)

    if form.is_valid():
        form.save()
        return redirect('finances:home')
    
    return render(request, 'finances/transaction-form.html', {'form': form, 'trans': trans})

@login_required
def view_transaction(request):
    current_year = now().year

    # retrieve year and month from request
    year = int(request.GET.get('year', current_year))
    month = request.GET.get('month', '')

    # retrieve all transactions associated with current user
    transactions = Transaction.objects.filter(user=request.user)
    # attempts to find all transactions by month and filters them if found
    if month:
        try:
            selected_month = Month.objects.get(month=month, year=year)
            transactions = transactions.filter(month=selected_month)
        # returns an empty query if requested month has no entries
        except Month.DoesNotExist:
            transactions = Transaction.objects.none()
    # if no month is provided than filters by selected year
    else:
        transactions = transactions.filter(month__year=year)

    # orders in descending order where the - means the most recent transactions first
    transactions = transactions.order_by('-date')

    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # generates a range of years for the drop down box, 5 years prior to current year as well as current
    available_years = range(current_year - 5, current_year + 1)
    # creates a list of month names. the [1:] excludes the empty string at index 0
    available_months = list(month_name)[1:]

    context = {
        'page_obj': page_obj, # Paginated transactions
        'year': year, # Year being viewed
        'month': month,
        'available_years': available_years,
        'available_months': available_months
    }

    return render(request, 'finances/transaction-view.html', context)

@login_required
def detail_transaction(request, id):
    transaction = get_object_or_404(Transaction, pk=id)
    return render(request, 'finances/transaction-detail.html', {'transaction': transaction})

@login_required
def delete_transaction(request, id):
    transaction = get_object_or_404(Transaction, pk=id)
    transaction.delete()
    return redirect('finances:view_transaction')
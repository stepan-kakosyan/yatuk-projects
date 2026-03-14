import json
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from product.forms import TransactionForm, CostForm, TransferForm
from .models import BORDER_COLORS, COLORS, TRANSACTION_TYPES, COST_TYPES, Collaborator, \
    CostTransaction, Product, ProductTransaction, Transfer, ProductCategory
from core_play.models import Audio, Author
from django.db.models import Sum, Q, Sum
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def products(request):
    return render(request, "core/products.html", context={
        "products":Product.objects.all()
        })

@login_required
def transactions(request):
    products = Product.objects.filter(transactions__isnull=False).distinct()
    collabarators = Collaborator.objects.filter(transactions__isnull=False).distinct()
    transactions = ProductTransaction.objects.all().order_by("-id")
    prod = request.GET.get("prod", "all")
    type = request.GET.get("type", "all")
    coll = request.GET.get("coll", "all")
    if prod and prod != "all":
        transactions = transactions.filter(product_id=prod)
        prod = int(prod)
    if type and type != "all":
        transactions = transactions.filter(type=type)
    if coll and coll != "all":
        transactions = transactions.filter(collaborator_id=coll)
        coll = int(coll)
    page = request.GET.get('page', 1)    
    paginator = Paginator(transactions, 12)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    template = "core/partials/transaction-table.html" if request.htmx else "core/transactions.html"
    return render(request, template, context={
        "transactions": result,
        "products": products,
        "collabarators": collabarators,
        "types": [{"value":i[0], "name": i[1]} for i in TRANSACTION_TYPES],
        "prod": prod,
        "type": type,
        "coll": coll,
        "page": int(page)
        })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("transactions"))
        else:
                return render(request, "core/add-transaction.html", 
                  context={
                      "form": form
                      }
                  )
    else:
        form = TransactionForm()

    return render(request, "core/add-transaction.html", 
                  context={
                      "form": form
                      }
                  )

@login_required
def costs(request):
    categories = ProductCategory.objects.filter(costs__isnull=False).distinct()
    costs = CostTransaction.objects.all().order_by("-date")
    category = request.GET.get("category", "all")
    cost_type = request.GET.get("cost_type", "all")
    search = request.GET.get("search", None)
    if category and category != "all":
        costs = costs.filter(product_category_id=category)
        category = int(category)

    if cost_type and cost_type != "all":
        costs = costs.filter(type=cost_type)
    if search:
        costs = costs.filter(note__icontains=search)
    page = request.GET.get('page', 1)    
    paginator = Paginator(costs, 12)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    template = "core/partials/cost-table.html" if request.htmx else "core/costs.html"
    return render(request, template, context={
        "costs": result,
        "categories": categories,
        "cost_types": [{"value":i[0], "name": i[1]} for i in COST_TYPES],
        "category": category,
        "cost_type": cost_type,
        "search": search if search else "",
        "page": int(page)
        })

@login_required
def add_cost(request):
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("costs"))
        else:
                return render(request, "core/add-cost.html", 
                  context={
                      "form": form
                      }
                  )
    else:
        form = CostForm()

    return render(request, "core/add-cost.html", 
                  context={
                      "form": form
                      }
                  )

@login_required
def transfers(request):
    products = Product.objects.filter(transfers__isnull=False).distinct()
    collabarators = Collaborator.objects.filter(transfers__isnull=False).distinct()
    transfers = Transfer.objects.all().order_by("-date")
    prod = request.GET.get("prod", "all")
    coll = request.GET.get("coll", "all")
    if prod and prod != "all":
        transfers = transfers.filter(product_id=prod)
        prod = int(prod)
    if coll and coll != "all":
        transfers = transfers.filter(collaborator_id=coll)
        coll = int(coll)
    page = request.GET.get('page', 1)    
    paginator = Paginator(transfers, 12)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    template = "core/partials/transfer-table.html" if request.htmx else "core/transfers.html"
    return render(request, template, context={
        "transfers": result,
        "products": products,
        "collabarators": collabarators,
        "prod": prod,
        "coll": coll,
        "page": int(page)
        })

@login_required
def add_transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("transfers"))
        else:
                return render(request, "core/add-transfer.html", 
                  context={
                      "form": form
                      }
                  )
    else:
        form = TransferForm()

    return render(request, "core/add-transfer.html", 
                  context={
                      "form": form
                      }
                  )

@login_required
def collabarators(request):
    collabarators = Collaborator.objects.all().annotate(sum = Sum("transactions__amount")).order_by("-sum")
    page = request.GET.get('page', 1)    
    paginator = Paginator(collabarators, 12)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    template = "core/partials/coll-table.html" if request.htmx else "core/collabarators.html"
    return render(request, template, context={
        "collabarators": result,
        "page": int(page)
        })

@login_required
def product(request, pk):
    _collaborators = Collaborator.objects.filter(transfers__product_id=pk).annotate(
                sent_count = Sum("transfers__count", filter=Q(transfers__product_id=pk)))
    for i in _collaborators:
        i.sell_count = i.transactions.filter(product_id=pk).aggregate(sum=Sum("count"))['sum']
    transactions = ProductTransaction.objects.filter(product_id=pk)
    data = {
        "labels": [i[0] for i in TRANSACTION_TYPES],
        "datasets": [{
            "data": [transactions.filter(type=i[0]).aggregate(sum = Sum("count"))['sum'] for i in TRANSACTION_TYPES],
            "backgroundColor": COLORS,
            "borderColor": BORDER_COLORS
          }
        ]
      }
    return render(request, "core/product.html", context={
        "product": Product.objects.get(id=pk),
        "collabarators": _collaborators,
        "sell_chart": json.dumps(data),
        "total_sell": transactions.aggregate(sum=Sum("amount"))['sum']
        })

from django.core.files.base import ContentFile
from django.http import HttpResponse
# import cv2

def change_filenames(request):
    for image in Audio.objects.all():
        try:
            img = image.image.read()
            image.image.save(image.image.name, ContentFile(img))
        except:
            pass
    for image in Author.objects.all():
        try:
            img = image.image.read()
            image.image.save(image.image.name, ContentFile(img))
        except:
            pass
    return HttpResponse("Done")

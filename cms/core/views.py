from django.shortcuts import render
from product.models import (
    BORDER_COLORS, COLORS, COST_TYPES, TRANSACTION_TYPES,
    CostTransaction, ProductTransaction, Product
)
from django.db.models import Sum, Q
from datetime import datetime, timedelta
import json
from django.contrib.auth.decorators import login_required
from core.models import ToDo, Order, ORDER_STATUS, ContactUs
from core.forms import ToDoForm
from django.db import models
from django.db.models import Func
from django.conf import settings
from django.utils.translation import check_for_language
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


def set_language(request):
    from django.utils.translation import activate
    lang_code = request.GET.get('language', settings.LANGUAGE_CODE)
    next_url = request.GET.get("next_url")
    if next_url:
        next_url = "/"+lang_code+next_url[3:]
    else:
        next_url = "/"+lang_code+"/"
    response = HttpResponseRedirect(next_url)
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['language'] = lang_code
        response.set_cookie("django_language", lang_code, max_age=31536000)
        request.session.set_expiry(31536000)
        activate(lang_code)
    return response


@login_required
def index(request):
    transactions = ProductTransaction.objects.all()
    sum = transactions.aggregate(sum=Sum("amount"))['sum']
    lm_sum = transactions.filter(date__gte=datetime.today()-timedelta(30)).aggregate(
        sum=Sum("amount"))['sum']
    lm_pre_sum = transactions.filter(
        date__range=[
            datetime.today() - timedelta(60),
            datetime.today() - timedelta(30)
        ]
    ).aggregate(sum=Sum("amount"))['sum']
    costs = CostTransaction.objects.all().order_by("-date")
    cost_sum = costs.aggregate(sum=Sum("amount"))['sum']
    lm_cost_sum = costs.filter(
        date__gte=datetime.today()-timedelta(30)).aggregate(
            sum=Sum("amount"))['sum']
    lm_cost_pre_sum = costs.filter(
        date__range=[datetime.today()-timedelta(60),
                     datetime.today()-timedelta(30)]
        ).aggregate(sum=Sum("amount"))['sum']
    sell_percent = 0
    sell_prepercent = 0
    cost_percent = 0
    cost_prepercent = 0
    if lm_sum and lm_pre_sum and sum:
        sell_percent = round(lm_sum*100/sum, 1)
        sell_prepercent = round(lm_pre_sum*100/sum, 1)
    if lm_cost_sum and cost_sum and sum and lm_cost_pre_sum:
        cost_percent = round(lm_cost_sum*100/cost_sum, 1)
        cost_prepercent = round(lm_cost_pre_sum*100/cost_sum, 1)
    sums = costs.aggregate(
        direct_sum=Sum("amount", filter=Q(type="direct")),
        indirect_sum=Sum("amount", filter=Q(type="indirect")))
    mc = {}
    monthly_costs = CostTransaction.objects.annotate(m=Month('date')).filter(
        date__gte=datetime.today()+timedelta(-365)).annotate(
        monthly_cost=Sum('amount')
    ).order_by("date")
    for i in monthly_costs:
        date = f"{i.m}-{i.date.year}"
        if date in mc:
            mc[date] += i.monthly_cost
        else:
            mc[date] = i.monthly_cost
    ms = {}
    monthly_sell = ProductTransaction.objects.annotate(m=Month('date')).filter(
        date__gte=datetime.today()+timedelta(-365)).annotate(
        monthly_sell=Sum('amount')
    ).order_by("date")

    for i in monthly_sell:
        date = f"{i.m}-{i.date.year}"
        if date in ms:
            ms[date] += i.monthly_sell
        else:
            ms[date] = i.monthly_sell
    doughnutPieData1 = {
        "datasets": [{
            "data": [
                transactions.filter(type=i[0]).aggregate(sum=Sum("count"))['sum']
                for i in TRANSACTION_TYPES
            ],
            "backgroundColor": COLORS,
            "borderColor": BORDER_COLORS,
        }],
        "labels": [i[0] for i in TRANSACTION_TYPES]
      }
    doughnutPieData2 = {
        "datasets": [{
            "data": [
                costs.filter(type=i[0]).aggregate(sum=Sum("amount"))['sum']
                for i in COST_TYPES
            ],
            "backgroundColor": COLORS,
            "borderColor": BORDER_COLORS,
        }],
        "labels": [i[0] for i in COST_TYPES]
      }
    CostLineData = {
        "labels": [i for i in mc.keys()],
        "datasets": [{
            "label": '#dddd',
            "data": [i for i in mc.values()],
            "borderColor": [
                '#fc424a'
            ],
            "fill": False
            }]
        }
    SellLineData = {
        "labels": [i for i in ms.keys()],
        "datasets": [{
            "label": '#dddd',
            "data": [i for i in ms.values()],
            "borderColor": [
                '#00d25b'
            ],
            "fill": False
            }]
        }
    ctx = {
        "total_sell": sum if sum else 0,
        "sell_percent": sell_percent,
        "lm_total_sell": lm_sum if lm_sum else 0,
        "sell_prepercent": round(sell_percent - sell_prepercent, 1),
        # ...existing code...
        "cost_percent": cost_percent,
        "lm_total_costs": lm_cost_sum if lm_cost_sum else 0,
        "cost_prepercent": round(cost_percent - cost_prepercent, 1),
        "todos": todo_list(limit=5, owner=request.user),
        "todo_form": ToDoForm(),
        "indirect_sum": sums['indirect_sum'] if sums['indirect_sum'] else 0,
        "direct_sum": sums['direct_sum'] if sums['direct_sum'] else 0,
        "CostLineData": json.dumps(CostLineData),
        "SellLineData": json.dumps(SellLineData),
        "sell_chart": json.dumps(doughnutPieData1),
        "cost_chart": json.dumps(doughnutPieData2)
    }
    return render(request, "core/index.html", context=ctx)


@login_required
def add_todo(request):
    form = ToDoForm(request.POST)
    in_dashboard = request.GET.get("in_dashboard")
    if form.is_valid():
        todo = form.save(commit=False)
        todo.owner = request.user
        todo.save()
    if in_dashboard:
        template = "core/partials/todo-small.html"
        limit = 5
    else:
        template = "core/partials/todo-table.html"
        limit = 1000
    return render(request, template, context={
        "todo_form": ToDoForm(),
        "todos": todo_list(limit=limit, owner=request.user)
    })


@login_required
def remove_todo(request, pk):
    todo = ToDo.objects.get(id=pk)
    in_dashboard = request.GET.get("in_dashboard")
    if in_dashboard:
        template = "core/partials/todo-small.html"
        limit = 5
    else:
        template = "core/partials/todo-table.html"
        limit = 1000
    if todo.owner == request.user:
        todo.removed = True
        todo.save()
    return render(request, template, context={
        "todo_form": ToDoForm(),
        "todos": todo_list(limit=limit, owner=request.user)
    })


@login_required
def done_undone_todo(request, pk):
    todo = ToDo.objects.get(id=pk)
    in_dashboard = request.GET.get("in_dashboard", False)
    if in_dashboard:
        template = "core/partials/todo-small.html"
        limit = 5
    else:
        template = "core/partials/todo-table.html"
        limit = 1000
    if todo.owner == request.user:
        todo.done = not todo.done
        todo.save()
    return render(request, template, context={
        "todo_form": ToDoForm(),
        "todos": todo_list(limit=limit, owner=request.user)
    })


@login_required
def todos(request):
    ctx = {
        "todo_form": ToDoForm(),
        "todos": todo_list(owner=request.user)
    }
    if request.htmx:
        return render(request, "core/partials/todo-table.html", context=ctx)
    return render(request, "core/todos.html", context=ctx)


def todo_list(owner, limit=1000):
    return ToDo.objects.filter(owner=owner, removed=False).order_by(
        "done", "-created_at"
    )[:limit]


@login_required
def orders(request):
    prod = request.GET.get("prod", "all")
    status = request.GET.get("status", "all")
    orders = Order.objects.all().order_by("-id")
    if status and status != "all":
        orders = orders.filter(status=status)
    if prod and prod != "all":
        orders = orders.filter(items__product_id=prod).distinct()
        prod = int(prod)
    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 12)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    template = "core/partials/orders-table.html" if request.htmx else "core/orders.html"
    return render(request, template, context={
            "orders": result,
            "status": status,
            "prod": prod,
            "products": Product.objects.filter(ordered_products__isnull=False).distinct(),
            "statuses": [{"value": i[0], "name": i[1]} for i in ORDER_STATUS],
            "page": int(page)
        })


@login_required
def status_order(request):
    order = Order.objects.get(id=request.GET.get("order_id"))
    order.status = request.GET.get("status")
    order.save()
    return render(request, "core/partials/order-raw.html", context={"order": order})


@login_required
def contact_us_list(request):
    contact_us_list = ContactUs.objects.all().order_by("-id")
    page = request.GET.get('page', 1)
    paginator = Paginator(contact_us_list, 12)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    template = "core/partials/contact-us-table.html" if request.htmx else "core/contact-us-list.html"
    return render(request, template, context={
        "contact_us_list": result,
        "page": int(page)
        })


@login_required
def check_contact_us(request):
    contact_us = ContactUs.objects.get(id=int(request.GET.get("id")))
    contact_us.is_seen = True
    contact_us.save()
    return render(request, "core/partials/contact-us-row.html", context={
        "contact_us": contact_us
    })

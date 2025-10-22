from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from .models import Student, Product, AmountInserted, Order, ChangeReturn

# -------- Home --------
def home(request):
    return render(request, 'home.html')


# -------- Student Login --------
def student_login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        campus = request.POST.get('campus')

        if not name or not campus:
            campuses = [c[0] for c in Student._meta.get_field('campus').choices]
            return render(request, 'student_login.html', {
                'campuses': campuses,
                'error': 'Please enter name and select campus.'
            })

        student, created = Student.objects.get_or_create(name=name, campus=campus)

        # Save student info in session
        request.session['student_id'] = student.id
        request.session['balance'] = float(student.amountinserted_set.aggregate(total=models.Sum('total_amount'))['total'] or 0)
        request.session['temp_total'] = 0.0
        request.session['temp_denominations'] = {"notes": {}, "coins": {}}

        return redirect('student_dashboard')

    campuses = [c[0] for c in Student._meta.get_field('campus').choices]
    return render(request, 'student_login.html', {'campuses': campuses})


# -------- Helper: Calculate Change Denominations --------
def calculate_denominations(amount):
    amount = int(amount)
    notes = [200, 100, 50, 25]
    coins = [20, 10, 5, 1]
    note_counts = {}
    coin_counts = {}
    for note in notes:
        count, amount = divmod(amount, note)
        note_counts[str(note)] = count
    for coin in coins:
        count, amount = divmod(amount, coin)
        coin_counts[str(coin)] = count
    return {"notes": note_counts, "coins": coin_counts}


# -------- Student Dashboard --------
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = get_object_or_404(Student, id=student_id)
    products = Product.objects.all()
    balance = Decimal(request.session.get('balance', 0.0))

    if request.method == 'POST':
        # --- Add money manually ---
        if 'add_money' in request.POST:
            add_money = request.POST.get('add_money', '').strip()
            try:
                add_money = Decimal(add_money)
                if add_money <= 0:
                    raise ValueError("Amount must be positive.")
            except (InvalidOperation, ValueError) as e:
                return render(request, 'student_dashboard.html', {
                    'student': student,
                    'products': products,
                    'balance': balance,
                    'error': f'Invalid amount ({str(e)})'
                })
            balance += add_money
            request.session['balance'] = float(balance)
            return render(request, 'student_dashboard.html', {
                'student': student,
                'products': products,
                'balance': balance,
                'success': f'Rs {add_money:.2f} added.'
            })

        # --- Preview order ---
        elif 'preview_order' in request.POST:
            selected_products = request.POST.getlist('product_id')
            qtys = request.POST.getlist('qty')
            if not selected_products:
                return render(request, 'student_dashboard.html', {
                    'student': student,
                    'products': products,
                    'balance': balance,
                    'error': 'Select at least one product.'
                })
            selected_items = []
            total_cost = Decimal('0.00')
            for i, pid in enumerate(selected_products):
                try:
                    product = Product.objects.get(id=pid)
                    qty = int(qtys[i])
                    cost = Decimal(qty) * product.price
                    selected_items.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'qty': qty,
                        'cost': float(cost)
                    })
                    total_cost += cost
                except Product.DoesNotExist:
                    continue

            if total_cost > balance:
                return render(request, 'student_dashboard.html', {
                    'student': student,
                    'products': products,
                    'balance': balance,
                    'error': f'Insufficient balance! Need Rs {total_cost - balance:.2f} more.'
                })
            return render(request, 'student_dashboard.html', {
                'student': student,
                'products': products,
                'balance': balance,
                'selected_items': selected_items,
                'total_cost': float(total_cost),
                'preview': True
            })

        # --- Confirm order ---
        elif 'confirm_order' in request.POST:
            selected_ids = request.POST.getlist('product_id')
            qtys = request.POST.getlist('qty')
            if not selected_ids:
                return redirect('student_dashboard')

            total_purchase = Decimal('0.00')
            ordered_items = []

            for i, pid in enumerate(selected_ids):
                try:
                    product = Product.objects.get(id=pid)
                    qty = int(qtys[i]) if i < len(qtys) else 1
                    if qty <= 0 or qty > product.qty:
                        continue
                    cost = Decimal(qty) * product.price
                    total_purchase += cost
                    product.qty -= qty
                    product.save()
                    ordered_items.append({
                        'name': product.name,
                        'qty': qty,
                        'price': float(product.price),
                        'cost': float(cost)
                    })
                    # Create order entry
                    Order.objects.create(
                        student=student,
                        product=product,
                        balance=balance,
                        total_purchase=cost,
                        change_amount=0,
                        amount_inserted=cost
                    )
                except Product.DoesNotExist:
                    continue

            change_amount = balance - total_purchase
            if change_amount < 0:
                change_amount = Decimal('0.0')

            change_denoms = calculate_denominations(change_amount)
            ChangeReturn.objects.create(
                student=student,
                notes_200=change_denoms["notes"].get("200", 0),
                notes_100=change_denoms["notes"].get("100", 0),
                notes_50=change_denoms["notes"].get("50", 0),
                notes_25=change_denoms["notes"].get("25", 0),
                coins_20=change_denoms["coins"].get("20", 0),
                coins_10=change_denoms["coins"].get("10", 0),
                coins_5=change_denoms["coins"].get("5", 0),
                coins_1=change_denoms["coins"].get("1", 0),
                denominations=change_denoms
            )

            # Save receipt info
            inserted_money = balance
            balance -= total_purchase
            if balance < 0:
                balance = Decimal('0.0')
            request.session['balance'] = float(balance)
            request.session['receipt'] = {
                'student_name': student.name,
                'campus': student.campus,
                'ordered_items': ordered_items,
                'total_purchase': float(total_purchase),
                'change': float(change_amount),
                'inserted_money': float(inserted_money),
                'date': timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M")
            }

            return redirect('receipt')

    return render(request, 'student_dashboard.html', {
        'student': student,
        'products': products,
        'balance': balance
    })


# -------- Balance Page --------
def balance_page(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("student_login")

    student = get_object_or_404(Student, id=student_id)
    balance = Decimal(request.session.get("balance", 0.0))
    temp_total = Decimal(request.session.get("temp_total", 0.0))
    temp_denominations = request.session.get("temp_denominations", {"notes": {}, "coins": {}})

    notes = ["200", "100", "50", "25"]
    coins = ["20", "10", "5", "1"]
    success, error = None, None

    if request.method == "POST":
        try:
            if "add_note" in request.POST:
                value = request.POST["add_note"]
                temp_total += Decimal(value)
                temp_denominations["notes"][value] = temp_denominations["notes"].get(value, 0) + 1
            elif "add_coin" in request.POST:
                value = request.POST["add_coin"]
                temp_total += Decimal(value)
                temp_denominations["coins"][value] = temp_denominations["coins"].get(value, 0) + 1
            elif "confirm_balance" in request.POST:
                if temp_total <= 0:
                    raise ValueError("Insert some notes or coins first.")
                balance += temp_total
                request.session["balance"] = float(balance)
                AmountInserted.objects.create(
                    student=student,
                    notes_200=temp_denominations["notes"].get("200", 0),
                    notes_100=temp_denominations["notes"].get("100", 0),
                    notes_50=temp_denominations["notes"].get("50", 0),
                    notes_25=temp_denominations["notes"].get("25", 0),
                    coins_20=temp_denominations["coins"].get("20", 0),
                    coins_10=temp_denominations["coins"].get("10", 0),
                    coins_5=temp_denominations["coins"].get("5", 0),
                    coins_1=temp_denominations["coins"].get("1", 0),
                    denominations=temp_denominations
                )
                temp_total = Decimal(0)
                temp_denominations = {"notes": {}, "coins": {}}
                request.session["temp_total"] = 0.0
                request.session["temp_denominations"] = temp_denominations
                success = f"Rs {balance:.2f} successfully added!"
            request.session["temp_total"] = float(temp_total)
            request.session["temp_denominations"] = temp_denominations
        except Exception as e:
            error = str(e)

    return render(request, "balance.html", {
        "student": student,
        "balance": balance,
        "temp_total": temp_total,
        "notes": notes,
        "coins": coins,
        "success": success,
        "error": error,
        "temp_denominations": temp_denominations,
    })


# -------- Receipt Page --------
def receipt(request):
    receipt_data = request.session.get('receipt')
    if not receipt_data:
        return redirect('student_dashboard')

    return render(request, 'receipt.html', {
        'student_name': receipt_data['student_name'],
        'campus': receipt_data['campus'],
        'ordered_items': receipt_data['ordered_items'],
        'total_purchase': receipt_data['total_purchase'],
        'change': receipt_data['change'],
        'inserted_money': receipt_data.get('inserted_money', 0),
        'date': receipt_data['date']
    })

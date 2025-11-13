from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from .models import Student, Product, AmountInserted, Order, ChangeReturn
import logging
import traceback

logger = logging.getLogger(__name__)

# Home 
def home(request):
    return render(request, 'home.html')


#  Student Login 
def student_login(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            campus = request.POST.get('campus', '').strip()

            if not name or not campus:
                campuses = [c[0] for c in Student._meta.get_field('campus').choices]
                return render(request, 'student_login.html', {
                    'campuses': campuses,
                    'error': 'Please enter name and select campus.'
                })

            
            try:
                student, created = Student.objects.get_or_create(
                    name=name, 
                    campus=campus
                   
                )
                logger.info(f"Student {'created' if created else 'found'}: {name} from {campus}")
                
            except Exception as e:
                logger.error(f"Database error in student_login: {str(e)}")
                campuses = [c[0] for c in Student._meta.get_field('campus').choices]
                return render(request, 'student_login.html', {
                    'campuses': campuses,
                    'error': 'Database error. Please try again.'
                })

            # Save student info 
            request.session['student_id'] = student.id
            request.session['balance'] = 0.0  
            request.session['temp_total'] = 0.0
            request.session['temp_denominations'] = {"notes": {}, "coins": {}}

            return redirect('student_dashboard')

        campuses = [c[0] for c in Student._meta.get_field('campus').choices]
        return render(request, 'student_login.html', {'campuses': campuses})
        
    except Exception as e:
        logger.error(f"Unexpected error in student_login: {str(e)}")
        campuses = ['Ebene']  #  only campus choice
        return render(request, 'student_login.html', {
            'campuses': campuses,
            'error': 'System error. Please try again.'
        })

            # Save student info in session
        request.session['student_id'] = student.id
        request.session['balance'] = 0.0
        request.session['temp_total'] = 0.0
        request.session['temp_denominations'] = {"notes": {}, "coins": {}}
            
        logger.info(f"Session set - student_id: {student.id}, redirecting to dashboard")
        return redirect('student_dashboard')

        # GET request - show login form
        try:
            campuses = [c[0] for c in Student._meta.get_field('campus').choices]
        except Exception as e:
            logger.warning(f"Could not get campus choices: {str(e)}")
            campuses = ['Main Campus', 'Tech Campus', 'Business Campus']
            
        logger.info(f"Rendering login form with {len(campuses)} campuses")
        return render(request, 'student_login.html', {'campuses': campuses})
        
    except Exception as e:
        logger.error(f"Unexpected error in student_login: {str(e)}")
        logger.error(traceback.format_exc())
        
        campuses = ['Main Campus', 'Tech Campus', 'Business Campus']
        return render(request, 'student_login.html', {
            'campuses': campuses,
            'error': 'System error. Please try again.'
        })


# -------- Calculate Change Denominations --------
def calculate_denominations(amount):
    try:
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
    except Exception as e:
        logger.error(f"Error in calculate_denominations: {str(e)}")
        return {"notes": {}, "coins": {}}


# -------- Student Dashboard --------
def student_dashboard(request):
    try:
        student_id = request.session.get('student_id')
        logger.info(f"Student dashboard accessed - student_id: {student_id}")
        
        if not student_id:
            logger.warning("No student_id in session, redirecting to login")
            return redirect('student_login')

        student = get_object_or_404(Student, id=student_id)
        products = Product.objects.all()
        balance = Decimal(request.session.get('balance', 0.0))
        
        logger.info(f"Student: {student.name}, Balance: {balance}, Products: {products.count()}")

        selected_items = []
        total_cost = Decimal('0.00')

        if request.method == 'POST':
            logger.info(f"POST request to dashboard - keys: {list(request.POST.keys())}")
            
            
            if 'add_money' in request.POST:
                add_money = request.POST.get('add_money', '').strip()
                logger.info(f"Adding money: {add_money}")
                try:
                    add_money = Decimal(add_money)
                    if add_money <= 0:
                        raise ValueError("Amount must be positive.")
                except (InvalidOperation, ValueError) as e:
                    logger.warning(f"Invalid money amount: {add_money}")
                    return render(request, 'student_dashboard.html', {
                        'student': student,
                        'products': products,
                        'balance': balance,
                        'error': f'Invalid amount ({str(e)})'
                    })
                balance += add_money
                request.session['balance'] = float(balance)
                logger.info(f"New balance: {balance}")
                return render(request, 'student_dashboard.html', {
                    'student': student,
                    'products': products,
                    'balance': balance,
                    'success': f'Rs {add_money:.2f} added.'
                })

            elif 'preview_order' in request.POST:
                selected_products = request.POST.getlist('product_id')
                qtys = request.POST.getlist('qty')
                logger.info(f"Preview order - Products: {selected_products}, Quantities: {qtys}")
                
                if not selected_products:
                    return render(request, 'student_dashboard.html', {
                        'student': student,
                        'products': products,
                        'balance': balance,
                        'error': 'Select at least one product.'
                    })
                for i, pid in enumerate(selected_products):
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

           
            elif 'confirm_order' in request.POST:
                selected_ids = request.POST.getlist('product_id')
                qtys = request.POST.getlist('qty')
                logger.info(f"Confirm order - Products: {selected_ids}, Quantities: {qtys}")
                
                # Validate that we have products selected
                if not selected_ids:
                    return render(request, 'student_dashboard.html', {
                        'student': student,
                        'products': products,
                        'balance': balance,
                        'error': 'Please select at least one product.'
                    })
                
                
                if len(qtys) < len(selected_ids):
                    return render(request, 'student_dashboard.html', {
                        'student': student,
                        'products': products,
                        'balance': balance,
                        'error': 'Invalid order data. Please try again.'
                    })
                
                total_purchase = Decimal('0.00')
                ordered_items = []

                
                for i, pid in enumerate(selected_ids):
                    product = Product.objects.get(id=pid)
                    qty = int(qtys[i]) if i < len(qtys) else 1
                    
                    if qty <= 0:
                        continue
                    
                    if qty > product.qty:
                        return render(request, 'student_dashboard.html', {
                            'student': student,
                            'products': products,
                            'balance': balance,
                            'error': f'Not enough stock for {product.name}.'
                        })
                    
                    cost = Decimal(qty) * product.price
                    total_purchase += cost
                
                # Calculate change
                change_amount = balance - total_purchase
                if change_amount < 0:
                    change_amount = Decimal('0.0')
                
                # Now create orders and update stock
                for i, pid in enumerate(selected_ids):
                    product = Product.objects.get(id=pid)
                    qty = int(qtys[i]) if i < len(qtys) else 1
                    
                    if qty <= 0:
                        continue
                        
                    cost = Decimal(qty) * product.price

                    product.qty -= qty
                    product.save()

                    # Create order with individual product cost
                    order = Order.objects.create(
                        student=student,
                        product=product,
                        balance=balance,
                        total_purchase=cost,  
                        change_amount=Decimal('0.00'),  
                        amount_inserted=cost  
                    )

                    ordered_items.append({
                        'name': product.name,
                        'qty': qty,
                        'price': float(product.price),
                        'cost': float(cost)
                    })

                change_amount = balance - total_purchase
                if change_amount < 0:
                    change_amount = Decimal('0.0')

                # Save change return - FIXED BUG
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

                # Save receipt info in session
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

                logger.info(f"Order completed - Total: {total_purchase}, Change: {change_amount}")
                return redirect('receipt')

        return render(request, 'student_dashboard.html', {
            'student': student,
            'products': products,
            'balance': balance
        })
        
    except Exception as e:
        logger.error(f"Error in student_dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        return render(request, 'error.html', {
            'error_message': 'An error occurred. Please try logging in again.'
        })


# -------- Balance Page (Denominations) --------
def balance_page(request):
    try:
        student_id = request.session.get("student_id")
        logger.info(f"Balance page accessed - student_id: {student_id}")
        
        if not student_id:
            return redirect("student_login")

        student = get_object_or_404(Student, id=student_id)
        request.session.setdefault("balance", 0.0)
        request.session.setdefault("temp_total", 0.0)
        request.session.setdefault("temp_denominations", {"notes": {}, "coins": {}})

        balance = Decimal(request.session["balance"])
        temp_total = Decimal(request.session["temp_total"])
        temp_denominations = request.session["temp_denominations"]

        success = None
        error = None
        notes = ["200", "100", "50", "25"]
        coins = ["20", "10", "5", "1"]

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
                        raise ValueError("Please insert some notes or coins first.")

                    balance += temp_total
                    request.session["balance"] = float(balance)

                    # Save denominations in AmountInserted 
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

                    # Reset temp
                    temp_total = Decimal(0)
                    temp_denominations = {"notes": {}, "coins": {}}
                    request.session["temp_total"] = 0.0
                    request.session["temp_denominations"] = temp_denominations

                    success = f"Rs {balance:.2f} successfully added!"

                request.session["temp_total"] = float(temp_total)
                request.session["temp_denominations"] = temp_denominations

            except ValueError as ve:
                error = str(ve)
            except Exception as e:
                logger.error(f"Error in balance_page POST: {str(e)}")
                error = "An error occurred. Please try again."

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
        
    except Exception as e:
        logger.error(f"Error in balance_page: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect('student_login')


# -------- Receipt Page --------
def receipt(request):
    try:
        receipt_data = request.session.get('receipt')
        if not receipt_data:
            logger.warning("No receipt data in session")
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
    except Exception as e:
        logger.error(f"Error in receipt: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect('student_dashboard')
    

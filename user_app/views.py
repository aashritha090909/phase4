from ipaddress import ip_address

from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, "user_app/home.html")

def add_patient_view(request):
    context = {}

    if request.method == 'POST':
        ip_ssn = request.POST.get('ssn')
        ip_first_name = request.POST.get('first_name')
        ip_last_name = request.POST.get('last_name')
        ip_birthdate = request.POST.get('birthdate')
        ip_address = request.POST.get('address')

        try :
            ip_funds = int(request.POST.get('funds'))
        except (ValueError, TypeError):
            context['error'] = 'Funds must be a whole number'
            return render(request, 'user_app/patient_form.html', context)
        ip_contact = request.POST.get('contact')

        required_fields = [ip_ssn, ip_first_name, ip_last_name, ip_birthdate, ip_address, ip_contact]
        if not all(required_fields) or ip_funds < 0:
            context['error'] = 'All fields are required and Funds cannot be negative'
            return render(request, 'user_app/patient_form.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('add_patient', [ip_ssn, ip_first_name, ip_last_name, ip_birthdate, ip_address, ip_funds, ip_contact])
                context['message'] = f'Patient {ip_ssn} added successfully'

        except Exception as e:
            print(f"Databse Error: {e}")
            context['error'] = f"Database error occurred. Details: {e}"

    return render(request, 'user_app/patient_form.html', context)


def record_symptom_view(request):
    context = {}
    if request.method == 'POST':
        ip_patientId = request.POST.get('patient_id')
        ip_apptDate = request.POST.get('appt_date')
        ip_apptTime = request.POST.get('appt_time')
        ip_symptomType = request.POST.get('symptom_type')

        try:
            ip_numDays = int(request.POST.get('num_days'))
        except (ValueError, TypeError):
            context['error'] = 'Number of Days must be a whole number'
            return render(request, 'user_app/symptom_form.html', context)

        required_fields = [ip_patientId, ip_apptDate, ip_apptTime, ip_symptomType]
        if not all(required_fields) or ip_numDays < 0:
            context['error'] = 'All fields are required and Days cannot be negative'
            return render(request, 'user_app/symptom_form.html', context)


        try:
            with connection.cursor() as cursor:
                    cursor.callproc('record_symptom', [ip_patientId, ip_numDays, ip_apptDate, ip_apptTime, ip_symptomType])
            context['message'] = f'Symptom "{ip_symptomType}" recorded for Patient {ip_patientId} at {ip_apptDate} {ip_apptTime}.'
        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error recording symptom. Details: {e}"

    return render(request, 'user_app/symptom_form.html', context)



def book_appointment_view(request):
    context = {}
    if request.method == 'POST':
        ip_patientId = request.POST.get('patient_id')
        ip_apptDate = request.POST.get('appt_date')
        ip_apptTime = request.POST.get('appt_time')

        try :
            ip_apptCost = int(request.POST.get('cost'))
        except (ValueError, TypeError):
            context['error'] = 'Cost must be a whole number'
            return render(request, 'user_app/book_appointment.html', context)

        required_fields = [ip_patientId, ip_apptDate, ip_apptTime, ip_apptCost]
        if not all(required_fields) or ip_apptCost < 0:
            context['error'] = 'All fields are required and cost cannot be negative'
            return render(request, 'user_app/book_appointment.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('book_appointment', [ip_patientId, ip_apptDate, ip_apptTime, ip_apptCost])
                context['message'] = f'Appointment recorded for Patient {ip_patientId} at {ip_apptDate} {ip_apptTime}.'
        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error recording appointment. Details: {e}"

    return render(request, 'user_app/book_appointment.html', context)



def place_order_view(request):
    context = {}
    if request.method == 'POST':
        ip_patientId = request.POST.get('patient_id')
        ip_doctorId = request.POST.get('doctor_id')
        ip_labType = request.POST.get('lab_type') or None
        ip_drug = request.POST.get('drug') or None
        ip_dosage_raw = (request.POST.get('dosage'))


        try:
            ip_priority = int(request.POST.get('priority'))
            ip_cost = int(request.POST.get('cost'))
            ip_orderNumber = int(request.POST.get('order_number'))
        except(ValueError, TypeError):
            context['error'] = 'Priority, Cost, and Order Number must be a whole number'
            return render(request, 'user_app/place_order.html', context)

        try:
            ip_dosage = int(ip_dosage_raw) if ip_dosage_raw else None
        except (ValueError, TypeError):
            context['error'] = 'Dosage must be a whole number'
            return render(request, 'user_app/place_order.html', context)



        required_fields = [ip_orderNumber, ip_priority, ip_patientId, ip_doctorId, ip_cost]
        if not all(required_fields):
            context['error'] = 'These fields are required'
            return render(request, 'user_app/place_order.html', context)

        if ip_cost < 0:
            context['error'] = 'Cost cant be negative.'
            return render(request, 'user_app/place_order.html', context)

        if not (1 <= ip_priority <= 5) :
            context['error'] = 'Priority must be between 1 and 5'
            return render(request, 'user_app/place_order.html', context)

        is_lab_order = ip_labType not in (None, '', 'None')
        is_prescription = ip_drug not in (None, '', 'None') and ip_dosage is not None

        if is_lab_order and is_prescription:
            context['error'] = 'Order cant be both lab and prescription'
            return render(request, 'user_app/place_order.html', context)

        if not (is_lab_order or is_prescription):
            context['error'] = 'Either lab or prescription must be specified'
            return render(request, 'user_app/place_order.html', context)

        if is_prescription and ip_dosage <= 0:
            context['error'] = 'Dosage must be positive'
            return render(request, 'user_app/place_order.html', context)

        if is_lab_order:
            ip_drug = None
            ip_dosage = None
        else:
            ip_labType = None


        try:
            with connection.cursor() as cursor:
                cursor.callproc('place_order', [ip_orderNumber, ip_priority, ip_patientId, ip_doctorId, ip_cost, ip_labType, ip_drug, ip_dosage])
                context['message'] = f'Order placed for Patient {ip_patientId}.'
        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error placing order. Details: {e}"

    return render(request, 'user_app/place_order.html', context)



def add_staff_to_dept_view(request):
    context = {}
    if request.method == 'POST':
        ip_deptId = request.POST.get('dept_id')
        ip_ssn = request.POST.get('ssn')
        ip_firstname = request.POST.get('firstname')
        ip_lastname = request.POST.get('lastname')
        ip_birthdate = request.POST.get('birthdate')
        ip_startdate = request.POST.get('startdate')
        ip_address = request.POST.get('address')
        ip_staffId = request.POST.get('staff_id')
        ip_salary = request.POST.get('salary')

        required = [ip_deptId, ip_ssn, ip_firstname, ip_lastname, ip_birthdate, ip_startdate, ip_address, ip_staffId, ip_salary]
        if not all(required):
            context['error'] = 'These fields are required'
            return render(request, 'user_app/add_staff_to_dept.html', context)

        try:
            ip_deptId = int(ip_deptId)
            ip_staffId = int(ip_staffId)
            ip_salary = int(ip_salary)
        except (ValueError, TypeError):
            context['error'] = 'Department ID, Staff ID, Salary must be a whole number'
            return render(request, 'user_app/add_staff_to_dept.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('add_staff_to_dept', [ip_deptId, ip_ssn, ip_firstname, ip_lastname, ip_birthdate, ip_startdate, ip_address, ip_staffId, ip_salary])
                context['message'] = f'Staff added to Department {ip_deptId}.'
        except Exception as e:
            context['error'] = f"Error adding staff. Details: {e}"

    return render(request, 'user_app/add_staff_to_dept.html', context)


def query_view(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in rows]

def room_wise(request):
    data = query_view("SELECT * FROM room_wise_view;")
    return render(request, "user_app/room_wise.html", {"data": data})

def symptoms_overview(request):
    data = query_view("SELECT * FROM symptoms_overview_view;")
    return render(request, "user_app/symptoms_overview.html", {"data": data})

def medical_staff(request):
    staff = query_view("SELECT * FROM medical_staff_view;")
    return render(request, "user_app/medical_staff.html", {"staff": staff})

def department_view(request):
    data = query_view("SELECT * FROM department_view;")
    return render(request, "user_app/department_view.html", {"data": data})

def outstanding_charges(request):
    data = query_view("SELECT * FROM outstanding_charges_view;")
    return render(request, "user_app/outstanding_charges.html", {"data": data})

def add_funds_view(request):
    context = {}

    if request.method == 'POST':
        ip_ssn = request.POST.get('ssn')
        amount_raw = request.POST.get('amount')

        try:
            ip_amount = int(amount_raw)
        except (ValueError, TypeError):
            context['error'] = 'Amount must be a valid whole number'
            return render(request, 'user_app/add_funds.html', context)

        if not ip_ssn or ip_amount is None or ip_amount < 0:
            context['error'] = 'SSN is required and amount must be non-negative'
            return render(request, 'user_app/add_funds.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('add_funds', [ip_ssn, ip_amount])
                context['message'] = f'${ip_amount} successfully added to patient {ip_ssn}.'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Database error occurred: {e}"

    return render(request, 'user_app/add_funds.html', context)

def assign_nurse_to_room_view(request):
    context = {}

    if request.method == 'POST':
        nurse_id = request.POST.get('nurse_id')
        room_number_raw = request.POST.get('room_number')

        if not nurse_id or not room_number_raw:
            context['error'] = 'All fields are required.'
            return render(request, 'user_app/assign_nurse_to_room.html', context)

        try:
            room_number = int(room_number_raw)
        except ValueError:
            context['error'] = 'Room number must be a valid number.'
            return render(request, 'user_app/assign_nurse_to_room.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('assign_nurse_to_room', [nurse_id, room_number])
                context['message'] = f'Nurse {nurse_id} assigned to room {room_number} successfully.'
        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Database error occurred: {e}"

    return render(request, 'user_app/assign_nurse_to_room.html', context)









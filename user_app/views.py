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


def assign_room_to_patient_view(request):
    context = {}

    if request.method == 'POST':
        ip_ssn = request.POST.get('ssn')
        ip_roomType = request.POST.get('room_type')

        try:
            ip_roomNumber = int(request.POST.get('room_number'))
        except (ValueError, TypeError):
            context['error'] = 'Room number must be a whole number'
            return render(request, 'user_app/assign_room_to_patient.html', context)

        if not ip_ssn or not ip_roomType:
            context['error'] = 'All fields are required'
            return render(request, 'user_app/assign_room_to_patient.html', context)

        if len(ip_ssn) != 11:
            context['error'] = 'SSN must be XXX-XX-XXXX format'
            return render(request, 'user_app/assign_room_to_patient.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('assign_room_to_patient', [ip_ssn, ip_roomNumber, ip_roomType])
                context['message'] = f'Patient {ip_ssn} assigned to room {ip_roomNumber}'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error assigning room to patient. Details: {e}"

    return render(request, 'user_app/assign_room_to_patient.html', context)


def assign_doctor_to_appointment_view(request):
    context = {}
    if request.method == 'POST':
        ip_patientId = request.POST.get('patient_id')
        ip_apptDate = request.POST.get('appt_date')
        ip_apptTime = request.POST.get('appt_time')
        ip_doctorId = request.POST.get('doctor_id')

        if not ip_patientId or not ip_apptDate or not ip_apptTime or not ip_doctorId:
            context['error'] = 'All fields are required'
            return render(request, 'user_app/assign_doctor_to_appointment.html', context)

        if len(ip_patientId) != 11 or len(ip_doctorId) != 11:
            context['error'] = 'SSNs must be XXX-XX-XXXX FORMAT'
            return render(request, 'user_app/assign_doctor_to_appointment.html', context)

        import re
        if not re.match(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$', ip_apptTime):
            context['error'] = 'Time must be in 24-hour format (HH:MM:SS)'
            return render(request, 'user_app/assign_doctor_to_appointment.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('assign_doctor_to_appointment', [ip_patientId, ip_apptDate, ip_apptTime, ip_doctorId])
                context['message'] = f'Doctor {ip_doctorId} assigned to appointment'

        except Exception as e:
            print(f"Database Error: {e}")
            if "maximum" in str(e).lower() or "3" in str(e):
                context['error'] = f"Error: Maximum 3 doctors per appointment already reached"
            elif "conflict" in str(e).lower() or "other patient" in str(e).lower():
                context['error'] = f"Error: Doctor {ip_doctorId} has another appointment at this time"
            else:
                context['error'] = f"Error assigning doctor to appointment. Details: {e}"

    return render(request, 'user_app/assign_doctor_to_appointment.html', context)


def manage_department_view(request):
    context = {}
    if request.method == 'POST':
        ip_ssn = request.POST.get('ssn')

        try:
            ip_deptId = int(request.POST.get('dept_id'))
        except (ValueError, TypeError):
            context['error'] = 'Department ID must be a whole number'
            return render(request, 'user_app/manage_department.html', context)

        if not ip_ssn:
            context['error'] = 'All fields are required'
            return render(request, 'user_app/manage_department.html', context)

        if len(ip_ssn) != 11:
            context['error'] = 'SSN must be XXX-XX-XXXX format'
            return render(request, 'user_app/manage_department.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('manage_department', [ip_ssn, ip_deptId])
                context['message'] = f'Staff {ip_ssn} set as manager of department {ip_deptId}'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error managing department. Details: {e}"

    return render(request, 'user_app/manage_department.html', context)


def release_room_view(request):
    context = {}
    if request.method == 'POST':
        ip_roomNumber = int(request.POST.get('room_number'))

        if not ip_roomNumber:
            context['error'] = 'Room is required'
            return render(request, 'user_app/release_room.html', context)

        try:
            ip_roomNumber = int(ip_roomNumber)
        except (ValueError, TypeError):
            context['error'] = 'Room number must be a whole number'
            return render(request, 'user_app/release_room.html', context)

        if ip_roomNumber <= 0:
            context['error'] = 'Room number must be positive'
            return render(request, 'user_app/release_room.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('release_room', [ip_roomNumber])
                context['message'] = f'Room {ip_roomNumber} released'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error releasing room. Details: {e}"

    return render(request, 'user_app/release_room.html', context)


def remove_patient_view(request):
    context = {}
    if request.method == 'POST':
        ip_ssn = request.POST.get('ssn')

        if not ip_ssn:
            context['error'] = 'SSN is required'
            return render(request, 'user_app/remove_patient.html', context)

        if len(ip_ssn) != 11:
            context['error'] = 'SSN must be XXX-XX-XXXX format'
            return render(request, 'user_app/remove_patient.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('remove_patient', [ip_ssn])
                context['message'] = f'Patient {ip_ssn} removed'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error removing patient. Details: {e}"

    return render(request, 'user_app/remove_patient.html', context)


def remove_staff_from_dept_view(request):
    context = {}
    if request.method == 'POST':
        ip_ssn = request.POST.get('ssn')

        try:
            ip_deptId = int(request.POST.get('dept_id'))
        except (ValueError, TypeError):
            context['error'] = 'Department ID must be a whole number'
            return render(request, 'user_app/remove_staff_from_dept.html', context)

        if not ip_ssn or not ip_deptId :
            context['error'] = 'All fields are required'
            return render(request, 'user_app/remove_staff_from_dept.html', context)

        if len(ip_ssn) != 11:
            context['error'] = 'SSN must be XXX-XX-XXXX format'
            return render(request, 'user_app/remove_staff_from_dept.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('remove_staff_from_dept', [ip_ssn, ip_deptId])
                context['message'] = f'Staff {ip_ssn} removed from department {ip_deptId}'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error removing staff from department. Details: {e}"

    return render(request, 'user_app/remove_staff_from_dept.html', context)


def complete_appointment_view(request):
    context = {}
    if request.method == 'POST':
        ip_patientId = request.POST.get('patient_id')
        ip_apptDate = request.POST.get('appt_date')
        ip_apptTime = request.POST.get('appt_time')

        if not ip_patientId or not ip_apptDate or not ip_apptTime:
            context['error'] = 'All fields are required'
            return render(request, 'user_app/complete_appointment.html', context)

        if len(ip_patientId) != 11:
            context['error'] = 'PatientID must be XXX-XX-XXXX format'
            return render(request, 'user_app/complete_appointment.html', context)

        import re
        if not re.match(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$', ip_apptTime):
            context['error'] = 'Time must be in 24-hour format (HH:MM:SS)'
            return render(request, 'user_app/complete_appointment.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('complete_appointment', [ip_patientId, ip_apptDate, ip_apptTime])
                context['message'] = f'Appointment completed for patient {ip_patientId}'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error completing appointment. Details: {e}"

    return render(request, 'user_app/complete_appointment.html', context)


def complete_orders_view(request):
    context = {}
    if request.method == 'POST':
        try:
            ip_num_orders = int(request.POST.get('num_orders'))
        except (ValueError, TypeError):
            context['error'] = 'Number of orders must be a whole number'
            return render(request, 'user_app/complete_orders.html', context)

        if not ip_num_orders:
            context['error'] = 'Number of orders is required'
            return render(request, 'user_app/complete_orders.html', context)

        if ip_num_orders < 1:
            context['error'] = 'Number of orders must be at least 1'
            return render(request, 'user_app/complete_orders.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('complete_orders', [ip_num_orders])
                context['message'] = f'Completed {ip_num_orders} order(s)'

        except Exception as e:
            print(f"Database Error: {e}")
            context['error'] = f"Error completing orders. Details: {e}"

    return render(request, 'user_app/complete_orders.html', context)







from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
#from .forms import RegisterForm ,DeviceForm
from .models import (
    Department,
    Designation,
    User,
    DeviceType,
    DeviceSpecification,
    Device,
    DeviceLocation,
    DeviceIssues
)


# -------------------------
# AUTHENTICATION
# -------------------------
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = (request.POST.get("role") or "").strip().lower() 

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

        if not user.designation:
            messages.error(request, "No designation assigned to your account.")
            return redirect("login")

        user_role = user.designation.designation.strip().lower()

  
        if user_role == "principal":
            if role == "staff":
                messages.error(request, "Please use Principal tab.")
                return redirect("login")
            login(request, user)
            return redirect("dashboard")

        login(request, user)
        return redirect("dashboard")

    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

<<<<<<< HEAD
from .forms import RegisterForm
=======

# -------------------------
# REGISTER
# -------------------------
from django.contrib import messages
from .models import User
>>>>>>> 0fd18cb (jih)

def register_view(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        username = request.POST.get("username")

        # 🔥 CHECK USER EXISTS
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists. Redirecting to login...")
            return render(request, 'register.html', {'form': form})  # ❗ stay here

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})
# -------------------------
# DASHBOARD
# -------------------------
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.models import Device, DeviceIssues, Department, User

@login_required
def dashboard(request):

    user = request.user
    user_role = user.designation.designation.strip().lower() if user.designation else None

    if user_role == "principal":

        device_count = Device.objects.count()
        working_device_count = Device.objects.filter(status="Working").count()

     
        reported_issues = DeviceIssues.objects.exclude(status="Solved")
        issue_count = reported_issues.count()

        solved_issue_count = DeviceIssues.objects.filter(status="Solved").count()

        user_count = User.objects.count()
        department_count = Department.objects.count()

    else:
        department = user.department

        device_count = Device.objects.filter(department=department).count()
        working_device_count = Device.objects.filter(
            department=department,
            status="Working"
        ).count()

        reported_issues = DeviceIssues.objects.filter(
            device__department=department
        ).exclude(status="Solved")
        issue_count = reported_issues.count()

        solved_issue_count = DeviceIssues.objects.filter(
            device__department=department,
            status="Solved"
        ).count()

        user_count = None
        department_count = None

    total_issue_count = issue_count + solved_issue_count
    solved_rate = (
        round((solved_issue_count / total_issue_count) * 100)
        if total_issue_count > 0
        else 0
    )
    working_device_rate = (
        round((working_device_count / device_count) * 100)
        if device_count > 0
        else 0
    )
    latest_reported_issues = reported_issues.select_related(
        "device",
        "device__department",
        "reported_by",
    ).order_by("-report_date", "-issue_id")[:5]

    current_hour = timezone.localtime().hour
    if 5 <= current_hour < 12:
        greeting_text = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting_text = "Good Afternoon"
    elif 17 <= current_hour < 21:
        greeting_text = "Good Evening"
    else:
        greeting_text = "Good Night"

    return render(request, "dashboard.html", {
        "device_count": device_count,
        "issue_count": issue_count,
        "solved_issue_count": solved_issue_count,
        "total_issue_count": total_issue_count,
        "solved_rate": solved_rate,
        "working_device_count": working_device_count,
        "working_device_rate": working_device_rate,
        "latest_reported_issues": latest_reported_issues,
        "user_count": user_count,
        "department_count": department_count,
        "is_principal": user_role == "principal",
        "greeting_text": greeting_text,
    })

# -------------------------
# DEPARTMENT
# -------------------------
from django.db.models import Q
from .models import Department

def department_list(request):
    departments = Department.objects.all()


    search_query = request.GET.get("search")
    if search_query:
        departments = departments.filter(
            Q(department_name__icontains=search_query)
        )


    sort = request.GET.get("sort")
    if sort == "asc":
        departments = departments.order_by("department_name")
    elif sort == "desc":
        departments = departments.order_by("-department_name")

    return render(request, "department_list.html", {
        "departments": departments
    })

# -------------------------
# ADD_DEPARTMENT 
# -------------------------
def add_department(request):
    teachers = User.objects.all()

    if request.method == "POST":
        name = request.POST.get("department_name")
        teacher_id = request.POST.get("teacher_in_charge")

        if Department.objects.filter(department_name=name).exists():
            return render(request, "add_department.html", {
                "error": "Department already exists",
                "teachers": teachers
            })

        teacher = User.objects.get(pk=teacher_id) if teacher_id else None

        # 🔥 CREATE DEPARTMENT
        department = Department.objects.create(
            department_name=name,
            teacher_in_charge=teacher
        )

        # 🔥 ADD THIS BLOCK (ONLY CHANGE)
        if teacher:
            teacher.department = department
            teacher.save()

        return redirect("department_list")

    return render(request, "add_department.html", {
        "teachers": teachers
    })


# -------------------------
# DELETE_DEPARTMENT 
# -------------------------

from django.shortcuts import get_object_or_404, redirect
from .models import Department

def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        department.delete()
        return redirect('department_list')

    return render(request, 'delete_department.html', {'department': department})


# -------------------------
# EDIT_DEPARTMENT 
# -------------------------

def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    teachers = User.objects.all()

    if request.method == "POST":
        department.department_name = request.POST.get('department_name')
        teacher_id = request.POST.get('teacher_in_charge')

        old_teacher = department.teacher_in_charge   # 🔥 store old teacher

        new_teacher = User.objects.get(pk=teacher_id) if teacher_id else None
        department.teacher_in_charge = new_teacher

        department.save()

        # 🔥 REMOVE department from old teacher
        if old_teacher and old_teacher != new_teacher:
            old_teacher.department = None
            old_teacher.save()

        # 🔥 ASSIGN department to new teacher
        if new_teacher:
            new_teacher.department = department
            new_teacher.save()

        return redirect('department_list')

    return render(request, 'edit_department.html', {
        'department': department,
        'teachers': teachers
    })
# -------------------------
# USER_DETIALS
# -------------------------
from django.shortcuts import render, get_object_or_404
from .models import User

def user_details(request, id):
    user = get_object_or_404(User, user_id=id)
    return render(request, 'user_details.html', {'user': user})


# -------------------------
# USER_PROFILE
# -------------------------
from django.contrib.auth.decorators import login_required

@login_required
def user_details(request, id):
    user_obj = get_object_or_404(User, user_id=id)

  
    if request.user.user_id != user_obj.user_id:
        return redirect('dashboard')

    return render(request, 'user_details.html', {'user': user_obj})
# -------------------------
# DEVICE_DETAIL
# -------------------------

from django.shortcuts import render, get_object_or_404
from .models import Device, DeviceIssues

def device_detail(request, pk):
    device = get_object_or_404(Device, device_id=pk)

    report_count = DeviceIssues.objects.filter(device=device).count()

    return render(request, "device_detail.html", {
        "device": device,
        "report_count": report_count
    })


# -------------------------
# DEVICE_REPORT_HISTORY
# -------------------------
from django.db.models import Sum

@login_required
def device_report_history(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)

    issues = DeviceIssues.objects.filter(device=device).order_by("-report_date")
    total_cost = DeviceIssues.objects.filter(
        device=device,
        status="Solved"
    ).aggregate(total=Sum("cost"))["total"] or 0

    return render(request, "device_report_history.html", {
        "device": device,
        "issues": issues,
        "total_cost": total_cost
    })
    
# -------------------------
# DOWNLOAD_DEVICE_REPORT_HISTORY 
# -------------------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import styles
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable
from django.http import HttpResponse
from django.db.models import Sum

def download_device_report_history_pdf(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)
    issues = DeviceIssues.objects.filter(device=device).order_by("-report_date")

    total_cost = issues.filter(status="Solved").aggregate(
        total=Sum("cost")
    )["total"] or 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Report_History_{device.label_no}.pdf"'

    doc = SimpleDocTemplate(response)
    elements = []

    style = styles.getSampleStyleSheet()

    elements.append(Paragraph(f"<b>Report History - {device.label_no}</b>", style["Title"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"<b>Total Repair Cost:</b> ₹ {total_cost}", style["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Description", "Status", "Reported", "Repaired", "Cost"]]

    for issue in issues:
        data.append([
            issue.issue_description,
            issue.status,
            issue.report_date.strftime("%d-%m-%Y"),
            issue.repaired_date.strftime("%d-%m-%Y") if issue.repaired_date else "-",
            f"₹ {issue.cost}" if issue.cost else "-"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))

    elements.append(table)
    doc.build(elements)

    return response
# -------------------------
# EDIT_DEVICE
# -------------------------

from django.shortcuts import render, get_object_or_404, redirect
from .models import Device
from .forms import DeviceForm  

def edit_device(request, pk):
    device = get_object_or_404(Device, device_id=pk)

    if request.method == "POST":
        form = DeviceForm(request.POST, request.FILES, instance=device)
        if form.is_valid():
            form.save()
            return redirect('device_detail', pk=device.device_id)
    else:
        form = DeviceForm(instance=device)

    return render(request, 'edit_device.html', {'form': form})


# -------------------------
# DEVICE LOCATION LIST
# -------------------------
@login_required
def device_location_list(request):
    locations = DeviceLocation.objects.select_related("device", "department")
    return render(request, "device_location_list.html", {"locations": locations})


from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReportIssueForm
from .models import Device, Notification


@login_required
def report_issue(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)
    user = request.user

 
    if not user.designation:
        messages.error(request, "Access denied.")
        return redirect("device_list")

    user_role = user.designation.designation.strip().lower()

    if user_role != "principal":

       
        if device.department != user.department and \
           device.department.department_name.lower() != "office":
            messages.error(request, "You are not allowed to report this device.")
            return redirect("device_list")

    if request.method == "POST":
        form = ReportIssueForm(request.POST)

        if form.is_valid():
            issue = form.save(commit=False)
            issue.device = device
            issue.reported_by = user
            issue.status = "Reported"
            issue.save()

           
            device.status = "Reported"
            device.save()

            Notification.objects.create(
                title="Issue Reported",
                message=f"{user.username} reported issue for device {device.label_no}",
                notification_type="ISSUE_REPORTED",
                related_id=issue.issue_id
            )

            messages.success(request, "Issue reported successfully.")
            return redirect("issue_detail", issue_id=issue.issue_id)

    else:
        form = ReportIssueForm()

    return render(request, "report_issue.html", {
        "device": device,
        "form": form
    })


# -------------------------
# ISSUE SOLVED 
# -------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DeviceIssues, Notification


@login_required
def issue_solved(request, pk):
    issue = get_object_or_404(DeviceIssues, issue_id=pk)

    if request.method == "POST":
        issue.status = "Solved"
        issue.repaired_date = timezone.now().date()
        issue.repaired_description = request.POST.get("repaired_description")
        issue.cost = request.POST.get("cost")
        issue.save()

<<<<<<< HEAD
    
=======
        # 🔥 ADD THIS BLOCK
        device = issue.device

        remaining_issues = DeviceIssues.objects.filter(
            device=device
        ).exclude(status="Solved")

        if not remaining_issues.exists():
            device.status = "Working"
            device.save()

        # 🔔 Notification
>>>>>>> 0fd18cb (jih)
        Notification.objects.create(
            title="Issue Solved",
            message=f"Issue solved for device {issue.device.label_no}",
            notification_type="ISSUE_SOLVED",
            related_id=issue.issue_id
        )

        messages.success(request, "Issue marked as solved successfully.")
        return redirect('solved_issue_list')

    return render(request, 'issue_solved.html', {
        'issue': issue
    })

# -------------------------
# DEVICE TYPE LIST
# -------------------------
@login_required
def device_type_list(request):
    types = DeviceType.objects.all().order_by("device_type")

    return render(request, "device_type_list.html", {
        "types": types
    })


# -------------------------
# DEVICE SPEC LIST 
# -------------------------
@login_required
def device_spec_list(request):
    specs = DeviceSpecification.objects.all()
    return render(request, "device_spec_list.html", {"specs": specs})


# -------------------------
# INDEX
# -------------------------
def index(request):
    return render(request, 'index.html')

# -------------------------
# ADD_DEVICE
# -------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Notification, Device
from .forms import DeviceForm
import re


@login_required
def add_device(request):

    # 🔥 ACCESS CONTROL (ONLY ADD THIS BLOCK)
    if not (
    (request.user.designation and request.user.designation.designation.lower() == "principal")
    or
    (request.user.department and request.user == request.user.department.teacher_in_charge)
):
        messages.error(request, "Only principal or department in-charge can add devices.")
        return redirect('device_list')

    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES)

        if form.is_valid():
            device = form.save(commit=False)   # 🔥 IMPORTANT CHANGE

            # 🔥 AUTO LABEL GENERATION
            def generate_short(text):
                return ''.join(word[:3].upper() for word in text.split())

            device_type_short = generate_short(device.device_type.device_type)
            dept_short = generate_short(device.department.department_name)

            prefix = f"{device_type_short}{dept_short}"

            last_device = Device.objects.filter(
                label_no__startswith=prefix
            ).order_by('-device_id').first()

            if last_device:
                match = re.search(r'-(\d+)$', last_device.label_no)
                number = int(match.group(1)) + 1 if match else 1
            else:
                number = 1

            device.label_no = f"{prefix}-{number}"

            device.save()   # 🔥 SAVE AFTER GENERATING LABEL

            # ✅ Notification (UNCHANGED)
            Notification.objects.create(
                title="New Device Added",
                message=f"{request.user.username} added device {device.label_no}",
                notification_type="DEVICE",
                related_id=device.device_id
            )

            messages.success(request, "Device added successfully.")
            return redirect('device_list')

    else:
        form = DeviceForm()

    return render(request, 'add_device.html', {'form': form})
# -------------------------
#   DELETE_DEVICE
# -------------------------
from django.shortcuts import get_object_or_404, redirect

def delete_device(request, id):
    device = get_object_or_404(Device, device_id=id)
    device.delete()
    return redirect('device_list')

# -------------------------
# USER_LIST
# -------------------------
from django.db.models import Q

def user_list(request):
    users = User.objects.all()

    search_query = request.GET.get("search")
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

   
    sort = request.GET.get("sort")
    if sort == "asc":
        users = users.order_by("username")
    elif sort == "desc":
        users = users.order_by("-username")

    return render(request, "user_list.html", {
        "users": users
    })


# -------------------------
# ADD_USER
# -------------------------
from .models import User, Department, Designation
from django.shortcuts import render, redirect, get_object_or_404

def add_user(request):
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        department_id = request.POST.get("department")
        designation_id = request.POST.get("designation")

        department = Department.objects.get(pk=department_id)
        designation = Designation.objects.get(pk=designation_id)

        User.objects.create(
            username=username,
            email=email,
            department=department,
            designation=designation
        )

        return redirect("user_list")

    return render(request, "add_user.html", {
        "departments": departments,
        "designations": designations
    })


# -------------------------
# EDIT_USER
# -------------------------
from .forms import EditUserForm

def edit_user(request, pk):
    user = get_object_or_404(User, user_id=pk)

    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            obj = form.save(commit=False)

            if not (request.user.designation and request.user.designation.designation.lower() == "principal"):
                obj.department = user.department

            obj.save()
            return redirect('user_details', id=user.user_id)

    else:
        form = EditUserForm(instance=user)

    return render(request, 'edit_user.html', {'form': form})

# -------------------------
# ISSUE_LIST
# -------------------------
@login_required
def issue_list(request):

    user = request.user

    if not user.designation:
        issues = DeviceIssues.objects.none()
    else:
        user_role = user.designation.designation.strip().lower()

        if user_role == "principal":
            issues = DeviceIssues.objects.exclude(status="Solved")

        else:
            issues = DeviceIssues.objects.filter(
                device__department=user.department
            ).exclude(status="Solved")

    search_query = request.GET.get("search")
    if search_query:
        issues = issues.filter(
            Q(issue_description__icontains=search_query) |
            Q(device__label_no__icontains=search_query)
        )

    sort = request.GET.get("sort")

    if sort == "date_asc":
        issues = issues.order_by("report_date")
    elif sort == "date_desc":
        issues = issues.order_by("-report_date")
    elif sort == "status":
        issues = issues.order_by("status")

    return render(request, "issue_list.html", {
        "issues": issues,
    })
# -------------------------
# SOLVED_ISSUE_LIST
# -------------------------

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import DeviceIssues

@login_required
def solved_issue_list(request):

    user = request.user

    if not user.designation:
        issues = DeviceIssues.objects.none()
    else:
        user_role = user.designation.designation.strip().lower()

    
        if user_role == "principal":
            issues = DeviceIssues.objects.filter(status="Solved")

  
        else:
            issues = DeviceIssues.objects.filter(
                status="Solved",
                device__department=user.department
            )

    search_query = request.GET.get("search")
    if search_query:
        issues = issues.filter(
            Q(issue_description__icontains=search_query) |
            Q(device__label_no__icontains=search_query)
        )

    sort_query = request.GET.get("sort")
    if sort_query == "report_date_asc":
        issues = issues.order_by("report_date", "issue_id")
    elif sort_query == "report_date_desc":
        issues = issues.order_by("-report_date", "-issue_id")
    elif sort_query == "repaired_date_asc":
        issues = issues.order_by("repaired_date", "issue_id")
    elif sort_query == "repaired_date_desc":
        issues = issues.order_by("-repaired_date", "-issue_id")
    elif sort_query == "cost_asc":
        issues = issues.order_by("cost", "issue_id")
    elif sort_query == "cost_desc":
        issues = issues.order_by("-cost", "-issue_id")

    return render(request, "solved_issue_list.html", {
        "issues": issues,
    })


# -------------------------
# EDIT_SOLVED_ISSUE
# -------------------------
def edit_solved_issue(request, pk):
    issue = get_object_or_404(DeviceIssues, issue_id=pk)

    if request.method == "POST":
        issue.issue_description = request.POST.get("issue_description")
        issue.repaired_description = request.POST.get("repaired_description")
        issue.cost = request.POST.get("cost")
        issue.repaired_date = request.POST.get("repaired_date")
        issue.save()

        return redirect('solved_issue_list')

    return render(request, "edit_solved_issue.html", {
        "issue": issue
    })


# -------------------------
# DELETE_SOLVED_ISSUE 
# -------------------------
def delete_solved_issue(request, pk):
    issue = get_object_or_404(DeviceIssues, issue_id=pk)

    if request.method == "POST":
        issue.delete()
        return redirect('solved_issue_list')

    return redirect('solved_issue_list')

def solved_issue_detail(request, pk):
    issue = get_object_or_404(DeviceIssues, issue_id=pk)

    return render(request, "solved_issue_detail.html", {
        "issue": issue
    })

# -------------------------
# DEVICE_ISSUE 
# -------------------------
from django.shortcuts import render, get_object_or_404
from .models import Device, DeviceIssues
from django.db.models import Q

from django.db.models import Q

def device_issues(request, device_id):
    device = get_object_or_404(Device, pk=device_id)

    issues = DeviceIssues.objects.filter(
        device=device,
        status__in=["Pending", "In Progress"]
    )

    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if search:
        issues = issues.filter(
            Q(issue_description__icontains=search) |
            Q(status__icontains=search)
        )

    if sort == "date_asc":
        issues = issues.order_by("report_date")

    elif sort == "date_desc":
        issues = issues.order_by("-report_date")

    elif sort == "status":
        issues = issues.order_by("status")

    return render(request, "issue_list.html", {
        "device": device,
        "issues": issues
    })


# -------------------------
# ISSUE_DETAIL 
# -------------------------
@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(DeviceIssues, issue_id=issue_id)
    return render(request, "issue_detail.html", {"issue": issue})

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import units
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import ListFlowable
from reportlab.lib.styles import ParagraphStyle


# -------------------------
# DOWNLOAD_SOLVED_ISSUE_pdf 
# -------------------------
def download_solved_issue_pdf(request, pk):
    issue = get_object_or_404(DeviceIssues, issue_id=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Solved_Issue_{issue.issue_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Solved Issue Details</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [
        ["Device", issue.device.label_no],
        ["Problem", issue.issue_description],
        ["Reported By", str(issue.reported_by)],
        ["Reported Date", str(issue.report_date)],
        ["Repaired Description", issue.repaired_description],
        ["Repaired Date", str(issue.repaired_date)],
        ["Cost", f"₹ {issue.cost}"],
    ]

    table = Table(data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(table)

    doc.build(elements)

    return response






from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import PageBreak
from django.db.models import Q


# -------------------------
# DOWNLOAD_SOLVED_ISSUE__LIST_pdf 
# -------------------------
def download_solved_issue_list_pdf(request):
    search = request.GET.get("search")
    sort = request.GET.get("sort")

    issues = DeviceIssues.objects.filter(status__iexact="Solved")

    if search:
        issues = issues.filter(
            Q(issue_description__icontains=search) |
            Q(device__label_no__icontains=search)
        )

    if sort == "report_date_asc":
        issues = issues.order_by("report_date", "issue_id")
    elif sort == "report_date_desc":
        issues = issues.order_by("-report_date", "-issue_id")
    elif sort == "repaired_date_asc":
        issues = issues.order_by("repaired_date", "issue_id")
    elif sort == "repaired_date_desc":
        issues = issues.order_by("-repaired_date", "-issue_id")
    elif sort == "cost_asc":
        issues = issues.order_by("cost", "issue_id")
    elif sort == "cost_desc":
        issues = issues.order_by("-cost", "-issue_id")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Solved_Issues_List.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Solved Issues List</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [
        ["Device", "Problem", "Repaired Description", "Cost", "Reported Date", "Repaired Date"]
    ]

    for issue in issues:
        data.append([
            issue.device.label_no,
            issue.issue_description,
            issue.repaired_description,
            f"₹ {issue.cost}",
            str(issue.report_date),
            str(issue.repaired_date),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    doc.build(elements)

    return response



# -------------------------
# DEVICE_LIST
# -------------------------
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

@login_required
def device_list(request):

    user = request.user

    if not user.designation:
        devices = Device.objects.none()
    else:
        user_role = user.designation.designation.strip().lower()

        if user_role == "principal":
            devices = Device.objects.all()

        else:
            devices = Device.objects.filter(
                Q(department=user.department) |
                Q(department__department_name__iexact="office")
            )

 
    search_query = (request.GET.get("search") or "").strip()
    if search_query:
        devices = devices.filter(
            Q(label_no__icontains=search_query) |
            Q(device_brand__icontains=search_query) |
            Q(device_model__icontains=search_query) |
            Q(device_type__device_type__icontains=search_query)
        )

    total_devices = devices.count()

    status_filter = (request.GET.get("status") or "").strip()
    if status_filter not in {"Working", "Reported"}:
        status_filter = ""

    if status_filter:
        devices = devices.filter(status=status_filter)

    type_filter = (request.GET.get("type") or "").strip()
    if type_filter:
        devices = devices.filter(device_type__device_type=type_filter)

    devices = devices.order_by('device_type__device_type')


    device_type_counts = (
        devices.values('device_type__device_type')
        .annotate(count=Count('device_id'))
        .order_by('device_type__device_type')
    )

    return render(request, "device_list.html", {
        "devices": devices,
        "total_devices": total_devices,
        "current_status": status_filter,
        "search_query": search_query,
        "device_type_counts": device_type_counts,
    })
# -------------------------
# DOWNLOAD_DEVICE_DETIALS__LIST_pdf 
# -------------------------

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import fonts
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def download_device_pdf(request, pk):
    device = get_object_or_404(Device, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Device_{device.label_no}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Device Details</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Label No", device.label_no],
        ["Device Type", str(device.device_type)],
        ["Department", str(device.department) if device.department else "Not Assigned"],
        ["Brand", device.device_brand],
        ["Model", device.device_model],
        ["Cost", f"₹ {device.device_cost}"],
        ["Manufactured Year", str(device.manufactured_year)],
        ["Purchased Date", device.purchased_date.strftime("%d %b %Y")],
        ["Status", device.status],
        ["Block", device.block_number or "-"],
        ["Floor", device.floor_number or "-"],
        ["Room", device.room_number or "-"],
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))

    elements.append(table)

    doc.build(elements)
    return response

# -------------------------
# DOWNLOAD__issue_list__pdf 
# -------------------------

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.db.models import Q
from .models import DeviceIssues


def download_issue_list_pdf(request):
    issues = DeviceIssues.objects.exclude(status="Solved")

 
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if search:
        issues = issues.filter(
            Q(issue_description__icontains=search) |
            Q(status__icontains=search)
        )

    if sort == "date_asc":
        issues = issues.order_by("report_date")
    elif sort == "date_desc":
        issues = issues.order_by("-report_date")
    elif sort == "status":
        issues = issues.order_by("status")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reported_issues.pdf"'

    doc = SimpleDocTemplate(response)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reported Issues Report", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Device", "Description", "Status", "Reported By", "Date"]]

    for issue in issues:
        data.append([
            issue.device.label_no,
            issue.issue_description,
            issue.status,
            str(issue.reported_by),
            issue.report_date.strftime("%d-%m-%Y")
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    return response

# -------------------------
# DOWNLOAD_device_list_pdf 
# -------------------------

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from django.db.models import Q   # 🔥 ADD THIS
from .models import Device


def download_devices_pdf(request):
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")
    device_type = request.GET.get("type")   # 🔥 ADD THIS

    devices = Device.objects.all()

    # 🔍 Search filter
    if search_query:
        devices = devices.filter(
            Q(label_no__icontains=search_query) |
            Q(device_brand__icontains=search_query) |
            Q(device_model__icontains=search_query) |
            Q(device_type__device_type__icontains=search_query)
        )

    # 🔥 TYPE FILTER (THIS IS YOUR FIX)
    if device_type:
        devices = devices.filter(device_type__device_type=device_type)

    # 🔎 Status filter
    if status_filter == "Working":
        devices = devices.filter(status="Working")
    elif status_filter == "Reported":
        devices = devices.filter(status="Reported")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=devices.pdf"

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Device List - Central Hub", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    data = [["Label No", "Type", "Brand", "Model", "Status"]]

    for device in devices:
        data.append([
            device.label_no,
            str(device.device_type),
            device.device_brand,
            device.device_model,
            device.status,
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    return response


# -------------------------
# DELETE ISSUE
# -------------------------


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_issue(request, issue_id):

    issue = get_object_or_404(DeviceIssues, issue_id=issue_id)
    user = request.user
    device = issue.device   

   
    if user.designation.designation.strip().lower() != "principal":
        if device.department != user.department:
            return redirect("issue_list")

    if request.method == "POST":
        issue.delete()

        remaining_issues = DeviceIssues.objects.filter(
            device=device
        ).exclude(status="Solved")

        if not remaining_issues.exists():
            device.status = "Working"
            device.save()

    return redirect("issue_list")


# -------------------------
# DEVICE_ANALYTICS 
# -------------------------
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Device

@login_required
def device_analytics(request):

    user = request.user

    if user.designation.designation.lower() == "principal":
        devices = Device.objects.all()
    else:
        devices = Device.objects.filter(department=user.department)

    working = devices.filter(status="Working").count()
    reported = devices.filter(status="Reported").count()

    context = {
        "chart_data": json.dumps({
            "working": working,
            "reported": reported
        })
    }

    return render(request, "analytics/device_analytics.html", context)


# -------------------------
# ISSUE_ANALYTICS 
# -------------------------

@login_required
def issue_analytics(request):

    user = request.user

    if user.designation and user.designation.designation.lower() == "principal":
        issues = DeviceIssues.objects.all()
    else:
        issues = DeviceIssues.objects.filter(device__department=user.department)

    pending = issues.filter(status="Pending").count()
    progress = issues.filter(status="In Progress").count()
    solved = issues.filter(status="Solved").count()

    import json

    context = {
    "chart_data": json.dumps({
        "pending": pending,
        "progress": progress,
        "solved": solved
    })
}

    return render(request, "analytics/issue_analytics.html", context)

# -------------------------
# SOLVED_ANALYTICS 
# -------------------------



import json
from django.db.models import Count
from .models import DeviceIssues

@login_required
def solved_analytics(request):
    user = request.user

    if user.designation and user.designation.designation.lower() == "principal":
        issues = DeviceIssues.objects.all()
    else:
        issues = DeviceIssues.objects.filter(device__department=user.department)

    solved = issues.filter(status="Solved").count()
    unsolved = issues.exclude(status="Solved").count()

    context = {
        "chart_data": json.dumps({
            "solved": solved,
            "unsolved": unsolved
        })
    }

    return render(request, "analytics/solved_analytics.html", context)



# -------------------------
# WORKING_ANALYTICS 
# -------------------------

import json
from django.contrib.auth.decorators import login_required
from .models import Device

@login_required
def working_analytics(request):
    user = request.user

    if user.designation and user.designation.designation.lower() == "principal":
        devices = Device.objects.all()
    else:
        devices = Device.objects.filter(department=user.department)

    working = devices.filter(status="Working").count()
    non_working = devices.exclude(status="Working").count()

    context = {
        "chart_data": json.dumps({
            "working": working,
            "non_working": non_working
        })
    }

    return render(request, "analytics/working_analytics.html", context)

# -------------------------
# DELETE_DEVICE
# -------------------------

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Device

@login_required
def delete_device(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)

    if request.method == "POST":
        device.delete()

    return redirect("device_list")


# -------------------------
# DELETE_USER
# -------------------------



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def delete_user(request, user_id):
    user_obj = get_object_or_404(User, user_id=user_id)

    if user_obj.designation and user_obj.designation.designation.lower() == "principal":
        messages.error(request, "Principal account cannot be deleted.")
        return redirect("user_list")

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "User deleted successfully.")

    return redirect("user_list")


# -------------------------
# ADD_DEVICE_TYPE
# -------------------------
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DeviceType


@login_required
def add_device_type(request):

    
    if not request.user.designation or request.user.designation.designation.lower() != "principal":
        messages.error(request, "Only Principal can add device types.")
        return redirect("device_type_list")  

    if request.method == "POST":
        name = request.POST.get("device_type", "").strip()

        if not name:
            messages.error(request, "Device type name cannot be empty.")
            return render(request, "add_device_type.html")

        
        if DeviceType.objects.filter(device_type__iexact=name).exists():
            messages.error(request, "Device type already exists.")
            return render(request, "add_device_type.html")

        DeviceType.objects.create(device_type=name)
        messages.success(request, "Device type added successfully.")

        return redirect("device_type_list")   
    return render(request, "add_device_type.html")




# -------------------------
# DELETE_DEVICE_TYPE
# -------------------------

from django.shortcuts import get_object_or_404

@login_required
def delete_device_type(request, id):

    if not request.user.designation or request.user.designation.designation.lower() != "principal":
        messages.error(request, "Only Principal can delete device types.")
        return redirect("device_type_list")

    device_type = get_object_or_404(DeviceType, device_type_id=id)

    if Device.objects.filter(device_type=device_type).exists():
        messages.error(request, "Cannot delete. This type is already used by devices.")
        return redirect("device_type_list")

    device_type.delete()
    messages.success(request, "Device type deleted successfully.")

    return redirect("device_type_list")


# -------------------------
# NOTIFICATIONS
# -------------------------
@login_required
def notifications(request):

    if not request.user.designation or request.user.designation.designation.lower() != "principal":
        return redirect("dashboard")

    notifications = Notification.objects.all().order_by("-created_at")

    notifications.filter(is_read=False).update(is_read=True)

    return render(request, "notifications.html", {
        "notifications": notifications
    })

# -------------------------
# ABOUT
# -------------------------
from django.shortcuts import render
from django.utils import timezone

def about(request):
    return render(request, "about.html", {
        "now": timezone.now()
    })


from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from .models import Department, Device

def department_devices(request, department_id):
    department = get_object_or_404(Department, department_id=department_id)

    device_types = (
        Device.objects
        .filter(department=department)
        .values('device_type__device_type')
        .annotate(count=Count('device_id'))
        .order_by('device_type__device_type')
    )

    return render(request, "department_devices.html", {
        "department": department,
        "device_types": device_types
    })

def department_devices_by_type(request, department_id, device_type):
    department = get_object_or_404(Department, department_id=department_id)

    devices = Device.objects.filter(
        department=department,
        device_type__device_type=device_type
    )

    return render(request, "department_device_list.html", {
        "department": department,
        "devices": devices,
        "device_type": device_type
    })


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from django.db.models import Count

from .models import Department, Device


def department_devices(request, department_id):
    department = get_object_or_404(Department, department_id=department_id)

    device_types = (
        Device.objects
        .filter(department=department)
        .values('device_type__device_type')
        .annotate(count=Count('device_id'))   # keep same as your working view
        .order_by('device_type__device_type')
    )

    if request.GET.get("download") == "pdf":
        return generate_department_pdf(department, device_types)

    return render(request, "department_devices.html", {
        "department": department,
        "device_types": device_types
    })

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

def generate_department_pdf(department, device_types):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{department.department_name}_devices.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()

    title = Paragraph(f"{department.department_name} - Device Types", styles['Title'])

    data = [["Device Type", "Count"]]

    for item in device_types:
        data.append([
            item['device_type__device_type'],
            item['count']
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    doc.build([title, table])

    return response

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from django.db.models import Count

from .models import Department, Device


def download_department_device_types_pdf(request, department_id):
    department = get_object_or_404(Department, department_id=department_id)

    device_types = (
    Device.objects
    .filter(department_id=department_id)   # 🔥 FIX HERE
    .values('device_type__device_type')
    .annotate(count=Count('device_id'))
    .order_by('device_type__device_type')
)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{department.department_name}_devices.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)

    data = [["Device Type", "Count"]]

    for item in device_types:
        data.append([
            item['device_type__device_type'],
            item['count']
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    doc.build([table])

    return response

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet


def download_department_devices_pdf(request, department_id, device_type):

    department = get_object_or_404(Department, department_id=department_id)

    devices = Device.objects.filter(
        department_id=department_id,
        device_type__device_type=device_type
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{device_type}_devices.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    title = Paragraph(f"{department.department_name} - {device_type}", styles['Title'])

    data = [["Label No", "Brand", "Model", "Status"]]

    for d in devices:
        data.append([
            d.label_no,
            d.device_brand,
            d.device_model,
            d.status
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    doc.build([title, table])

    return response




@login_required
def clear_notifications(request):
    if request.method == "POST":
        Notification.objects.all().delete()   # 🔥 FIX
    return redirect('notifications')


@login_required
def delete_notification(request, pk):
    if request.method == "POST":
        Notification.objects.filter(id=pk).delete()   # 🔥 FIX
    return redirect('notifications')
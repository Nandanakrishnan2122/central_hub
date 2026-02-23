from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm ,DeviceForm
from .models import (
    Department,
    Designation,
    User,
    DeviceType,
    DeviceSpecification,
    TypeSpec,
    Device,
    DeviceLocation,
    DeviceIssues
)


# -------------------------
# AUTHENTICATION
# -------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

def register_view(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html', {'form': form})

# -------------------------
# DASHBOARD
# -------------------------
@login_required
def dashboard(request):
    context = {
        "device_count": Device.objects.count(),
        "issue_count": DeviceIssues.objects.count(),
        "department_count": Department.objects.count(),
        "user_count": User.objects.count(),
    }
    return render(request, "dashboard.html", context)


# -------------------------
# DEPARTMENT
# -------------------------
from django.db.models import Q
from .models import Department

def department_list(request):
    departments = Department.objects.all()

    # 🔎 Search
    search_query = request.GET.get("search")
    if search_query:
        departments = departments.filter(
            Q(department_name__icontains=search_query)
        )

    # 🔽 Sorting
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
from django.shortcuts import render, redirect
from .models import Department

def add_department(request):
    if request.method == "POST":
        name = request.POST.get("department_name")

        if name:
            Department.objects.create(department_name=name)
            return redirect("department_list")

    return render(request, "add_department.html")


from django.shortcuts import get_object_or_404

def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        department.delete()
        return redirect("department_list")

    return redirect("department_list")

# -------------------------
# DEVICE
# -------------------------
@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, "device_list.html", {"devices": devices})


from django.shortcuts import render, get_object_or_404
from .models import Device

def device_detail(request, pk):
    device = get_object_or_404(Device, device_id=pk)
    return render(request, 'device_detail.html', {'device': device})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Device
from .forms import DeviceForm   # assuming you already have this

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
# DEVICE LOCATION
# -------------------------
@login_required
def device_location_list(request):
    locations = DeviceLocation.objects.select_related("device", "department")
    return render(request, "device_location_list.html", {"locations": locations})


# -------------------------
# DEVICE ISSUES
# -------------------------
from .forms import ReportIssueForm

@login_required
def report_issue(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)

    if request.method == "POST":
        form = ReportIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.device = device
            issue.reported_by = request.user
            issue.status = "Reported"
            issue.save()

            return redirect("issue_detail", issue_id=issue.issue_id)

    else:
        form = ReportIssueForm()

    return render(request, "report_issue.html", {
        "device": device,
        "form": form
    })


# -------------------------
# DEVICE TYPE & SPEC
# -------------------------
@login_required
def device_type_list(request):
    device_types = DeviceType.objects.all()
    return render(request, "device_type_list.html", {"device_types": device_types})


@login_required
def device_spec_list(request):
    specs = DeviceSpecification.objects.all()
    return render(request, "device_spec_list.html", {"specs": specs})
def index(request):
    return render(request, 'index.html')

def add_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('device_list')
    else:
        form = DeviceForm()

    return render(request, 'add_device.html', {'form': form})




from django.db.models import Q

def user_list(request):
    users = User.objects.all()

    # 🔎 Search
    search_query = request.GET.get("search")
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # 🔽 Sorting
    sort = request.GET.get("sort")
    if sort == "asc":
        users = users.order_by("username")
    elif sort == "desc":
        users = users.order_by("-username")

    return render(request, "user_list.html", {
        "users": users
    })

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

def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.department = Department.objects.get(pk=request.POST.get("department"))
        user.designation = Designation.objects.get(pk=request.POST.get("designation"))
        user.save()

        return redirect("user_list")

    return render(request, "edit_user.html", {
        "user_obj": user,
        "departments": departments,
        "designations": designations
    })


@login_required
def issue_list(request):
    issues = DeviceIssues.objects.select_related("device", "reported_by")
    return render(request, "issue_list.html", {"issues": issues})

from django.shortcuts import render, get_object_or_404
from .models import Device, DeviceIssues
from django.db.models import Q

def device_issues(request, device_id):
    device = get_object_or_404(Device, pk=device_id)

    issues = DeviceIssues.objects.filter(device=device)

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

    return render(request, "device_issues.html", {
        "device": device,
        "issues": issues
    })

@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(DeviceIssues, issue_id=issue_id)
    return render(request, "issue_detail.html", {"issue": issue})
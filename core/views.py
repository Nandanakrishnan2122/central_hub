from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})


# -------------------------
# DEVICE
# -------------------------
@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, "device_list.html", {"devices": devices})


@login_required
def device_detail(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)
    locations = DeviceLocation.objects.filter(device=device)
    issues = DeviceIssues.objects.filter(device=device)

    context = {
        "device": device,
        "locations": locations,
        "issues": issues,
    }
    return render(request, "device_detail.html", context)


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
@login_required
def issue_list(request):
    issues = DeviceIssues.objects.select_related("device", "reported_by")
    return render(request, "issue_list.html", {"issues": issues})


@login_required
def report_issue(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)

    if request.method == "POST":
        description = request.POST.get("issue_description")

        DeviceIssues.objects.create(
            device=device,
            reported_by=request.user,
            issue_description=description,
            report_date=request.POST.get("report_date"),
            status="Reported",
        )
        return redirect("issue_list")

    return render(request, "report_issue.html", {"device": device})


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

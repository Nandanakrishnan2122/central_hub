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

        "issue_count": DeviceIssues.objects.exclude(
            status__iexact="Solved"
        ).count(),
        "solved_issue_count": DeviceIssues.objects.filter(
            status__iexact="Solved"
        ).count(),

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
from .models import Department, User
from django.shortcuts import render, redirect

def add_department(request):
    teachers = User.objects.all()  # or filter by designation if needed

    if request.method == "POST":
        department_name = request.POST.get('department_name')
        teacher_id = request.POST.get('teacher_in_charge')

        teacher = User.objects.get(id=teacher_id) if teacher_id else None

        Department.objects.create(
            department_name=department_name,
            teacher_in_charge=teacher
        )

        return redirect('department_list')

    return render(request, 'add_department.html', {'teachers': teachers})



from django.shortcuts import get_object_or_404, redirect
from .models import Department

def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        department.delete()
        return redirect('department_list')

    return render(request, 'delete_department.html', {'department': department})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Department, User

def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    teachers = User.objects.all()

    if request.method == "POST":
        department.department_name = request.POST.get('department_name')
        teacher_id = request.POST.get('teacher_in_charge')

        if teacher_id:
            department.teacher_in_charge = User.objects.get(id=teacher_id)
        else:
            department.teacher_in_charge = None

        department.save()
        return redirect('department_list')

    return render(request, 'edit_department.html', {
        'department': department,
        'teachers': teachers
    })

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



from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import DeviceIssues   # IMPORTANT

def issue_solved(request, pk):
    issue = get_object_or_404(DeviceIssues, issue_id=pk)

    if request.method == "POST":
        issue.status = "Solved"
        issue.repaired_date = timezone.now().date()
        issue.repaired_description = request.POST.get("repaired_description")
        issue.cost = request.POST.get("cost")
        issue.save()

        return redirect('solved_issue_list')

    return render(request, 'issue_solved.html', {
        'issue': issue
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


from django.db.models import Q

def issue_list(request):
    issues = DeviceIssues.objects.exclude(status__iexact="Solved")

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
        "issues": issues
    })

from django.db.models import Q
from .models import DeviceIssues

def solved_issue_list(request):
    issues = DeviceIssues.objects.filter(status__iexact="Solved").order_by("-repaired_date")

    search = request.GET.get("search")

    if search:
        issues = issues.filter(
            Q(issue_description__icontains=search) |
            Q(device__label_no__icontains=search)
        )

    return render(request, "solved_issue_list.html", {
        "issues": issues
    })

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

@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(DeviceIssues, issue_id=issue_id)
    return render(request, "issue_detail.html", {"issue": issue})
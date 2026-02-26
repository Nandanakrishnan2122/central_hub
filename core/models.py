from django.db import models
from django.contrib.auth.models import AbstractUser


# -------------------------
# DEPARTMENT
# -------------------------
from django.conf import settings

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100, unique=True)

    teacher_in_charge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments_in_charge"
    )

    def __str__(self):
        return self.department_name

# -------------------------
# DESIGNATION
# -------------------------
class Designation(models.Model):
    des_id = models.AutoField(primary_key=True)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.designation


# -------------------------
# USER
# -------------------------
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.username


# -------------------------
# DEVICE TYPE
# -------------------------
class DeviceType(models.Model):
    device_type_id = models.AutoField(primary_key=True)
    device_type = models.CharField(max_length=100)

    def __str__(self):
        return self.device_type


# -------------------------
# DEVICE SPECIFICATION
# -------------------------
class DeviceSpecification(models.Model):
    specification_no = models.AutoField(primary_key=True)
    specification = models.CharField(max_length=100)

    def __str__(self):
        return self.specification


# -------------------------
# TYPE_SPEC (Mapping Table)
# -------------------------
class TypeSpec(models.Model):
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    specification = models.ForeignKey(DeviceSpecification, on_delete=models.CASCADE)


# -------------------------
# DEVICE
# -------------------------
class Device(models.Model):

    STATUS_CHOICES = [
        ('Working', 'Working'),
        ('Reported', 'Reported'),
    ]

    device_id = models.AutoField(primary_key=True)

    device_type = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True)
    device_specification = models.ForeignKey(DeviceSpecification, on_delete=models.SET_NULL, null=True)

    label_no = models.CharField(max_length=50, unique=True)
    device_model = models.CharField(max_length=100)
    device_brand = models.CharField(max_length=100)

    device_cost = models.DecimalField(max_digits=10, decimal_places=2)
    manufactured_year = models.PositiveIntegerField()
    purchased_date = models.DateField()

    # ✅ FIXED STATUS FIELD
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Working'
    )

    device_image = models.ImageField(upload_to='devices/', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    block_number = models.CharField(max_length=50, null=True, blank=True)
    floor_number = models.CharField(max_length=20, null=True, blank=True)
    room_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.label_no


# -------------------------
# DEVICE LOCATION
# -------------------------
class DeviceLocation(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    block_no = models.CharField(max_length=20)
    floor_no = models.CharField(max_length=20)
    room_no = models.CharField(max_length=20)

    status = models.CharField(max_length=50)


# -------------------------
# DEVICE ISSUES
# -------------------------
from django.db import models
from django.conf import settings
from django.utils import timezone


class DeviceIssues(models.Model):
    issue_id = models.AutoField(primary_key=True)

    device = models.ForeignKey(
        'Device',
        on_delete=models.CASCADE,
        related_name="issues"
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_device_issues"
    )

    issue_description = models.TextField()

    report_date = models.DateField(auto_now_add=True)

    # 🔧 Repair / Solve Details
    repaired_date = models.DateField(null=True, blank=True)
    
    repaired_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repaired_device_issues"
    )

    repaired_description = models.TextField(null=True, blank=True)

    precautions = models.TextField(null=True, blank=True)

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Solved', 'Solved'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def mark_as_solved(self, user):
        self.status = 'Solved'
        self.repaired_date = timezone.now().date()
        self.repaired_by = user
        self.save()

    def __str__(self):
        return f"{self.device.label_no} - {self.status}"

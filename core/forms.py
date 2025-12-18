from django import forms
from django.contrib.auth.forms import AuthenticationForm
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


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name']


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ['designation']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'department', 'designation', 'email']


class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['device_type']


class DeviceSpecificationForm(forms.ModelForm):
    class Meta:
        model = DeviceSpecification
        fields = ['specification']


class TypeSpecForm(forms.ModelForm):
    class Meta:
        model = TypeSpec
        fields = ['device_type', 'specification']


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'label_no',
            'device_type',
            'device_specification',
            'device_brand',
            'device_model',
            'device_cost',
            'manufactured_year',
            'purchased_date',
            'status'
        ]


class DeviceLocationForm(forms.ModelForm):
    class Meta:
        model = DeviceLocation
        fields = [
            'device',
            'department',
            'block_no',
            'floor_no',
            'room_no',
            'status'
        ]


class DeviceIssuesForm(forms.ModelForm):
    class Meta:
        model = DeviceIssues
        fields = [
            'device',
            'issue_description',
            'report_date',
            'status',
            'repaired_date',
            'repaired_description',
            'precautions',
            'cost'
        ]

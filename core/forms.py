from django import forms
from django.contrib.auth.forms import AuthenticationForm ,UserCreationForm
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

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


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
        fields = '__all__'
        widgets = {
            'label_no': forms.TextInput(attrs={'class': 'form-control'}),
            'device_type': forms.Select(attrs={'class': 'form-select'}),
            'device_specification': forms.Select(attrs={'class': 'form-select'}),
            'device_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'device_model': forms.TextInput(attrs={'class': 'form-control'}),
            'device_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'manufactured_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchased_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'device_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


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
class ReportIssueForm(forms.ModelForm):
    class Meta:
        model = DeviceIssues
        fields = ['issue_description']
        widgets = {
            'issue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue clearly...'
            }),
        }
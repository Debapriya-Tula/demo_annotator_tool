from django import forms


class LoginForm(forms.Form):
    ROLE_CHOICES = [
        ('company', 'Company'),
        ('annotator', 'Annotator'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(),
        initial='annotator',
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Password',
        })
    )


class TaskUploadForm(forms.Form):
    ANSWER_TYPE_CHOICES = [
        ('yes_no', 'Yes / No'),
        ('free_text', 'Free Text'),
    ]

    file = forms.FileField(
        label='File (Image or PDF)',
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 '
                     'file:rounded-lg file:border-0 file:text-sm file:font-semibold '
                     'file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
            'accept': 'image/*,.pdf',
        })
    )
    question = forms.CharField(
        label='Question',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none '
                     'focus:ring-2 focus:ring-indigo-500 resize-none',
            'rows': 4,
            'placeholder': 'Enter the annotation question for this file...',
        })
    )
    answer_type = forms.ChoiceField(
        label='Answer Type',
        choices=ANSWER_TYPE_CHOICES,
        widget=forms.RadioSelect(),
    )


class SignupForm(forms.Form):
    ROLE_CHOICES = [
        ('company', 'Company'),
        ('annotator', 'Annotator'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(),
        initial='annotator',
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Choose a username',
            'autofocus': True,
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Email (optional)',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Password',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Confirm password',
        })
    )

    def clean_username(self):
        from .models import User
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('That username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        cpw = cleaned_data.get('confirm_password')
        if pw and cpw and pw != cpw:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class AnnotationForm(forms.Form):
    answer = forms.CharField(
        label='Your Answer',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none '
                     'focus:ring-2 focus:ring-indigo-500 resize-none',
            'rows': 4,
            'placeholder': 'Type your answer here...',
        })
    )

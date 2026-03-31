import cloudinary.uploader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import AnnotationForm, LoginForm, TaskUploadForm
from .models import Annotation, Task


def login_view(request):
    """
    Login page — handles GET (show form) and POST (authenticate + redirect by role).
    If user is already authenticated, redirect them to the appropriate dashboard.
    """
    if request.user.is_authenticated:
        if request.user.role == 'company':
            return redirect('company_upload')
        return redirect('annotator_dashboard')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                if user.role == 'company':
                    return redirect('company_upload')
                return redirect('annotator_dashboard')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Log the user out and redirect to login."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@role_required('company')
def company_upload(request):
    """
    Company upload view — upload a file to Cloudinary and create a Task.
    """
    form = TaskUploadForm()

    if request.method == 'POST':
        form = TaskUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            question = form.cleaned_data['question']
            answer_type = form.cleaned_data['answer_type']

            try:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    uploaded_file,
                    resource_type='auto',
                )
                file_url = result['secure_url']
                file_type = 'pdf' if result.get('format') == 'pdf' else 'image'

                # Save the Task
                Task.objects.create(
                    uploaded_by=request.user,
                    file_url=file_url,
                    file_type=file_type,
                    question=question,
                    answer_type=answer_type,
                )
                messages.success(request, 'Task uploaded successfully! Annotators can now see it.')
                return redirect('company_results')

            except Exception as e:
                messages.error(request, f'Upload failed: {str(e)}')

    return render(request, 'company/upload.html', {'form': form})


@role_required('company')
def company_results(request):
    """
    Company results view — list all Tasks with their Annotations.
    """
    tasks = Task.objects.filter(uploaded_by=request.user).prefetch_related('annotations__annotator')
    return render(request, 'company/results.html', {'tasks': tasks})


@role_required('annotator')
def annotator_dashboard(request):
    """
    Annotator dashboard — show the latest Task and handle answer submission.
    Skips tasks already annotated by this user.
    """
    # Find the latest task this annotator has NOT yet annotated
    annotated_task_ids = Annotation.objects.filter(
        annotator=request.user
    ).values_list('task_id', flat=True)

    task = Task.objects.exclude(id__in=annotated_task_ids).order_by('-created_at').first()

    if request.method == 'POST' and task:
        answer_type = task.answer_type

        if answer_type == 'yes_no':
            answer = request.POST.get('answer')
            if answer not in ('Yes', 'No'):
                messages.error(request, 'Please select Yes or No.')
                return render(request, 'annotator/dashboard.html', {'task': task})
        else:
            form = AnnotationForm(request.POST)
            if form.is_valid():
                answer = form.cleaned_data['answer']
            else:
                messages.error(request, 'Please provide a valid answer.')
                return render(request, 'annotator/dashboard.html', {'task': task, 'form': form})

        # Save annotation
        Annotation.objects.create(
            task=task,
            annotator=request.user,
            answer=answer,
        )
        messages.success(request, 'Answer submitted! Loading next task...')
        return redirect('annotator_dashboard')

    form = AnnotationForm() if task and task.answer_type == 'free_text' else None
    return render(request, 'annotator/dashboard.html', {'task': task, 'form': form})

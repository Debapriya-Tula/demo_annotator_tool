import cloudinary.uploader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import AnnotationForm, LoginForm, SignupForm, TaskUploadForm
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
                selected_role = form.cleaned_data['role']
                if user.role != selected_role:
                    messages.error(request, f'This account is not registered as a {selected_role}.')
                else:
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


def signup_view(request):
    """Sign up as a company or annotator."""
    if request.user.is_authenticated:
        if request.user.role == 'company':
            return redirect('company_upload')
        return redirect('annotator_dashboard')

    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            from .models import User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data.get('email', ''),
                password=form.cleaned_data['password'],
                role=form.cleaned_data['role'],
            )
            login(request, user)
            messages.success(request, f'Account created! Welcome, {user.username}.')
            if user.role == 'company':
                return redirect('company_upload')
            return redirect('annotator_dashboard')

    return render(request, 'signup.html', {'form': form})


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
    Annotator dashboard — list all tasks pending annotation by this user.
    """
    annotated_task_ids = Annotation.objects.filter(
        annotator=request.user
    ).values_list('task_id', flat=True)

    pending_tasks = Task.objects.exclude(id__in=annotated_task_ids).order_by('-created_at')
    completed_tasks = Task.objects.filter(id__in=annotated_task_ids).order_by('-created_at')

    return render(request, 'annotator/dashboard.html', {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
    })


@role_required('annotator')
def annotate_task(request, task_id):
    """
    Show a single task and handle answer submission.
    """
    task = get_object_or_404(Task, id=task_id)

    # Redirect if already answered
    if Annotation.objects.filter(task=task, annotator=request.user).exists():
        messages.info(request, 'You have already answered this task.')
        return redirect('annotator_dashboard')

    if request.method == 'POST':
        if task.answer_type == 'yes_no':
            answer = request.POST.get('answer')
            if answer not in ('Yes', 'No'):
                messages.error(request, 'Please select Yes or No.')
                return render(request, 'annotator/task.html', {'task': task})
        else:
            form = AnnotationForm(request.POST)
            if not form.is_valid():
                messages.error(request, 'Please provide a valid answer.')
                return render(request, 'annotator/task.html', {'task': task, 'form': form})
            answer = form.cleaned_data['answer']

        Annotation.objects.create(task=task, annotator=request.user, answer=answer)
        messages.success(request, 'Answer submitted!')
        return redirect('annotator_dashboard')

    form = AnnotationForm() if task.answer_type == 'free_text' else None
    return render(request, 'annotator/task.html', {'task': task, 'form': form})

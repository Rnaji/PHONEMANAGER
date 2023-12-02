from django.shortcuts import render
from django.views.decorators.http import require_GET


# Landing views

@require_GET
def landing(request):
    return render(request, 'landing_index.html')

@require_GET
def legal(request):
    return render(request, 'landing_legal.html')



# dans votre_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Stockez le nom d'utilisateur dans la session
            request.session['registered_username'] = user.username

            return redirect('complete_store_configuration')
    else:
        form = UserRegistrationForm()

    return render(request, 'user_registration.html', {'form': form})



# dans votre_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import StoreConfigurationForm

@login_required
def complete_store_configuration(request):
    # Récupérez le nom d'utilisateur depuis la session
    registered_username = request.session.get('registered_username', None)

    if request.method == 'POST':
        form = StoreConfigurationForm(request.POST)
        if form.is_valid():
            store_configuration = form.save(commit=False)

            # Assurez-vous que l'utilisateur est bien enregistré
            if registered_username:
                store_configuration.user = User.objects.get(username=registered_username)
                store_configuration.save()

            return redirect('confirmation_page')
    else:
        form = StoreConfigurationForm()

    return render(request, 'complete_store_configuration.html', {'form': form})


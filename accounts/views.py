from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirecionar para a página principal ou outra página de destino após o login bem-sucedido
            return redirect('militares:militar_list')
        else:
            # Exibir uma mensagem de erro de login inválido
            return render(request, 'login.html', {'error': 'Credenciais inválidas. Tente novamente.'})
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    # Redirecionar para a página de login após o logout bem-sucedido
    return redirect('login')

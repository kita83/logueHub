# from django.shortcuts import render, redirect
# from allauth.account import views


# class LoginView(views.LoginView):
#     """
#     ログインページへ遷移
#     """
#     template_name = 'accounts/login.html'
#     ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False

#     def dispatch(self, request, *args, **kwargs):
#         response = super(LoginView, self).dispatch(request, *args, **kwargs)
#         return response

#     def form_valid(self, form):
#         return super(LoginView, self).form_valid(form)


# login = LoginView.as_view()


# class LogoutView(views.LogoutView):
#     """
#     ログアウトページへ遷移
#     """
#     template_name = 'accounts/logout.html'
#     def get(self, *args, **kwargs):
#         return self.post(*args, **kwargs)

#     def post(self, *args, **kwargs):
#         if self.request.user.is_authenticated():
#             self.logout()
#         return redirect('/')


# logout = LogoutView.as_view()


# class SignupView(views.SignupView):
#     """
#     サインアップページへ遷移
#     """
#     template_name = 'accounts/signup.html'
#     ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False

#     def get_context_data(self, **kwargs):
#         context = super(SignupView, self).get_context_data(**kwargs)
#         return context


# signup = SignupView.as_view()

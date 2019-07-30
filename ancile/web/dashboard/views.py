import json
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ancile.web.dashboard.models import *
from ancile.web.dashboard.forms import *
from ancile.web.dashboard.decorators import *

# Create your views here.

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {})

@login_required
def providers(request):
    tokens = Token.objects.filter(user=request.user)
    return render(request, "user/providers.html", {"tokens" : tokens})

@login_required
def policies(request):
    policies = Policy.objects.filter(user=request.user)
    return render(request, "user/policies.html", {"policies" : policies})

@login_required
def apps(request):
    policies = Policy.objects.filter(user=request.user)
    context = {}
    context["apps"] = [policy.app for policy in policies]
    context["all_apps"] = App.objects.all()
    return render(request, "user/apps.html", context)

@login_required
@user_is_admin
def admin_users(request):
    users = User.objects.all()
    return render(request, "admin/users.html", {"users" : users})

@login_required
@user_is_admin
def admin_tokens(request):
    tokens = Token.objects.all()
    return render(request, "admin/tokens.html", {"tokens" : tokens})

@login_required
@user_is_admin
def admin_apps(request):
    apps = App.objects.all()
    return render(request, "admin/apps.html", {"apps" : apps})

@login_required
@user_is_admin
def admin_policies(request):
    policies = Policy.objects.all()
    return render(request, "admin/policies.html", {"policies" : policies})

@login_required
@user_is_admin
def admin_groups(request):
    groups = PermissionGroup.objects.all()
    return render(request, "admin/groups.html", {"groups" : groups})

@login_required
@user_is_admin
def admin_providers(request):
    providers = DataProvider.objects.all()
    return render(request, "admin/providers.html", {"providers" : providers})

@login_required
@user_is_admin
def admin_functions(request):
    functions = Function.objects.all()
    return render(request, "admin/functions.html", {"functions" : functions})

@login_required
@user_is_admin
def admin_delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect("/dashboard/admin/users")

@login_required
@user_is_admin
def admin_view_user(request, user_id):
    usr = User.objects.get(pk=user_id)
    tokens = Token.objects.filter(user_id=user_id)
    policies = Policy.objects.filter(user_id=user_id)
    return render(request, "admin/view_user.html", {"usr" : usr, "tokens" : tokens, "policies" : policies})

@login_required
@user_is_admin
def admin_delete_token(request, token_id):
    token = Token.objects.get(pk=token_id)
    user_id = token.user.id
    token.delete()
    return redirect("/dashboard/admin/view/user/" + str(user_id))

@login_required
@user_is_admin
def admin_view_token(request, token_id):
    token = Token.objects.get(pk=token_id)
    return render(request, "admin/view_token.html", {"token" : token})

@login_required
@user_is_admin
def admin_delete_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    user_id = policy.user.id
    policy.delete()
    return redirect("/dashboard/admin/view/user/" + str(user_id))

@login_required
@user_is_admin
def admin_view_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    return render(request, "admin/view_policy.html", {"policy" : policy})

@login_required
@user_is_admin
def admin_add_policy(request, user_id):
    if request.method == "POST":
        form = AdminAddPolicyForm(request.POST)

        provider = request.POST.get('provider')
        form.fields['provider'].choices = [(provider, provider)]

        if form.is_valid():
            policy = Policy(text=form.cleaned_data['text'],
                            provider=DataProvider.objects.get(name=form.cleaned_data['provider']),
                            user=User.objects.get(id=user_id),
                            app=App.objects.get(name=form.cleaned_data['app']),
                            active = True if form.cleaned_data['active'] else False)
            policy.save()
            return redirect("/dashboard/admin/view/user/" + str(user_id))
    else:
        user = User.objects.get(id=user_id)
        form = AdminAddPolicyForm(initial={})
        form.fields['provider'].choices=set([(token.provider.name, token.provider.name) for token in Token.objects.filter(user=user)])

    return render(request, 'admin/add_policy.html', {"user_id" : user_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_policy(request, policy_id):
    policy = Policy.objects.get(pk=policy_id)
    user_id = policy.user.id

    if request.method == "POST":
        form = AdminEditPolicyForm(request.POST)

        if form.is_valid():
            policy.text = form.cleaned_data['text']
            policy.active = True if form.cleaned_data['active'] else False
            policy.save()
            return redirect("/dashboard/admin/view/user/" + str(user_id))
    else:
        form = AdminEditPolicyForm(initial={"text" : policy.text, "active" : policy.active})

    return render(request, 'admin/edit_policy.html', {"policy_id" : policy_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_user(request, user_id):
    user = User.objects.get(pk=user_id)

    if request.method == "POST":
        form = AdminEditUserForm(request.POST)

        if form.is_valid():
            user.is_developer = True if form.cleaned_data['is_developer'] else False
            if user.is_developer:
                for app in user.apps:
                    if app.name not in form.cleaned_data['apps']:
                        app.developers.remove(user)
                        app.save()
                for app in form.cleaned_data['apps']:
                    this_app = App.objects.get(name=app)
                    this_app.developers.add(user)
                    this_app.save()

            user.is_superuser = True if form.cleaned_data['is_admin'] else False
            user.save()
            return redirect("/dashboard/admin/view/user/" + str(user_id))
    else:
        form = AdminEditUserForm(initial={"apps" : [app.name for app in user.apps], "is_admin" : user.is_superuser})

    return render(request, 'admin/edit_user.html', {"user_id" : user_id, "form" : form})

@login_required
@user_is_admin
def admin_delete_app(request, app_id):
    app = App.objects.get(pk=app_id)
    app.delete()
    return redirect("/dashboard/admin/apps")

@login_required
@user_is_admin
def admin_view_app(request, app_id):
    app = App.objects.get(pk=app_id)
    developers = app.developers.all()
    groups = PermissionGroup.objects.filter(app=app)
    functions = Function.objects.filter(app=app)
    return render(request, "admin/view_app.html", {"app" : app,
                                                    "developers" : developers,
                                                    "groups" : groups,
                                                    "functions" : functions})

@login_required
@user_is_admin
def admin_edit_app(request, app_id):
    app = App.objects.get(pk=app_id)

    if request.method == "POST":
        form = AdminEditAppForm(request.POST)

        if form.is_valid():
            app.name = form.cleaned_data["name"]
            app.description = form.cleaned_data["description"]
            app.developers.clear()
            for dev in form.cleaned_data["developers"]:
                dev_user = User.objects.get(username=dev)
                app.developers.add(dev_user)
            app.save()
            return redirect("/dashboard/admin/view/app/" + str(app_id))
    else:
        form = AdminEditAppForm(initial={"developers" : [usr.username for usr in app.developers.all()],
                                            "name" : app.name,
                                            "description" : app.description,
                                            "app_id" : app_id})

    return render(request, 'admin/edit_app.html', {"app_id" : app_id, "form" : form})

@login_required
@user_is_admin
def admin_delete_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    app = group.app
    group.delete()
    return redirect("/dashboard/admin/view/app/" + str(app.id))

@login_required
@user_is_admin
def admin_view_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    policies = PolicyTemplate.objects.filter(group_id=group.id)
    scopes = group.scopes.all()
    return render(request, "admin/view_group.html", {"group" : group,
                                                        "policies" : policies,
                                                        "app" : group.app,
                                                        "scopes" : scopes})

@login_required
@user_is_admin
def admin_add_group(request, app_id):
    if request.method == "POST":
        form = AdminAddGroupForm(request.POST)

        if form.is_valid():
            group = PermissionGroup(name = form.cleaned_data['name'],
                            description = form.cleaned_data['description'],
                            approved = True if form.cleaned_data['approved'] else False,
                            app_id=app_id)

            group.save()
            group.scopes.set([Scope.objects.get(value=scp) for scp in form.cleaned_data['scopes']])
            group.save()
            return redirect("/dashboard/admin/view/app/" + str(app_id))
    else:
        form = AdminEditGroupForm()

    return render(request, 'admin/add_group.html', {"app_id" : app_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_group(request, group_id):
    group = PermissionGroup.objects.get(pk=group_id)
    app_id = group.app.id

    if request.method == "POST":
        form = AdminEditGroupForm(request.POST)

        if form.is_valid():
            group.name = form.cleaned_data['name']
            group.description = form.cleaned_data['description']
            group.scopes.clear()
            group.scopes.set([Scope.objects.get(value=scp) for scp in form.cleaned_data['scopes']])
            approved = True if form.cleaned_data['approved'] else False
            group.save()
            return redirect("/dashboard/admin/view/group/" + str(group_id))
    else:
        form = AdminEditGroupForm(initial={"name" : group.name,
                                            "description" : group.description,
                                            "approved" : group.approved,
                                            "scopes" : [scp.value for scp in group.scopes.all()]})

    return render(request, 'admin/edit_group.html', {"group_id" : group_id, "form" : form})

@login_required
@user_is_admin
def admin_delete_function(request, function_id):
    function = Function.objects.get(pk=function_id)
    app = App.objects.get(id=function.app.id)
    function.delete()
    return redirect("/dashboard/admin/view/app/" + str(app.id))

@login_required
@user_is_admin
def admin_view_function(request, function_id):
    function = Function.objects.get(pk=function_id)
    return render(request, "admin/view_function.html", {"function" : function})

@login_required
@user_is_admin
def admin_add_function(request, app_id):
    if request.method == "POST":
        form = AdminAddFunctionForm(request.POST)

        if form.is_valid():
            function = Function(name = form.cleaned_data['name'],
                            description = form.cleaned_data['description'],
                            body = form.cleaned_data['body'],
                            approved = True if form.cleaned_data["approved"] else False,
                            app_id=app_id)

            function.save()
            return redirect("/dashboard/admin/view/app/" + str(app_id))
    else:
        form = AdminAddFunctionForm()

    return render(request, 'admin/add_function.html', {"app_id" : app_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_function(request, function_id):
    function = Function.objects.get(pk=function_id)

    if request.method == "POST":
        form = AdminEditFunctionForm(request.POST)

        if form.is_valid():
            function.name = form.cleaned_data["name"]
            function.description = form.cleaned_data["description"]
            function.body = form.cleaned_data["body"]
            function.app_id = form.cleaned_data["app_id"]
            function.approved = True if form.cleaned_data["approved"] else False
            function.save()
            return redirect("/dashboard/admin/view/app/" + str(function.app_id))
    else:
        form = AdminEditFunctionForm(initial={"name" : function.name,
                                                "description" : function.description,
                                                "approved" : function.approved,
                                                "app_id" : function.app.id,
                                                "body" : function.body})

    return render(request, 'admin/edit_function.html', {"app_id" : function.app.id, "form" : form})

@login_required
@user_is_admin
def admin_delete_policy_template(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    group_id = policy.group.id
    policy.delete()
    return redirect("/dashboard/admin/view/group/" + str(group_id))

@login_required
@user_is_admin
def admin_view_policy_template(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    return render(request, "admin/view_policy_template.html", {"policy" : policy})

@login_required
@user_is_admin
def admin_add_policy_template(request, group_id):
    if request.method == "POST":
        form = AdminAddPolicyTemplateForm(request.POST)

        if form.is_valid():
            group = PermissionGroup.objects.get(id=group_id)
            policy = PolicyTemplate(text=form.cleaned_data['text'],
                            provider=DataProvider.objects.get(path_name=form.cleaned_data['provider']),
                            group=group,
                            app=group.app)
            policy.save()
            return redirect("/dashboard/admin/view/group/" + str(group_id))
    else:
        form = AdminAddPolicyTemplateForm()

    return render(request, 'admin/add_policy_template.html', {"group_id" : group_id, "form" : form})

@login_required
@user_is_admin
def admin_edit_policy_template(request, policy_id):
    policy = PolicyTemplate.objects.get(pk=policy_id)
    group_id = policy.group.id

    if request.method == "POST":
        form = AdminEditPolicyTemplateForm(request.POST)

        if form.is_valid():
            policy.text = form.cleaned_data['text']
            policy.provider = DataProvider.objects.get(path_name=form.cleaned_data['provider'])
            policy.save()
            return redirect("/dashboard/admin/view/group/" + str(group_id))
    else:
        form = AdminEditPolicyTemplateForm(initial={"text" : policy.text, "provider" : policy.provider.path_name})

    return render(request, 'admin/edit_policy_template.html', {"policy_id" : policy_id, "form" : form})


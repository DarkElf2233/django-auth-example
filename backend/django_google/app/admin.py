from django.contrib import admin
from app.models import Model1, Model2, Model3


def get_app_list(self, request, app_label=None):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    app_dict = self._build_app_dict(request, app_label)

    app_list = list(app_dict.values())

    app_list.append({'name': 'Analitics', 'app_label': 'analitics', 'app_url': '/admin/app/', 'has_module_perms': True, 'models': []})

    model2 = app_list[1]['models'][1]
    app_list[1]['models'].remove(model2)

    app_list[-1]['models'].append(model2)

    return app_list


admin.AdminSite.get_app_list = get_app_list


@admin.register(Model1)
class Model1Admin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Model2)
class Model2Admin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Model3)
class Model3Admin(admin.ModelAdmin):
    list_display = ["name"]

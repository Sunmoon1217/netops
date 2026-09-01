from django.urls import path

from ops.ansible import views as ansible_views

urlpatterns = [
    path("ansible/playbooks/", ansible_views.list_playbooks, name="ansible-playbooks"),
    path("ansible/playbook/", ansible_views.run_playbook, name="ansible-playbook"),
    path("ansible/inventory/", ansible_views.generate_inventory, name="ansible-inventory"),
]

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Q
from django.forms import ModelForm
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView

from .forms import RecordForm
from .models import CashFlowRecord, Category, Status, Subcategory, Type


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("record_list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


MODEL_MAP = {
    "status": (Status, None),
    "type": (Type, None),
    "category": (Category, "type"),
    "subcategory": (Subcategory, "category"),
}


class DirectoryListView(LoginRequiredMixin, ListView):
    template_name = "cashflow/directory_list.html"
    paginate_by = 50

    def get_model(self):
        return MODEL_MAP[self.kwargs["model_name"]][0]

    def get_queryset(self):
        return self.get_model().objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_name"] = self.kwargs["model_name"]
        ctx["parent_field"] = MODEL_MAP[self.kwargs["model_name"]][1]
        return ctx


class DirectoryCreateView(LoginRequiredMixin, CreateView):
    template_name = "cashflow/directory_form.html"

    def get_model(self):
        return MODEL_MAP[self.kwargs["model_name"]][0]

    def get_form_class(self):
        model = self.get_model()
        return type(
            "DirectoryForm",
            (ModelForm,),
            {"Meta": type("Meta", (), {"model": model, "fields": "__all__"})},
        )

    def get_success_url(self):
        return reverse_lazy("directory_list", kwargs={"model_name": self.kwargs["model_name"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_name"] = self.kwargs["model_name"]
        return ctx


class DirectoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "cashflow/directory_form.html"

    def get_model(self):
        return MODEL_MAP[self.kwargs["model_name"]][0]

    def get_form_class(self):
        model = self.get_model()
        return type(
            "DirectoryForm",
            (ModelForm,),
            {"Meta": type("Meta", (), {"model": model, "fields": "__all__"})},
        )

    def get_object(self, queryset=None):
        _ = queryset
        return self.get_model().objects.get(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("directory_list", kwargs={"model_name": self.kwargs["model_name"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_name"] = self.kwargs["model_name"]
        return ctx


class DirectoryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "cashflow/directory_confirm_delete.html"

    def get_model(self):
        return MODEL_MAP[self.kwargs["model_name"]][0]

    def get_object(self, queryset=None):
        _ = queryset
        return self.get_model().objects.get(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("directory_list", kwargs={"model_name": self.kwargs["model_name"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_name"] = self.kwargs["model_name"]
        return ctx

    def post(self, request, *_args, **_kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Запись удалена.")
        except ProtectedError:
            messages.error(request, "Невозможно удалить: запись используется в ДДС.")
        return redirect(self.get_success_url())


def api_categories_by_type(request):
    type_id = request.GET.get("type_id")
    if not type_id:
        return JsonResponse([], safe=False)
    qs = Category.objects.filter(type_id=type_id).values("id", "name")
    return JsonResponse(list(qs), safe=False)


def api_subcategories_by_category(request):
    category_id = request.GET.get("category_id")
    if not category_id:
        return JsonResponse([], safe=False)
    qs = Subcategory.objects.filter(category_id=category_id).values("id", "name")
    return JsonResponse(list(qs), safe=False)


class RecordListView(LoginRequiredMixin, ListView):
    model = CashFlowRecord
    template_name = "cashflow/record_list.html"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("status", "type", "category", "subcategory")
        qs = qs.filter(user=self.request.user)
        params = self.request.GET

        date_from = params.get("date_from")
        date_to = params.get("date_to")
        status = params.get("status")
        type_obj = params.get("type")
        category = params.get("category")
        subcategory = params.get("subcategory")

        filters = Q()
        if date_from:
            filters &= Q(date__gte=date_from)
        if date_to:
            filters &= Q(date__lte=date_to)
        if status:
            filters &= Q(status_id=status)
        if type_obj:
            filters &= Q(type_id=type_obj)
        if category:
            filters &= Q(category_id=category)
        if subcategory:
            filters &= Q(subcategory_id=subcategory)

        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Status.objects.all()
        ctx["types"] = Type.objects.all()
        ctx["filter_params"] = self.request.GET
        return ctx


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = CashFlowRecord
    form_class = RecordForm
    template_name = "cashflow/record_form.html"
    success_url = reverse_lazy("record_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = CashFlowRecord
    form_class = RecordForm
    template_name = "cashflow/record_form.html"
    success_url = reverse_lazy("record_list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_update"] = True
        return ctx


class RecordDeleteView(LoginRequiredMixin, DeleteView):
    model = CashFlowRecord
    template_name = "cashflow/record_confirm_delete.html"
    success_url = reverse_lazy("record_list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

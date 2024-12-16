from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, View
from apps.models import Modules, Question, UserExperience
from api.serializers import ModulesSerializer, QuestionSerializer, UserSerializer
from django.db.models import Sum, F  # Add this import

from apps.forms import ModuleForm, QuestionForm, AnswerForm
from apps.models import (
    Students,
    Sections,
    AccessToken,
    Teachers,
    Modules,
    ModuleMaterials,
    Question,
    Answer,
    UserCompletedModules,
    User_Module_Answer
)


# Create your views here.
class SignInView(TemplateView):
    template_name = "auth/signin.html"


class HomepageView(LoginRequiredMixin, TemplateView):
    template_name = "homepage.html"
    login_url = "/signin"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the top 10 users sorted by total experience points
        leaderboard = UserExperience.objects.annotate(
            annotated_total_points=F('total_points')  # Rename annotation
        ).order_by('-annotated_total_points')[:10]  # Use the new annotated field name

        leaderboard_data = []
        
        for user_experience in leaderboard:
            user = user_experience.user
            user_data = UserSerializer(user).data
            user_data['experience'] = user_experience.total_points
            leaderboard_data.append(user_data)

        context["analytics_active"] = True
        context["leaderboard"] = leaderboard_data
        return context


class UsersManagementView(LoginRequiredMixin, TemplateView):
    template_name = "users_management.html"
    login_url = "/signin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students = Students.objects.all()

        context["users_management_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )

        context["students"] = students
        return context

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "user_profile_template.html"
    login_url = "/signin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get("student_id")
        student = get_object_or_404(Students, user_id=student_id)
        user_experience = UserExperience.objects.get_or_create(user=student.user)[0]
          # Get the list of completed modules and points earned in each
        completed_modules = UserCompletedModules.objects.filter(user=student.user)
        completed_modules_data = []

        for completed in completed_modules:
            module = completed.module
            # Calculate the total points for the completed module
            total_module_points = User_Module_Answer.objects.filter(
                user=student.user, question__module=module
            ).filter(
                question__answer__text=F('text')  # Correct answers matching user's answer
            ).aggregate(total_points=Sum('question__answer__points'))['total_points'] or 0

            completed_modules_data.append({
                'module_title': module.title,
                'points_earned': total_module_points
            })
        
        # Assuming the student has a related experience and completed modules
        student_data = {
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'section': student.section,
            'experience': user_experience.total_points,
            'completed_modules': completed_modules_data,
        }
        context['user'] = student_data
        return context


class ClassSectionsView(LoginRequiredMixin, TemplateView):
    template_name = "class_sections.html"
    login_url = "/signin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sections = Sections.objects.all()

        context["class_lists_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )

        context["sections"] = sections
        return context


class ClassSectionsDetailView(LoginRequiredMixin, DetailView):
    template_name = "class_lists_per_section.html"
    login_url = "/signin"
    context_object_name = "section"
    model = Sections

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_slug = self.kwargs.get("slug")

        students = Students.objects.all()

        context["class_lists_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )

        context["students"] = students
        context["section_slug"] = section_slug
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "settings.html"
    login_url = "/signin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = get_object_or_404(Teachers, user=self.request.user)
        sections = Sections.objects.all()
        access_token = AccessToken.objects.filter(created_by=teacher).first()

        context["settings_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )

        context["sections"] = sections
        context["access_token"] = access_token if access_token else ""
        return context


class ModuleBuilderView(LoginRequiredMixin, TemplateView):
    template_name = "module_builder.html"
    login_url = "/signin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        teacher = get_object_or_404(Teachers, user=user)
        modules = Modules.objects.filter(created_by=teacher)
        form = ModuleForm(self.request.POST or None)

        context["module_builder_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )
        context["form"] = form
        context["modules"] = modules
        return context


class ModuleDetailView(LoginRequiredMixin, DetailView):
    template_name = "module_detail.html"
    login_url = "/signin"
    context_object_name = "module"
    model = Modules

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_slug = self.kwargs.get("slug")
        module = get_object_or_404(Modules, slug=module_slug)
        teacher = get_object_or_404(Teachers, user=self.request.user)
        module_materials = ModuleMaterials.objects.filter(
            module=module, uploaded_by=teacher
        )
        questions = Question.objects.filter(module=module).prefetch_related(
            "answer"
        )
        context["module_builder_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )
        context["module_slug"] = module_slug
        context["module_materials"] = module_materials
        context["questions"] = questions
        return context


class QuestionAnswerCreateView(LoginRequiredMixin, TemplateView):
    login_url = "/signin"
    template_name = "question_and_answer_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        context["slug"] = slug
        context["question_form"] = QuestionForm(self.request.POST or None)
        context["answer_form"] = AnswerForm(self.request.POST or None)
        context["module_builder_active"] = (
            "bg-indigo-500 text-white px-2 rounded-lg font-semibold hover:text-indigo-600 hover:bg-white"
        )
        return context

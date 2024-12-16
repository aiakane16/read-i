import datetime
import json

import pandas as pd
from typing import Union, Dict

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from apps.models import (
    Users,
    Teachers,
    Sections,
    Students,
    AccessToken,
    Modules,
    ModuleMaterials,
    Question,
    Answer,
    Choice
)
from apps.utils import (
    generate_access_token,
    upload_file_to_storage,
    generate_signed_url,
)
from ireadwebapp.settings import redis


def signin_services(request: HttpRequest):
    if request.method == "POST":
        email: str = request.POST.get("email", "")
        password: str = request.POST.get("password", "")

        is_email_exists: bool = Users.objects.filter(email=email).exists()

        if not is_email_exists:
            return render(
                request,
                "components/error_message_alerts.html",
                {"message": "Email address does not exist or invalid."},
            )

        # Authenticate the user with the provided email and password
        user: Union[Users, None] = authenticate(email=email, password=password)

        if user:

            is_user_teacher: bool = Teachers.objects.filter(user=user).exists()

            if not is_user_teacher:
                return render(
                    request,
                    "components/error_message_alerts.html",
                    {"message": "You do not have permission to access this system"},
                )
            login(request, user)
            response = JsonResponse({"message": "Successfully signed in"})
            response["HX-Redirect"] = "/"
            return response

        return render(
            request,
            "components/error_message_alerts.html",
            {"message": "Invalid email address or password"},
        )


def add_new_section(request: HttpRequest):
    if request.method == "POST":
        user: Users = request.user
        section: str = request.POST.get("section", "")

        teacher: Teachers = get_object_or_404(Teachers, user=user)

        Sections.objects.create(section=section, created_by=teacher)
        response = JsonResponse({"message": "Successfully added new section"})
        response["HX-Redirect"] = "/class/sections"
        return response


def upload_class_list(request: HttpRequest, section: str):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        df = pd.read_excel(excel_file)
        data = []
        sections = get_object_or_404(Sections, slug=section)
        for _, row in df.iterrows():
            data.append(
                {
                    "last_name": row.get("Last Name"),
                    "first_name": row.get("First Name"),
                    "middle_name": row.get("Middle Name"),
                    "email": row.get("E-mail"),
                    "section": sections.section,
                    "strand": row.get("Strand"),
                    "birthday": (
                        pd.to_datetime(row.get("Birthday")).strftime("%Y-%m-%d")
                        if pd.notnull(row.get("Birthday"))
                        else None
                    ),
                    "address": row.get("Address"),
                }
            )
        excel_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        redis.set(excel_file_name, data)
        return render(
            request,
            "components/uploaded_class_lists_table.html",
            {"data": data, "excel_file_name": excel_file_name, "section": section},
        )


def validate_student_data(data: Dict) -> bool:
    required_fields = ["email", "first_name", "last_name", "strand", "section"]
    return all(data.get(field) for field in required_fields)


def save_uploaded_class_lists(request: HttpRequest, filename: str, section: str):
    try:
        user = request.user

        teacher = get_object_or_404(Teachers, user=user)
        # Get and decode Redis data
        file_data = redis.get(filename)
        section = get_object_or_404(Sections, slug=section)
        if not file_data:
            raise ValueError("No data found in Redis for the given filename")

        students_data = json.loads(file_data)

        # Validate data format
        if not isinstance(students_data, list):
            raise ValueError("Invalid data format - expected a list of students")

        # Validate each student's data
        invalid_records = []
        valid_students_data = []

        for idx, student in enumerate(students_data):
            if not validate_student_data(student):
                invalid_records.append(idx + 1)
            else:
                valid_students_data.append(student)

        if not valid_students_data:
            raise ValueError("No valid student records found")

        with transaction.atomic():
            access_token = get_object_or_404(AccessToken, created_by=teacher)
            # Create users first
            users = [
                Users(
                    last_name=student["last_name"],
                    first_name=student["first_name"],
                    middle_name=student.get("middle_name", ""),
                    email=student["email"],
                    username=student["email"],  # If username is required
                    password=make_password(
                        access_token.access_token
                    ),  # Properly hashed password
                )
                for student in valid_students_data
            ]

            # Check for duplicate emails
            emails = [user.email for user in users]
            existing_emails = Users.objects.filter(email__in=emails).values_list(
                "email", flat=True
            )
            if existing_emails:
                raise ValidationError(
                    f"Duplicate emails found: {', '.join(existing_emails)}"
                )

            created_users = Users.objects.bulk_create(users)

            # Create students
            students = [
                Students(
                    user=user,
                    strand=student_data["strand"],
                    section=section,
                    birthday=student_data.get("birthday"),
                    address=student_data.get("address", ""),
                )
                for user, student_data in zip(created_users, valid_students_data)
            ]
            Students.objects.bulk_create(students)

        # Clean up Redis key after successful import
        redis.delete(filename)
        response = JsonResponse({"message": "Successfully added new section"})
        response["HX-Redirect"] = f"/class/sections/{section.slug}"
        return response
    except ValidationError as e:
        print(f"ValidationError: {e}")
    except Exception as e:
        print(f"Exception: {e}")


def generate_new_access_token(request: HttpRequest):
    user = request.user
    new_token = generate_access_token(20)

    # Get the teacher instance associated with the user
    teacher = get_object_or_404(Teachers, user=user)

    # Update the existing token if it exists, otherwise create a new one
    AccessToken.objects.update_or_create(
        created_by=teacher, defaults={"access_token": new_token}
    )

    response = JsonResponse({"message": "Successfully generated a new token"})
    response["HX-Redirect"] = "/settings"
    return response


def add_new_module_service(request: HttpRequest):
    user = request.user

    teacher = get_object_or_404(Teachers, user=user)
    if request.method == "POST":
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        difficulty = request.POST.get("difficulty", "")
        category = request.POST.get("category", "")

        Modules.objects.create(
            title=title,
            description=description,
            difficulty=difficulty,
            category=category,
            created_by=teacher,
        )
        response = JsonResponse({"message": "Successfully added a new module"})
        response["HX-Redirect"] = "/module/builder"
        return response


def upload_module_material_service(request: HttpRequest, slug: str):
    user = request.user
    teacher = get_object_or_404(Teachers, user=user)
    module = get_object_or_404(Modules, slug=slug)
    if request.method == "POST":
        name = request.POST.get("name", "")
        file = request.FILES.get("file", None)

        upload_file = upload_file_to_storage(file=file)

        path = upload_file["path"]
        signed_url = generate_signed_url(file_path=path)

        ModuleMaterials.objects.create(
            module=module,
            name=name,
            path=path,
            file_url=signed_url,
            uploaded_by=teacher,
        )
        response = JsonResponse({"message": "Successfully uplaoded a material"})
        response["HX-Redirect"] = f"/module/{slug}"
        return response


def question_and_answer_form_service(request, slug):
    if request.method == "POST":
        question_list = request.POST.getlist("question")
        answer_list = request.POST.getlist("answer")
        points = request.POST.get("points")
        question_type_list = request.POST.getlist("question_type")

        # Extract choices based on naming convention
        module = get_object_or_404(Modules, slug=slug)

        for idx, (question_text, answer_text, question_type) in enumerate(zip(question_list, answer_list, question_type_list)):
            # Create the question
            question = Question.objects.create(
                module=module, 
                text=question_text, 
                question_type=question_type
            )

            if question_type == "multiple_choice":
                # Handle multiple-choice questions
                choice_prefix = f"choice_{idx}_"
                correct_choice_text = answer_text.strip()

                # Collect choices using prefix matching
                choice_keys = [key for key in request.POST.keys() if key.startswith(choice_prefix)]

                for key in choice_keys:
                    choice_text = request.POST.get(key).strip()
                    is_correct = choice_text == correct_choice_text
                    Choice.objects.create(
                        question=question, 
                        text=choice_text, 
                        is_correct=is_correct
                    )
                # Create the correct Answer object with correct answer text
                Answer.objects.create(
                    question=question, 
                    text=correct_choice_text, 
                    points=points  # Assuming each answer has 1 point, adjust as needed
                )
            else:
                # Save answer for non-multiple-choice questions
                Answer.objects.create(question=question, text=answer_text, points=1)
                

        # Redirect after successful creation
        response = JsonResponse({"message": "Successfully created quizzes"})
        response["HX-Redirect"] = f"/module/questions-and-answers/{slug}"
        return response
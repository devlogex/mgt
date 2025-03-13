import os
import django
from django.conf import settings
from django.template import Template, TemplateSyntaxError

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mgt_todo.settings")
django.setup()

def validate_template(template_path):
    try:
        with open(template_path, 'r') as file:
            template_content = file.read()
            print(f"\nTemplate content of {template_path}:\n{template_content}\n")
            Template(template_content)
            print(f"Template {template_path} is valid.")
            return True
    except TemplateSyntaxError as e:
        print(f"Error in template {template_path}:")
        print(str(e))
        return False
    except Exception as e:
        print(f"Error opening or processing {template_path}:")
        print(str(e))
        return False

# Templates to validate
templates = [
    'todo/templates/todo/todo_form.html',
    'todo/templates/todo/todo_confirm_delete.html',
    'todo/templates/todo/todo_list.html',
]

# Validate each template
for template_path in templates:
    validate_template(template_path) 
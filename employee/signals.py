from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from employee.models import Employee


@receiver(pre_delete, sender=Employee)
def pre_delete_employee(sender, instance, **kwargs):
    # Get the Redis connection
    redis_connection = settings.REDIS_CURRICULUM_CONN
    if redis_connection:
        # Delete the Redis key associated with the employee instance
        employee_queue_key = instance.employee_queue_key
        employee_queue_key_str = str(employee_queue_key)

        try:
            redis_connection.delete(employee_queue_key_str)
            print(f"Deleted Redis key associated with employee: {instance.pk}")
        except Exception as e:
            print(f"Failed to delete Redis key: {e}")
    else:
        print("Failed to establish Redis connection")

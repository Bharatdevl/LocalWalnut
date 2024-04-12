import redis
from django.conf import settings

from curriculum.models import Curriculum, Curriculum_Message


def get_weekday_list():
    return [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]


def get_weekday_list_curriculum():
    return [
        "weekdays",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]


def get_schedule_time_list():
    return [
        "08:00 AM",
        "09:00 AM",
        "10:00 AM",
        "11:00 AM",
        "12:00 PM",
        "01:00 PM",
        "02:00 PM",
        "03:00 PM",
        "04:00 PM",
        "05:00 PM",
        "06:00 PM",
        "07:00 PM",
        "08:00 PM",
    ]


def generate_weekday_ordering():
    return {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }


def get_weekdays():
    return [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
    ]


def store_messages_in_redis(employee_obj, curriculum_list):
    # Fetching employee queue key
    employee_queue_key = employee_obj.employee_queue_key

    # Convert employee_queue_key to string
    employee_queue_key_str = str(employee_queue_key)

    redis_conn = settings.REDIS_CURRICULUM_CONN

    # Loop through the curriculum list
    for curriculum_name in curriculum_list:
        # Fetching curriculum object
        try:
            curriculum_obj = Curriculum.objects.get(
                curriculum_name=curriculum_name
            )
        except Curriculum.DoesNotExist:
            print(f"Curriculum with name {curriculum_name} does not exist")
            continue

        # Fetching messages for the curriculum
        curriculum_messages = Curriculum_Message.objects.filter(
            curriculum=curriculum_obj
        ).order_by("pk")

        for message_obj in curriculum_messages:
            redis_conn.lpush(
                employee_queue_key_str, message_obj.curriculum_message
            )

    print(f"Messages stored in Redis for employee {employee_obj}")


def is_queue_empty(employee_obj):
    # Get the length of the queue
    employee_queue_key = employee_obj.employee_queue_key

    # Convert employee_queue_key to string
    employee_queue_key_str = str(employee_queue_key)

    redis_conn = settings.REDIS_CURRICULUM_CONN
    queue_length = redis_conn.llen(employee_queue_key_str)

    # Check if the queue is empty
    if queue_length == 0:
        return True
    else:
        return False


def retrieve_message_from_redis(employee_obj):
    redis_conn = settings.REDIS_CURRICULUM_CONN
    employee_queue_key = employee_obj.employee_queue_key
    # Convert employee_queue_key to string
    employee_queue_key_str = str(employee_queue_key)

    try:
        message = redis_conn.rpop(employee_queue_key_str)
        if message is not None:
            decoded_message = message.decode(
                "utf-8"
            )  # Messages are stored as strings
            return decoded_message
        else:
            print("No message found in the employee's Redis queue")
            return None
    except redis.RedisError as e:
        print(f"Error while retrieving messages from Redis: {e}")
        return None
    except Exception:
        print(
            "Something went wrong while accessing messages from Redis database"
        )
        return None

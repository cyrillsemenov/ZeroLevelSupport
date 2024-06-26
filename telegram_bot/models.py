import json
import re
from enum import Enum

import yaml
from asgiref.sync import sync_to_async
from django.db.models import (
    CASCADE,
    BigIntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    Model,
    TextField,
    URLField,
)
from django.forms import model_to_dict


class GroupNames(Enum):
    ADMIN = "Admin"
    USER = "User"
    BANNED = "Banned"


class Group(Model):
    name = CharField(max_length=16)
    banned = BooleanField()
    is_admin = BooleanField()


class User(Model):
    tg_id = BigIntegerField(primary_key=True)
    groups = ForeignKey(Group, related_name="users", on_delete=CASCADE)

    @property
    def is_banned(self):
        return self.group.banned

    def assign_user_to_group(self, group_name: GroupNames):
        group, _ = Group.objects.get_or_create(name=group_name.value)
        self.groups = group
        self.save()

    async def a_assign_user_to_group(self, group_name: GroupNames):
        await sync_to_async(self.assign_user_to_group)(group_name)


class Status(Model):
    name = CharField(
        max_length=255
    )  # Don't forget to specify max_length for CharFields

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "statuses"


class Service(Model):
    name = CharField(max_length=255)
    status = ForeignKey(Status, related_name="services", on_delete=CASCADE)

    def __str__(self):
        return f"{self.name} (Status: {self.status.name})"


class Report(Model):
    provider_value = CharField(max_length=255, blank=True, null=True)
    region_value = CharField(max_length=255, blank=True, null=True)
    url = URLField(blank=True, null=True)
    comment_value = TextField(blank=True, null=True)
    status = ForeignKey(Status, related_name="reports", on_delete=CASCADE, null=True)
    time = DateTimeField(auto_now=True)
    # is_vpn_used = BooleanField(default=False, blank=True)
    is_vpn_used = CharField(max_length=255, blank=True, null=True)
    vpn_provider = CharField(max_length=255, blank=True, null=True)
    vpn_protocol = CharField(max_length=255, blank=True, null=True)
    services = ManyToManyField(Service, blank=True)

    def __str__(self):
        return f"Report at {self.time}"

    @staticmethod
    def convert_keys_to_snake_case(data):
        snake_case_data = {}
        for key, value in data.items():
            snake_case_key = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
            snake_case_data[snake_case_key] = value
        return snake_case_data

    @classmethod
    def create_report_instance(cls, data, is_snake_case=False, **kwargs):
        """General method to create a Report instance from provided data."""
        if not is_snake_case:
            data = cls.convert_keys_to_snake_case(data)

        status_name = data.pop("status", None)
        services_data = data.pop("services", [])
        report_instance = cls(**data)
        report_instance.save()

        if status_name:
            status, _ = Status.objects.get_or_create(name=status_name)
            report_instance.status = status
            report_instance.save()

        for service_name in services_data:
            service, _ = Service.objects.get_or_create(name=service_name)
            report_instance.services.add(service)

        return report_instance

    @classmethod
    def from_camel_case_yaml(cls, yaml_data, **kwargs):
        """Creates a Report instance from camelCase YAML data."""
        parsed_data = yaml.safe_load(yaml_data)
        return cls.create_report_instance(parsed_data, **kwargs)

    @classmethod
    def from_yaml(cls, yaml_data, **kwargs):
        """Creates a Report instance directly from YAML data assuming snake_case keys."""
        parsed_data = yaml.safe_load(yaml_data)
        return cls.create_report_instance(parsed_data, is_snake_case=True, **kwargs)

    @classmethod
    def from_json(cls, json_data, **kwargs):
        """Creates a Report instance from camelCase JSON data."""
        parsed_data = json.loads(json_data)
        return cls.create_report_instance(parsed_data, is_snake_case=False, **kwargs)

    def to_dict(self):
        """
        Converts the Report instance into a dictionary including handling for
        ManyToMany and ForeignKey fields.
        """
        data = model_to_dict(self, exclude=["services", "status"])
        data["status"] = str(self.status.name) if self.status else None
        data["services"] = list(self.services.all().values_list("name", flat=True))
        return data

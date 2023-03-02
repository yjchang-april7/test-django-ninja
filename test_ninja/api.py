from datetime import date
from typing import List

from django.db import models
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema, Header, Query, Form, UploadedFile, File
from ninja.parser import Parser
from orjson import orjson
from pydantic import Field


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


api = NinjaAPI(parser=ORJSONParser())


@api.get('/hello')
def hello(request, name=None):
    return f"Hello {name or 'world~'}"


@api.get('/math/{a}and{b}')
def math(request, a: int, b: int):
    return {"a+b": (a + b), "a*b": (a * b)}


class Error(Schema):
    message: str


class CommonSchema(Schema):
    code: int
    msg: str


class TestSchema(CommonSchema):
    name: str = 'world'


@api.post('/test', response={200: TestSchema, 403: Error})
def test_post(request, data: TestSchema, x: str = Header(default="x-header-value")):
    data.code = 100
    data.msg = f"test message {x}"
    return data


# class Department(models.Model):
#     title = models.CharField(max_length=100)
#
#
# class Employee(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     department = models.ForeignKey(Department)
#     birthdate = models.DateField(null=True, blank=True)
#
#
#
# class EmployeeIn(Schema):
#     first_name: str
#     last_name: str
#     department_id: int = None
#     birthdate: date = None
#
#
# @api.put("/employees/{employee_id}")
# def update_employee(request, employee_id: int, payload: EmployeeIn):
#     employee = get_object_or_404(Employee, id=employee_id)
#     # Here we used the payload.dict method to set all object attributes:
#     for attr, value in payload.dict().items():
#         setattr(employee, attr, value)
#     employee.save()
#     return {"success": True}

class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(None, alias="categories")


@api.get("/filter/{item_id}")
def events(request, item_id: int, filters: Filters = Query(...)):
    return {"filters": filters.dict()}


@api.post("/filter/{item_id}")
def filters(request, item_id: int, filters: Filters, q:str):
    return {"filters": filters.dict()}


class UserDetails(Schema):
    first_name: str
    last_name: str
    birthdate: date


@api.post('/user-form')
def create_user_form(request, details: UserDetails = Form(...), file: UploadedFile = File(...)):
    return [details.dict(), file.name]

@api.post('/user-json')
def create_user_json(request, details: UserDetails, file: UploadedFile = File(...)):
    return [details.dict(), file.name]


'''
snake case의 필드명을 camel case형으로 스키마에서 alias 자동 생성 예제
'''
def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class CamelModelSchema(Schema):
    str_field_name: str
    float_field_name: float

    class Config(Schema.Config):
        alias_generator = to_camel


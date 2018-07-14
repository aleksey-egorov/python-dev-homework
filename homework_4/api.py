#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import re
import json
import datetime
import logging
import hashlib
import random
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from scoring import get_score
from scoring import get_interests


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


FIELD_NULLABLE_ERROR = 1
FIELD_REQUIRED_ERROR = 2
FIELD_CHAR_ERROR = 3
FIELD_EMAIL_ERROR = 4
FIELD_PHONE_ERROR = 5
FIELD_GENDER_ERROR = 6
FIELD_DATE_ERROR = 7
FIELD_BIRTHDAY_ERROR = 8
FIELD_LIST_ERROR = 9
FIELD_IDS_ERROR = 10
FIELD_ARG_ERROR = 11

REQUEST_BAD_HANDLER_ERROR = 12
REQUEST_ARG_ERROR = 13
REQUEST_AUTH_ERROR = 14

FIELD_REQUEST_ERRORS = {
    FIELD_NULLABLE_ERROR: "This field is not nullable",
    FIELD_REQUIRED_ERROR: "This field is required",
    FIELD_CHAR_ERROR: "This field should be a string",
    FIELD_EMAIL_ERROR: "This field should contain '@'",
    FIELD_PHONE_ERROR: "This field should be 7XXXXXXXXXX",
    FIELD_GENDER_ERROR: "This field should be numeric [0,1,2]",
    FIELD_DATE_ERROR: "This field should be in format 'DD.MM.YYYY'",
    FIELD_BIRTHDAY_ERROR: "This field should be in format 'DD.MM.YYYY', not earlier than 70 years from current date",
    FIELD_LIST_ERROR: "This field should be a list",
    FIELD_IDS_ERROR: "This field should contain only positive numbers",
    FIELD_ARG_ERROR: "This field should be a dict",

    REQUEST_BAD_HANDLER_ERROR : "No method specified",
    REQUEST_ARG_ERROR : "Arguments should contain at least one pair of not-null values: phone/email, first_name/last_name, birthday/gender",
    REQUEST_AUTH_ERROR : "User authorization error"
}

ARGUMENTS_VALID = "Arguments are valid"
ARGUMENTS_INVALID = "Arguments invalid"
USER_AUTHORIZED = "User authorized"

phone_pattern = re.compile(r'7(\d{10})')


class Field(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, required=True, nullable=False):
        self.errors = []
        self.value = None
        self.null_value = ''
        self.required = required
        self.nullable = nullable

    def set(self, value):
        if not self.nullable and value == self.null_value:
            self.errors.append(FIELD_NULLABLE_ERROR)
        elif self.required and value == None:
            self.errors.append(FIELD_REQUIRED_ERROR)
        else:
            self.value = value

    def set_null(self):
        self.value = self.null_value

    @property
    def is_valid(self):
        return not self.errors


class CharField(Field):

    def set(self, value):
        super().set(value)
        if not value == self.null_value and not value == None and not isinstance(value, str):
            self.errors.append(FIELD_CHAR_ERROR)
            self.set_null()


class ArgumentsField(Field):

    def __init__(self, required, nullable):
       super().__init__(required=required, nullable=nullable)
       self.value = {}
       self.null_value = {}

    def set(self, value):
        super().set(value)
        if not value == self.null_value and not isinstance(value, dict):
            self.errors.append(FIELD_ARG_ERROR)
            self.set_null()


class EmailField(CharField):

    def set(self, value):
        super().set(value)
        if not value == self.null_value and not '@' in value:
            self.errors.append(FIELD_EMAIL_ERROR)
            self.set_null()


class PhoneField(Field):

    def set(self, value):
        super().set(value)
        if not value == self.null_value and not re.match(phone_pattern, str(value)):
            self.errors.append(FIELD_PHONE_ERROR)
            self.set_null()


class DateField(Field):

    def set(self, value):
        super().set(value)
        if not value == self.null_value:
            try:
                datetime.datetime.strptime(value, '%d.%m.%Y')
            except ValueError:
                self.errors.append(FIELD_DATE_ERROR)
                self.set_null()


class BirthDayField(DateField):

    def set(self, value):
        super().set(value)
        if not value == self.null_value:
            try:
                bdate = datetime.datetime.strptime(value, '%d.%m.%Y')
                if datetime.datetime.now().year - bdate.year > 70:
                    self.errors.append(FIELD_BIRTHDAY_ERROR)
                    self.set_null()
            except:
                pass


class GenderField(Field):

    def set(self, value):
        super().set(value)
        if not value == self.null_value and value not in GENDERS:
            self.errors.append(FIELD_GENDER_ERROR)
            self.set_null()


class ClientIDsField(Field):

    def __init__(self, required, nullable):
        super().__init__(required=required, nullable=nullable)
        self.value = []
        self.null_value = []

    def set(self, value):
        super().set(value)
        if not isinstance(value, list):
            self.errors.append(FIELD_LIST_ERROR)
            self.set_null()
        if not all(isinstance(v, int) and v >= 0 for v in value):
            self.errors.append(FIELD_IDS_ERROR)
            self.set_null()


class RequestMetaclass(type):

    def __new__(meta, name, bases, attrs):
        new_class = super().__new__(meta, name, bases, attrs)
        fields = []
        for field_name, field in attrs.items():
            if isinstance(field, Field):
                field._name = field_name
                fields.append((field_name, field))
        new_class.fields = fields
        return new_class


class Request(metaclass=RequestMetaclass):

    def __init__(self, set_values, **kwargs):
        self.errors = []
        self.request_handler = None
        self.fields_list = []
        self.valid_fields = []

        for field_name, value in kwargs.items():
            setattr(self, field_name + '_value', value)
            self.fields_list.append(field_name)
        for key, field in self.fields:
            field.set_null()
            field.errors = []

        if set_values:
            self.set_values(kwargs)

    def set_values(self, arguments):
        for key, field in self.fields:
            if key in arguments:
                field.set(arguments[key])
            else:
                field.set(None)

    def check_arguments(self):
        errors = 0
        for key, field in self.fields:
            if not field.is_valid:
                errors += 1
                for err in field.errors:
                    logging.error("Field '{}' error: {}".format(key, FIELD_REQUEST_ERRORS[err]))
            if not field.value == field.null_value:
                self.valid_fields.append(key)

    @property
    def is_valid(self):

        field_err = len(self.errors)
        for key, field in self.fields:
            field_err += len(field.errors)

        rh_field_err = 0
        if self.request_handler:
            rh_field_err = len(self.request_handler.errors)
            for key, field in self.request_handler.fields:
                rh_field_err += len(field.errors)

        if field_err == 0 and rh_field_err == 0:
            return True
        return False

    def get_errors_message(self, global_error_id):
        msg = ERRORS[global_error_id] + " : "
        for key, field in self.fields:
            for error in field.errors:
                msg += "Field '{}' error '{}'. ".format(field._name, FIELD_REQUEST_ERRORS[error])

        if self.request_handler:
            for key, field in self.request_handler.fields:
                for error in field.errors:
                    msg += "Argument '{}' error '{}'. ".format(field._name, FIELD_REQUEST_ERRORS[error])

        return msg


class ClientsInterestsRequest(Request):

    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)
    nclients = 0

    def check_arguments(self):
        super().check_arguments()
        self.nclients = len(self.client_ids.value)

    def get_result(self, is_admin, store):
        results = {}
        if not self.client_ids == None:
            for client in self.client_ids.value:
                results[client] = get_interests(store, client)
        return results, OK

    def update_context(self, ctx):
        ctx["nclients"] = self.nclients


class OnlineScoreRequest(Request):

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def check_arguments(self):
        super().check_arguments()

        field_pairs = [("phone", "email"), ("first_name", "last_name"), ("gender", "birthday")]
        if not any(all(name in self.valid_fields for name in pair) for pair in field_pairs):
            logging.error(FIELD_REQUEST_ERRORS[REQUEST_ARG_ERROR])
            self.errors.append(REQUEST_ARG_ERROR)

        if self.is_valid:
            logging.info(ARGUMENTS_VALID)
        else:
            logging.error(ARGUMENTS_INVALID)

    def get_result(self, is_admin, store):
        if is_admin:
            score = 42
        else:
            try:
                score = get_score(store, self.phone.value, self.email.value, self.birthday.value, self.gender.value,
                                self.first_name.value, self.last_name.value)
            except:
                return {"message" :  self.get_errors_message(INTERNAL_ERROR)}, INTERNAL_ERROR

        return {"score": score}, OK

    def update_context(self, ctx):
        ctx["has"] = self.valid_fields


class MethodRequest(Request):

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method= CharField(required=True, nullable=False)

    def process_request(self, ctx, store):
        handlers = {
            "clients_interests": ClientsInterestsRequest,
            "online_score": OnlineScoreRequest,
        }

        try:
            args = self.arguments.value
            self.request_handler = handlers[self.method.value](False, **args)
        except KeyError:
            self.errors.append(REQUEST_BAD_HANDLER_ERROR)

        if self.request_handler:
            self.request_handler.set_values(self.arguments.value)
            self.request_handler.check_arguments()
            self.request_handler.update_context(ctx)

        self.check_arguments()
        self.check_auth()

        if not self.is_good_request:
            return {"message": self.get_errors_message(INVALID_REQUEST)}, INVALID_REQUEST
        if not self.is_authorized:
            return {"message": self.get_errors_message(FORBIDDEN)}, FORBIDDEN
        if not self.is_valid:
            return {"message": self.get_errors_message(INVALID_REQUEST)}, INVALID_REQUEST

        return self.request_handler.get_result(self.is_admin, store)


    @property
    def is_admin(self):
        return self.login.value == ADMIN_LOGIN

    @property
    def is_authorized(self):
        return not REQUEST_AUTH_ERROR in self.errors

    @property
    def is_good_request(self):
        return not REQUEST_BAD_HANDLER_ERROR in self.errors

    def check_auth(self):
        if self.is_admin:
            digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
        else:
            ac = self.account.value
            if not ac:
                ac = ''
            lo = self.login.value
            if not lo:
                lo = ''
            digest = hashlib.sha512((ac + lo + SALT).encode('utf-8')).hexdigest()

        if digest == self.token.value:
            logging.info(USER_AUTHORIZED)
        else:
            logging.error(REQUEST_AUTH_ERROR)
            self.errors.append(REQUEST_AUTH_ERROR)


def method_handler(request, ctx, store):
    method_request = MethodRequest(True, **request['body'])
    response, code = method_request.process_request(ctx, store)
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            logging.exception("Bad request")
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)

        encoded = json.dumps(r).encode('utf-8')
        self.wfile.write(encoded)
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import re
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from constants import *
from scoring import get_score
from scoring import get_interests

phone_pattern = re.compile(r'7(\d{10})')


class ValidationError(Exception):
    def __init__(self, field, error):
        logging.error("Field '{}' error: {}".format(field, FIELD_REQUEST_ERRORS[error]))


class Field(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, required=True, nullable=False):
        self.name = ''
        self.value = None
        self.null_value = ''
        self.required = required
        self.nullable = nullable

    def _valid_error(self, value):
        if not self.nullable and value == self.null_value:
            raise ValidationError(self.name, FIELD_NULLABLE_ERROR)
        elif self.required and value == None:
            raise ValidationError(self.name, FIELD_REQUIRED_ERROR)

    def set(self, value):
        self._valid_error(value)
        self.value = value

    def set_null(self):
        self.value = self.null_value

    @property
    def is_empty(self):
        return self.value == None or self.value == self.null_value


class CharField(Field):

    def set(self, value):
        super().set(value)
        if not self.is_empty and not isinstance(value, str):
            raise ValidationError(self.name, FIELD_CHAR_ERROR)


class ArgumentsField(Field):

    def __init__(self, required, nullable):
       super().__init__(required=required, nullable=nullable)
       self.value = {}
       self.null_value = {}

    def set(self, value):
        super().set(value)
        if not self.is_empty and not isinstance(value, dict):
            raise ValidationError(self.name, FIELD_ARG_ERROR)


class EmailField(CharField):

    def set(self, value):
        super().set(value)
        if not self.is_empty and isinstance(value, str):
            if not '@' in value:
                raise ValidationError(self.name, FIELD_EMAIL_ERROR)


class PhoneField(Field):

    def set(self, value):
        super().set(value)
        if not self.is_empty and not re.match(phone_pattern, str(value)):
            raise ValidationError(self.name, FIELD_PHONE_ERROR)


class DateField(Field):

    def set(self, value):
        super().set(value)
        if not self.is_empty:
            try:
                datetime.datetime.strptime(value, '%d.%m.%Y')
            except:
                raise ValidationError(self.name, FIELD_DATE_ERROR)


class BirthDayField(DateField):

    def set(self, value):
        super().set(value)
        if not self.is_empty :
            if datetime.datetime.now().year - datetime.datetime.strptime(value, '%d.%m.%Y').year > 70:
                raise ValidationError(self.name, FIELD_BIRTHDAY_ERROR)


class GenderField(Field):

    def set(self, value):
        super().set(value)
        if not self.is_empty:
            if isinstance(value, int):
                if value not in GENDERS:
                    raise ValidationError(self.name, FIELD_GENDER_ERROR)
            else:
                raise ValidationError(self.name, FIELD_NUMERIC_ERROR)


class ClientIDsField(Field):

    def __init__(self, required, nullable):
        super().__init__(required=required, nullable=nullable)
        self.value = []
        self.null_value = []

    def set(self, value):
        super().set(value)
        if not self.is_empty:
            if not isinstance(value, list):
                raise ValidationError(self.name, FIELD_LIST_ERROR)
            if not all(isinstance(v, int) and v >= 0 for v in value):
                raise ValidationError(self.name, FIELD_IDS_ERROR)


class RequestMetaclass(type):

    def __new__(meta, name, bases, attrs):
        new_class = super().__new__(meta, name, bases, attrs)
        fields = []
        for field_name, field in attrs.items():
            if isinstance(field, Field):
                field.name = field_name
                fields.append((field_name, field))
        new_class.fields = fields
        return new_class


class Request(metaclass=RequestMetaclass):

    def __init__(self, **kwargs):
        self.request_handler = None
        self.fields_list = []
        self.valid_fields = []

        for field_name, value in kwargs.items():
            self.fields_list.append(field_name)
        for key, field in self.fields:
            field.set_null()

    def set_values(self, arguments):
        for key, field in self.fields:
            if key in arguments:
                value = arguments[key]
            else:
                value = None
            field.set(value)

    def err_msg(self, global_error_id, error):
        msg = ERRORS[global_error_id]
        if isinstance(error, tuple):
            try:
                msg += ": {} error - {}".format(error[0], FIELD_REQUEST_ERRORS[error[1]])
            except:
                pass
        return msg


class ClientsInterestsRequest(Request):

    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def get_result(self, is_admin, store):
        results = {}
        if not self.client_ids == None:
            for client in self.client_ids.value:
                results[client] = get_interests(store, client)
        return results, OK

    def check_arguments(self):
        pass

    def update_context(self, ctx):
        ctx["nclients"] = len(self.client_ids.value)


class OnlineScoreRequest(Request):

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def check_arguments(self):
        for key, field in self.fields:
            if not field.is_empty:
                self.valid_fields.append(key)

        field_pairs = [("phone", "email"), ("first_name", "last_name"), ("gender", "birthday")]
        if not any(all(name in self.valid_fields for name in pair) for pair in field_pairs):
            raise ValidationError('arguments', REQUEST_ARG_ERROR)

        logging.info(ARGUMENTS_VALID)

    def get_result(self, is_admin, store):
        if is_admin:
            score = 42
        else:
            try:
                score = get_score(store, self.phone.value, self.email.value, self.birthday.value, self.gender.value,
                                self.first_name.value, self.last_name.value)
            except:
                return {"message" :  self.err_msg(INTERNAL_ERROR, {})}, INTERNAL_ERROR

        return {"score": score}, OK

    def update_context(self, ctx):
        ctx["has"] = self.valid_fields


class MethodRequest(Request):

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method= CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login.value == ADMIN_LOGIN

    def check_auth(self):
        if self.is_admin:
            digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
        else:
            ac = self.account.value or ""
            lo = self.login.value or ""
            digest = hashlib.sha512((ac + lo + SALT).encode('utf-8')).hexdigest()

        if digest == self.token.value:
            logging.info(USER_AUTHORIZED)
        else:
            raise ValidationError('token', REQUEST_AUTH_ERROR)


def method_handler(request, ctx, store):
    method = MethodRequest(**request['body'])
    try:
        method.set_values(request['body'])
    except Exception as error:
        return {"message": method.err_msg(INVALID_REQUEST, error.args)}, INVALID_REQUEST

    handlers = {
        "clients_interests": ClientsInterestsRequest,
        "online_score": OnlineScoreRequest,
    }

    try:
        args = method.arguments.value
        method.request_handler = handlers[method.method.value](**args)
    except:
        return {"message": method.err_msg(INVALID_REQUEST, ('method', REQUEST_BAD_HANDLER_ERROR))}, INVALID_REQUEST

    try:
        method.check_auth()
    except Exception as error:
        print ("ER=", error.args)
        return {"message": method.err_msg(FORBIDDEN, error.args)}, FORBIDDEN

    if method.request_handler:
        try:
            method.request_handler.set_values(method.arguments.value)
            method.request_handler.check_arguments()
        except Exception as error:
            return {"message": method.err_msg(INVALID_REQUEST, error.args)}, INVALID_REQUEST

        method.request_handler.update_context(ctx)

    return method.request_handler.get_result(method.is_admin, store)


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

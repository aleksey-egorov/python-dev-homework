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
    pass


class Field(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, required=True, nullable=False):
        self.errors = []
        self.value = None
        self.null_value = ''
        self.required = required
        self.nullable = nullable

    def _valid_error(self, value):
        if not self.nullable and value == self.null_value:
            return FIELD_NULLABLE_ERROR
        elif self.required and value == None:
            return FIELD_REQUIRED_ERROR

    def set(self, value):
        err = self._valid_error(value)
        if err == None:
            self.value = value
        else:
            return err

    def set_null(self):
        self.value = self.null_value

    @property
    def is_valid(self):
        return not self.errors

    @property
    def is_empty(self):
        return self.value == None or self.value == self.null_value

    def show_error(self):
        pass


class CharField(Field):

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty and not isinstance(value, str):
            return FIELD_CHAR_ERROR
        return err


class ArgumentsField(Field):

    def __init__(self, required, nullable):
       super().__init__(required=required, nullable=nullable)
       self.value = {}
       self.null_value = {}

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty and not isinstance(value, dict):
            return FIELD_ARG_ERROR
        return err


class EmailField(CharField):

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty and isinstance(value, str):
            if not '@' in value:
                return FIELD_EMAIL_ERROR
        return err


class PhoneField(Field):

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty and not re.match(phone_pattern, str(value)):
            return FIELD_PHONE_ERROR
        return err


class DateField(Field):

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty:
            try:
                datetime.datetime.strptime(value, '%d.%m.%Y')
            except:
                return FIELD_DATE_ERROR
        return err


class BirthDayField(DateField):

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty :
            try:
                bdate = datetime.datetime.strptime(value, '%d.%m.%Y')
                if datetime.datetime.now().year - bdate.year > 70:
                    return FIELD_BIRTHDAY_ERROR
            except:
                pass
        return err


class GenderField(Field):

    def set(self, value):
        err = super().set(value)
        if err == None and not self.is_empty:
            if isinstance(value, int):
                if value not in GENDERS:
                    return FIELD_GENDER_ERROR
            else:
                return FIELD_NUMERIC_ERROR
        return err


class ClientIDsField(Field):

    def __init__(self, required, nullable):
        super().__init__(required=required, nullable=nullable)
        self.value = []
        self.null_value = []

    def set(self, value):
        err = super().set(value)
        print ("cliid=", err)
        if err == None and not self.is_empty:
            if not isinstance(value, list):
                return FIELD_LIST_ERROR
            if not all(isinstance(v, int) and v >= 0 for v in value):
                return FIELD_IDS_ERROR
        return err


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
        field_errors = {}
        for key, field in self.fields:
            if key in arguments:
                value = arguments[key]
            else:
                value = None
            field_error = field.set(value)
            if not field_error == None:
                field_errors[key] = field_error
        return field_errors

    def check_arguments(self):
        errors = 0
        for key, field in self.fields:
            if not field.is_valid:
                errors += 1
                for err in field.errors:
                    logging.error("Field '{}' error: {}".format(key, FIELD_REQUEST_ERRORS[err]))
            if not field.value == None:
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
        for error in self.errors:
            msg += "Request error '{}'. ".format(FIELD_REQUEST_ERRORS[error])

        for key, field in self.fields:
            for error in field.errors:
                msg += "Field '{}' error '{}'. ".format(field._name, FIELD_REQUEST_ERRORS[error])

        if self.request_handler:
            for key, field in self.request_handler.fields:
                for error in field.errors:
                    msg += "Argument '{}' error '{}'. ".format(field._name, FIELD_REQUEST_ERRORS[error])

        return msg

    def err_msg(self, global_error_id, field_errors):
        msg = ERRORS[global_error_id] + " : "
        #for error in self.errors:
        #    msg += "Request error '{}'. ".format(FIELD_REQUEST_ERRORS[error])
        for key in field_errors:
            msg += "Field '{}' error '{}'. ".format(key, FIELD_REQUEST_ERRORS[field_errors[key]])

        #if self.request_handler:
        #    for key, field in self.request_handler.fields:
        #        for error in field.errors:
        #            msg += "Argument '{}' error '{}'. ".format(field._name, FIELD_REQUEST_ERRORS[error])

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

    @property
    def is_admin(self):
        return self.login.value == ADMIN_LOGIN

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
            return True
        else:
            logging.error(FIELD_REQUEST_ERRORS[REQUEST_AUTH_ERROR])
            return False


def method_handler(request, ctx, store):
    method = MethodRequest(True, **request['body'])

    handlers = {
        "clients_interests": ClientsInterestsRequest,
        "online_score": OnlineScoreRequest,
    }

    try:
        args = method.arguments.value
        method.request_handler = handlers[method.method.value](False, **args)

        if method.request_handler:
            field_errors = method.request_handler.set_values(method.arguments.value)
            if not field_errors == {}:
                return {"message": method.get_errors_message(INVALID_REQUEST)}, INVALID_REQUEST
            method.request_handler.check_arguments()
            method.request_handler.update_context(ctx)

        method.check_arguments()

        if not method.check_auth():
            return {"message": method.err_msg(FORBIDDEN, {'token': REQUEST_AUTH_ERROR})}, FORBIDDEN
        if not method.is_valid:
            return {"message": method.get_errors_message(INVALID_REQUEST)}, INVALID_REQUEST
        if method.arguments.value == {}:
            return {"message": method.err_msg(INVALID_REQUEST, {'arguments': REQUEST_EMPTY_ARGS_ERROR})}, INVALID_REQUEST

        return method.request_handler.get_result(method.is_admin, store)

    except:
        return {"message": method.err_msg(INVALID_REQUEST, {'method': REQUEST_BAD_HANDLER_ERROR})}, INVALID_REQUEST


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

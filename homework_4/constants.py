
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
FIELD_NUMERIC_ERROR = 15

REQUEST_EMPTY_ARGS_ERROR = 16
REQUEST_BAD_HANDLER_ERROR = 12
REQUEST_ARG_ERROR = 13
REQUEST_AUTH_ERROR = 14

FIELD_REQUEST_ERRORS = {
    FIELD_NULLABLE_ERROR: "This field is not nullable",
    FIELD_REQUIRED_ERROR: "This field is required",
    FIELD_CHAR_ERROR: "This field should be a string",
    FIELD_EMAIL_ERROR: "This field should contain '@'",
    FIELD_PHONE_ERROR: "This field should be 7XXXXXXXXXX",
    FIELD_GENDER_ERROR: "This field should be numeric: 0,1,2",
    FIELD_DATE_ERROR: "This field should be in format 'DD.MM.YYYY'",
    FIELD_BIRTHDAY_ERROR: "This field should be in format 'DD.MM.YYYY', not earlier than 70 years from current date",
    FIELD_LIST_ERROR: "This field should be a list",
    FIELD_IDS_ERROR: "This field should contain only positive numbers",
    FIELD_ARG_ERROR: "This field should be a dict",
    FIELD_NUMERIC_ERROR: "This field should be numeric",

    REQUEST_EMPTY_ARGS_ERROR : "Request argumnts empty",
    REQUEST_BAD_HANDLER_ERROR : "No method specified",
    REQUEST_ARG_ERROR : "Arguments should contain at least one pair of not-null values: phone/email, first_name/last_name, birthday/gender",
    REQUEST_AUTH_ERROR : "User authorization error"
}

ARGUMENTS_VALID = "Arguments are valid"
ARGUMENTS_INVALID = "Arguments invalid"
USER_AUTHORIZED = "User authorized"
""" This module implements the HIL client library. """

from urlparse import urljoin
import json
import re
import functools
from hil.errors import BadArgumentError


class FailedAPICallException(Exception):
    """An exception indicating that the server returned an error.

    Attributes:

        error_type (str): the type of the error. This will be the name of
            one of the subclasses of APIError in hil.errors.
        message (str): a human readble description of the error.
    """

    def __init__(self, error_type, message):
        Exception.__init__(self, message)
        self.error_type = error_type


class ClientBase(object):
    """Main class which contains all the methods to

    -- ensure input complies to API requisites
    -- generates correct format for server API on behalf of the client
    -- parses output from received from the server.
    In case of errors recieved from server, it will generate appropriate
    appropriate message.
    """

    def __init__(self, endpoint, httpClient):
        """ Initialize an instance of the library with following parameters.

       endpoint: stands for the http endpoint eg. endpoint=http://127.0.0.1
       sess: depending on the authentication backend (db vs keystone) the
       parameters required to make up the session vary.
       user: username as which you wish to connect to HIL
       Currently all this information is fetched from the user's environment.
        """
        self.endpoint = endpoint
        self.httpClient = httpClient

    def object_url(self, *args):
        """Generate URL from combining endpoint and args as relative URL"""
        rel = "/".join(args)
        url = urljoin(self.endpoint, rel)
        return url

    def check_response(self, response):
        """
        Check the response from an API call, and do any needed error handling

        Returns the body of the response as (parsed) JSON, or None if there
        was no body. Raises a FailedAPICallException on any non 2xx status.
        """
        if 200 <= response.status_code < 300:
            try:
                return json.loads(response.content)
            except ValueError:  # No JSON request body; typical
                                # For methods PUT, POST, DELETE
                return
        try:
            e = json.loads(response.content)
            raise FailedAPICallException(
                error_type=e['type'],
                message=e['msg'],
            )
        # Catching 404's that do not return JSON
        except ValueError:
            return response.content

    def find_reserved(self, string):
        """Returns a list of illegal characters in a string"""
        p = r"[^A-Za-z0-9 $_.+!*'(),-]+"
        return list(x for l in re.findall(p, string) for x in l)

    def find_reserved_w_slash(self, string):
        """Returns a list of illegal characters in a string
        excluding `/` for channels and ports"""
        p = r"[^A-Za-z0-9 /$_.+!*'(),-]+"
        return list(x for l in re.findall(p, string) for x in l)

def check_reserved(*args, **kwargs):
    """Returns a list of illegal characters in a string"""
    slashes_ok = kwargs.pop('slashes_ok')
    strings = kwargs.pop('strings')
    types = kwargs.pop('types')
    for string in strings:
        if string in slashes_ok:
            p = r"[^A-Za-z0-9 /$_.+!*'(),-]+"
        else:
            p = r"[^A-Za-z0-9 $_.+!*'(),-]+"
        bad_chars = list(x for l in re.findall(p, string) for x in l)
        #if bool(bad_chars):
            #msg = types. + " may not contain " + bad_chars
            #raise BadArgumentError(msg)

def check_reserved_chars(*outer_args, **outer_kwargs):
    """Wraps Client lib functions to check for illegal characters
    and dynamically report the error by the offending argument(s)"""
    #if f is None:
    #    return functools.partial(check_reserved_chars, slashes_ok=slashes_ok)
    #@functools.wraps(f)
    def wrapper(f):
        #check_reserved(*args, **kwargs)
        #print(kwargs.pop('slashes_ok'))
        #print("In wrapper " + str(list(args)))
        #print("In wrapper " + str(list(kwargs)))
        def reserved_wrap(*args, **kwargs):
            #raise BadArgumentError(list(kwargs))
            #print("In reserved_wrap " + str(list(args)))
            #print("In reserved_wrap " + str(list(kwargs)))
            #print("In reserved_wrap " + str(list(outer_args)))
            #print("In reserved_wrap " + str(list(outer_kwargs)))
            strings = list(filter(lambda elm: isinstance(elm, str), args))
            #slashes_ok = outer_kwargs.pop('slashes_ok')
            types_dict = dict()
            print(strings)
            print(list(outer_args))
            for arg, out_arg in zip(strings, outer_args):
                types_dict.update({out_arg:arg})
            print(types_dict)
            #check_reserved(strings=strings,
            #               types=outer_args,
            #               slashes_ok=slashes_ok)
        return reserved_wrap
    return wrapper

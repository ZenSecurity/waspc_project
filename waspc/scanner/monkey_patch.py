from w3af.core.controllers.exceptions import BaseFrameworkException


# preventing dirty scheme "file:///etc/passwd", but in w3af scanner it used for reading targets from the file
# (it's not a bug it's a feature)
def w3af_core_target_verify_url(self, target_url, file_target=True):
    """
    Verify if the URL is valid and raise an exception if w3af doesn't
    support it.

    :param target_url: The target URL object to check if its valid or not.
    :return: None. A BaseFrameworkException is raised on error.
    """
    protocol = target_url.get_protocol()

    is_http = protocol in ('http', 'https') and target_url.is_valid_domain()

    if not is_http:
        msg = ('Invalid format for target URL "%s", you have to specify '
               'the protocol (http/https) and a domain or IP address.'
               ' Examples: http://host.tld/ ; https://127.0.0.1/ .')
        raise BaseFrameworkException(msg % target_url)

    return True

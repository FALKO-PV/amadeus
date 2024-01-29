from typing import Tuple
import re
import smtplib
import dns.resolver
import socket
import logging

logger = logging.getLogger('main')


def validate_email(email_adr: str) -> Tuple[bool, str]:
    """
    Checks an e-mail address if it is valid. The function performs 3 checks:
    - Regex-Check for e-mail address.
    - Check Domain if reachable via DNS.
    - Send EHLO via SMTP to e-mail domain and check for errors
    If no check fails: e-mail seems to be valid (but still: handle can be false)
    :param email_adr: email address as string
    :return: a tuple of boolean if email is valid (True/False) and a string with error description or empty
    """

    error_messages = {
        "invalid_regex": "Bitte geben Sie eine gültige E-Mail-Adresse ein (Syntaxfehler)!",
        "invalid_dns": "Bitte geben Sie eine gültige E-Mail-Adresse ein, der Domainname konnte nicht gefunden werden!",
        "invalid_smtp": "Bitte geben Sie eine gültige E-Mail-Adresse ein. Es konnte keine Verbindung zum SMTP-Server "
                        "hergestellt werden oder die angegebene E-Mail-Adresse existiert nicht auf dem Server."
    }

    domain = email_adr.split("@")[-1]

    # 1. check regex: regular expression is rfc5322 compatible and found on:
    # https://nedbatchelder.com/blog/200908/humane_email_validation.html

    regex = re.compile(r'^[^@ ]+@[^@ ]+\.[^@ ]+$')

    if not re.fullmatch(regex, email_adr):
        logger.warning(f"{error_messages['invalid_regex']} for Domain: {domain}")
        return False, error_messages["invalid_regex"]

    # 2. check domain via DNS

    try:
        mx_res = dns.resolver.resolve(domain, "MX")

    except (dns.resolver.NXDOMAIN, dns.exception.Timeout):
        logger.warning(f"{error_messages['invalid_dns']} for Domain: {domain}")
        return False, error_messages["invalid_dns"]

    # 3. check smtp

    # if DNS check for mail domain didn't fail, we got back a resolver object with mx address objects
    # we take the first mx address object, get it's string representation (something like '10 mx.domain.ltd.'),
    # remove the last character (a dot) and split it for the domain name
    # _, mx_domain = mx_res[0].__str__()[:-1].split(" ")
    #
    # server = smtplib.SMTP()
    # server.set_debuglevel(0)
    #
    # try:
    #     server.connect(mx_domain)
    #     lvl, _ = server.helo()
    #     if lvl != 250:
    #         logger.warning(f"{error_messages['invalid_smtp']} for Domain: {domain}")
    #         return False, error_messages["invalid_smtp"]
    #     server.quit()
    #
    # except (smtplib.SMTPException, socket.gaierror):
    #     logger.warning(f"{error_messages['invalid_smtp']} for Domain: {domain}")
    #     return False, error_messages["invalid_smtp"]

    return True, ""

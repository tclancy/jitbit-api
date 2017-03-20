import json
import logging

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger("jitbit")


class JitBitAPI(object):
    def __init__(self, api_url, username, password):
        self.api_url = api_url
        self.authentication = HTTPBasicAuth(username, password)

        if not self.test_credentials():
            logger.error("Authorization failed for JitBit API")
            raise ValueError("Authorization failed, please check your credentials")

    def _make_request(self, method, data=None):
        url = "%s/api/%s" % (self.api_url, method)
        if data:
            return requests.post(url, data=data, auth=self.authentication)
        return requests.get(url, auth=self.authentication)

    def test_credentials(self):
        response = self._make_request("Authorization")
        return response.status_code == 200

    def get_users(self, count=500, page=1, list_mode="all"):
        assert page > 0, "Page count is 1-based"
        modes = ["all", "techs", "admins", "regular"]
        assert list_mode in modes, "list_mode must be one of %s" % modes
        url = "Users?count=%d&page=%d&listMode=%s" % (count, page, list_mode)
        response = self._make_request(url)
        return json.loads(response.content)

    def get_user_by_email(self, email):
        response = self._make_request("UserByEmail?email=%s" % email)
        return json.loads(response.content)

    def create_user(self, username, password, email, first_name, last_name, company, phone="", location="",
                    send_welcome_email=False):
        """
        Add user per https://www.jitbit.com/helpdesk/helpdesk-api/#CreateUser
        If successful, returns JitBit userId
        """
        data = {
            "username": username,
            "password": password,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "phone": phone,
            "location": location,
            "company": company,
            "sendWelcomeEmail": send_welcome_email
        }
        response = self._make_request("CreateUser", data=data)
        if response.status_code == 201:
            logger.info("JitBit user created for %s %s", first_name, last_name)
            return int(json.loads(response.content)["userId"])
        logger.warn("JitBit user creation failed for %s %s, response code was %d", first_name, last_name,
                    response.status_code)

    def update_user(self, user_id, username, password, email, first_name, last_name, company, phone, location,
                    notes="", department="", disabled=False):
        """
        Update list of available parameters at  https://www.jitbit.com/helpdesk/helpdesk-api/#UpdateUser
        returns True/ False to indicate apparent success as JitBit's docs don't say they return any info
        """
        data = {
            "user_id": user_id,
            "username": username,
            "password": password,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "phone": phone,
            "location": location,
            "company": company,
            "notes": notes,
            "department": department,
            "disabled": disabled
        }
        response = self._make_request("UpdateUser", data=data)
        if response.status_code == 200:
            logger.info("JitBit user updated for %s %s", first_name, last_name)
            return True
        logger.warn("JitBit user update failed for %s %s (id: %s), response code was %d", first_name, last_name,
                    user_id, response.status_code)
        return False

    def get_companies(self):
        response = self._make_request("Companies")
        return json.loads(response.content)

    def get_categories(self):
        response = self._make_request("categories")
        return json.loads(response.content)

    def get_articles(self):
        response = self._make_request("Articles")
        return json.loads(response.content)

    def get_article_by_id(self, article_id):
        response = self._make_request("Article/%s" % article_id)
        return json.loads(response.content)

    def get_tickets(self):
        response = self._make_request("Tickets")
        return json.loads(response.content)

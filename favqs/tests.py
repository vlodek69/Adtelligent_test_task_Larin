import os
import requests
import uuid
from unittest import TestCase
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("FAVQS_API_KEY")
BASE_URL = "https://favqs.com/api"


def join_url(*parts: str) -> str:
    return ("/".join(p.strip("/") for p in parts)).lower()


def generate_unique_user(prefix: str = "VLarinUser") -> dict[str, str]:
    unique_id = uuid.uuid4().hex[:6]
    login = f"{prefix}_{unique_id}"
    email = f"{login}@test.com"

    return {"login": login, "email": email, "password": "123456"}


class FavqsUserTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_user = generate_unique_user()
        cls.headers = {"Authorization": f'Token token="{API_KEY}"'}

    def test_01_user_is_created(self):
        """Test whether users is successfully created."""
        response = requests.post(
            join_url(BASE_URL, "users"),
            json={"user": self.sample_user},
            headers=self.headers,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            self.sample_user["login"].lower(), response.json()["login"]
        )

    # for the purposes of this task and absolute minimalism, this test can be
    # skipped and User-Token can be obtained from previous test, but it is good
    # to check since both 'Create Session' and 'Get User' endpoints provide
    # user's 'login' and 'email'
    def test_02_create_session(self):
        """Test Create Session endpoint and validate user data."""
        login_data = {
            "user": {
                "login": self.sample_user["login"],
                "password": self.sample_user["password"],
            }
        }
        response = requests.post(
            join_url(BASE_URL, "session"),
            json=login_data,
            headers=self.headers,
        )
        self.headers["User-Token"] = response.json()[
            "User-Token"
        ]  # adds User-Token to the headers for the rest of the tests duration

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            self.sample_user["login"].lower(), response.json()["login"]
        )
        self.assertEqual(
            self.sample_user["email"].lower(), response.json()["email"]
        )

    # test 3 can be combined with test 1, but it is good for scalability and
    # readability to have them separate
    def test_03_get_user(self):
        """Test Get User endpoint and validate user data."""
        response = requests.get(
            join_url(BASE_URL, "/users/", self.sample_user["login"]),
            headers=self.headers,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            self.sample_user["login"].lower(), response.json()["login"]
        )
        self.assertEqual(
            self.sample_user["email"].lower(),
            response.json()["account_details"]["email"],
        )

    def test_04_update_user(self):
        """Test Update User endpoint and validate user data after updating."""
        updated_user_data = {
            "user": {
                "login": self.sample_user["login"] + "upd",
                "email": "upd" + self.sample_user["email"],
            }
        }
        response = requests.put(
            join_url(BASE_URL, "/users/", self.sample_user["login"]),
            json=updated_user_data,
            headers=self.headers,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            "User successfully updated.", response.json()["message"]
        )

        # validate updated data via Get User endpoint
        detail_response = requests.get(
            join_url(BASE_URL, "/users/", updated_user_data["user"]["login"]),
            headers=self.headers,
        )
        self.assertEqual(
            updated_user_data["user"]["login"].lower(),
            detail_response.json()["login"],
        )
        self.assertEqual(
            updated_user_data["user"]["email"].lower(),
            detail_response.json()["account_details"]["email"],
        )


# additionally it is a good idea to add tests with incorrect/conflicting data
# to check whether API acts as expected and gives proper error messages in
# response

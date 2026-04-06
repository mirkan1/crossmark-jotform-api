"""## [JOTFORM API DOCS](https://www.api.jotform.com)"""

# pylint: disable=C0115, C0116, C0103
import json
from abc import ABC
from datetime import datetime
from typing import Union, Dict, Optional, List, Any, Set
from urllib.parse import quote
from time import sleep
import requests
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from .utils import fix_query_key
from .jotFormSubmission import JotFormSubmission
from .types import (
    AnswerType,
    AnswerValue,
    AnswersDict,
    FormObject,
    JotformFormAPIResponse,
    Submission as SubmissionType,
    JotformApiSubmissionContent,
    JotformCreateSubmissionResponse,
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class JotForm(ABC):
    """JotForm API client to fetch and manage form submissions.
    Args:
        api_key (str): JotForm API key used for authentication.
        form_id (str): ID of the JotForm form.
        timeout (int): Request timeout in seconds (default: 45).

    This class provides methods to list, create, update, and delete submissions,
    and to query submissions by various criteria.
    """

    debug: bool = False
    update_timestamp: float
    api_key: str
    form_id: str
    url: str
    submission_ids: Set[str]
    submission_data: Dict[str, JotFormSubmission]
    updating_process: bool
    submission_count: int
    timeout: int
    total_submissions: int

    def __init__(self, api_key: str, form_id: str, timeout: int = 45):
        self.update_timestamp = datetime.now().timestamp()
        self.api_key = api_key
        self.form_id = form_id
        self.url = (
            "https://api.jotform.com/form/"
            + form_id
            + "/submissions?limit=1000&apiKey="
            + api_key
        )
        self.set_url_param("offset", "0")
        self.submission_ids = set()
        self.submission_data = {}
        self.updating_process = False
        self.submission_count = 0
        self.timeout = timeout
        self.total_submissions = self._fetch_submissions_count()
        self.update()

    @classmethod
    def build_url(cls, form_id: str, api_key: str) -> str:
        return (
            "https://api.jotform.com/form/"
            + form_id
            + "/submissions?limit=1000&apiKey="
            + api_key
        )

    def set_logging(self, debug: bool) -> None:
        """Enables or disables debug logging.

        Args:
            debug (bool): If True, enables debug logging; if False, disables it.
        """
        self.debug = debug

    def set_logging_level(self, level: int) -> None:
        """Sets the logging level for debug output.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING).
        """
        logger.setLevel(level)

    def _print(self, text: str, level: int = logging.INFO) -> None:
        if self.debug:
            logger.log(level, text)

    @classmethod
    def _set_get_submission_data(
        cls,
        submissions: List[SubmissionType],
        api_key: str,
        include_deleted: bool = False,
    ) -> Dict[str, JotFormSubmission]:
        """Sets and gets submission data.

        Args:
            submissions (List[SubmissionType]): List of submissions.
            api_key (str): API key for authentication.
            include_deleted (bool, optional): Whether to include deleted submissions. Defaults to False.

        Returns:
            Dict: Dictionary of submission data.
        """
        submissions_dict: Dict[str, JotFormSubmission] = {}
        for sub in submissions:
            if not include_deleted and sub["status"] == "DELETED":
                continue
            submissions_dict[sub["id"]] = JotFormSubmission(sub, api_key)
        return submissions_dict

    def get_submission_ids(self) -> Set[str]:
        return self.submission_ids

    def _set_submission_ids(self) -> None:
        """This function sets the submission memory. It is used for easier for loop for submissions.
        It is called in the constructor, and time to time in other functions"""
        self.submission_ids = set()
        for _, value in self.submission_data.copy().items():
            self.submission_ids.add(value.id)

    def _set_submission_count(self) -> None:
        self.submission_count = len(self.submission_ids)

    def get_submission_data(self) -> Dict[str, JotFormSubmission]:
        self.update()
        return self.submission_data

    def get_submission_count(self) -> int:
        return self.submission_count

    def get_submission_answers(self, submission_id: Union[int, str]) -> AnswersDict:
        """## Returns the answers of the submission by given submission id

        Args:
            submission_id (int or str):

        Returns:
            AnswersDict: answers of the submission
        """
        self.update()
        return self.submission_data[str(submission_id)].answers

    def get_submission_by_request(
        self, submission_id: Union[str, int]
    ) -> Optional[SubmissionType]:
        """## This function gets the submission by request

        Args:
            submission_id (Union[str, int]): _description_

        Returns:
            Optional[SubmissionType]: _description_
        """
        url = (
            f"https://api.jotform.com/submission/{submission_id}?apiKey={self.api_key}"
        )
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 200:
            response = response.json()
            return response["content"]
        return None

    def get_submission(self, submission_id: Union[int, str]) -> JotFormSubmission:
        return self.submission_data[str(submission_id)]

    def get_submissions(self) -> Dict[str, JotFormSubmission]:
        return self.get_submission_data()

    def get_submission_by_text(self, text: str, text_answer: str) -> Optional[object]:
        """## This function gets the submission by text and answer's text
            {
                "key": 1,
                "name": "userName",
                "answer": "John Doe",
                "type": "control_textbox",
                "text": "What is Your User Name",
            }
        Args:
            text (str): _description_
            text_answer (str): _description_

        Returns:
            Optional[object]: submission object if successful, None if not
        """
        for _, submission_object in self.submission_data.copy().items():
            answer = submission_object.get_answer_by_text(text)
            if answer == text_answer:
                return submission_object
        return None

    def get_submission_by_name(self, name: str, name_answer: str) -> Optional[object]:
        """## This function gets the submission by name and answer's name
            {
                "key": 1,
                "name": "userName",
                "answer": "John Doe",
                "type": "control_textbox",
                "text": "What is Your User Name",
            }
        Args:
            name (str): _description_
            name_answer (str): _description_

        Returns:
            Optional[object]: submission object if successful, None if not
        """
        for _, submission_object in self.submission_data.copy().items():
            answer = submission_object.get_answer_by_name(name)
            if answer == name_answer:
                return submission_object
        return None

    def get_submission_by_key(
        self, key: Union[str, int], key_answer: str
    ) -> Optional[object]:
        """## This function gets the submission by key and answer's key
            {
                "key": 1,
                "name": "userName",
                "answer": "John Doe",
                "type": "control_textbox",
                "text": "What is Your User Name",
            }
        Args:
            key (Union[str, int]): _description_
            key_answer (str): _description_

        Returns:
            Optional[object]: submission object if successful, None if not
        """
        for _, submission_object in self.submission_data.copy().items():
            answer = submission_object.get_answer_by_key(key)
            if answer == key_answer:
                return submission_object
        return None

    def get_answer_by_text(
        self, submission_id: Union[int, str], text: str
    ) -> AnswerValue:
        try:
            return self.get_submission(submission_id).get_answer_by_text(text)
        except KeyError:
            self.update()
            return self.get_submission(submission_id).get_answer_by_text(text)

    def get_answer_by_name(
        self, submission_id: Union[int, str], name: str
    ) -> AnswerValue:
        try:
            return self.get_submission(submission_id).get_answer_by_name(name)
        except KeyError:
            self.update()
            return self.get_submission(submission_id).get_answer_by_name(name)

    def get_answer_by_key(
        self, submission_id: Union[int, str], key: str
    ) -> AnswerValue:
        try:
            return self.get_submission(submission_id).get_answer_by_key(key)
        except KeyError:
            self.update()
            return self.get_submission(submission_id).get_answer_by_key(key)

    def get_answer_by_id(self, submission_id: Union[int, str], key: str) -> AnswerValue:
        return self.get_answer_by_key(submission_id, key)

    def get_submission_answers_by_question(
        self, submission_id: Union[int, str]
    ) -> AnswersDict:
        return self.get_submission_answers_by_question_id(submission_id)

    def get_submission_answers_by_question_id(
        self, submission_id: Union[int, str]
    ) -> AnswersDict:
        self.update()
        submission_answers = self.get_submission_answers(submission_id)
        submission_answers_by_question_id: AnswersDict = {}
        for _, answer in submission_answers.items():
            if "id" in answer and "answer" in answer:
                submission_answers_by_question_id[answer["id"]] = answer["answer"]
        return submission_answers_by_question_id

    def get_list_of_questions(self) -> Optional[JotformApiSubmissionContent]:
        """## jotform endpoint of form/{id}/questions

        ### Returns:
            - `object` or 'bool': questions list if successful, false if not
        """
        url = f"https://api.jotform.com/form/{self.form_id}/questions?apiKey={self.api_key}"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 200:
            response = response.json()
            return response["content"]
        return None

    def __delitem__(self, submission_id: Union[int, str]) -> None:
        """Delete a submission using del operator.

        Args:
            submission_id: The submission ID to delete

        Example:
            del jotform_instance[submission_id]
        """
        if not submission_id:
            raise ValueError("submission_id cannot be empty")

        submission_id = str(submission_id)
        if submission_id not in self.submission_data:
            raise KeyError(f"Submission {submission_id} not found")

        url = (
            f"https://api.jotform.com/submission/{submission_id}?apiKey={self.api_key}"
        )

        response = requests.delete(url, timeout=self.timeout)
        if response.status_code == 200:
            del self.submission_data[submission_id]
            self.submission_ids.discard(submission_id)
            self._set_submission_count()
        else:
            raise RuntimeError(f"Failed to delete submission {submission_id}")

    def delete_submission(self, submission_id: Union[int, str]) -> bool:
        if not submission_id:
            raise ValueError("submission_id cannot be empty")

        submission_id = str(submission_id)
        url = (
            f"https://api.jotform.com/submission/{submission_id}?apiKey={self.api_key}"
        )
        response = requests.delete(url, timeout=self.timeout)
        if response.status_code == 200:
            del self.submission_data[submission_id]
            self.submission_ids.discard(submission_id)
            self._set_submission_count()
            return True
        return False

    def create_submission(self, submission: SubmissionType) -> Union[bool, str]:
        """## This function creates a submission in Jotform
        then sets the new submission to the submission data.

        ### Args:
            - `submission (pseudo sumbission dictionary)`:
               {
                    "submission[1]": "value",
                    "submission[2]": "value",
                    ...
               }

        ### Returns:
            - `bool` or 'string': new created submission's id if successful, false if not
        """
        url = f"https://api.jotform.com/form/{self.form_id}/submissions?apiKey={self.api_key}"
        response = requests.post(url, data=submission, timeout=self.timeout)
        if response.status_code == 200:
            api_response: JotformCreateSubmissionResponse = response.json()
            submission_id = str(api_response["content"]["submissionID"])
            submission_data = self.get_submission_by_request(submission_id)
            if submission_data:
                self.set_new_submission(submission_data)
                return submission_id
        return False

    def create_submission_using_another(
        self, submission_data: SubmissionType, submission_to_copy: JotFormSubmission
    ) -> Union[bool, str]:
        """## This function creates a submission in Jotform
        then sets the new submission to the submission data.

        ### Args:
            - `submission_data (sumbission dictionary)`:
            contains name value pairs of the submission
            e.g:
               {
                    "data": "value",
                    "data2": "value",
                    ...
               }
            - submission_to_copy (JotFormSubmission): submission object to copy

        ### Returns:
            - `bool`: true if successful, false if not
        """
        data: SubmissionType = {}  # type: ignore
        questions = self.get_list_of_questions()
        if not questions:
            return False
        for q in questions:
            name = questions[q]["name"]
            if name in submission_data:
                data[f"submission[{q}]"] = submission_data[name]
            else:
                answer_obj = submission_to_copy.get_answer_by_name(name)  # type: ignore
                answer = answer_obj["answer"] if "answer" in answer_obj else None
                if answer:
                    data[f"submission[{q}]"] = answer
        return self.create_submission(data)

    def _set_limit_left(self, limit_left: Optional[int]) -> None:
        # TODO
        if limit_left is not None:
            logger.info(f"API rate limit left: {limit_left}")

    def update_submission_answers_batch(
        self, submission_id: Union[int, str], answers: Dict[str, AnswerType]
    ) -> bool:
        """## This function updates multiple answers of the submission in a single batch request

        ### Args:
            - `submission_id (Union[int, str])`: Submission ID
            - `answers (Dict[str, AnswerType])`: Dictionary of field_id to answer

        ### Returns:
            - `bool`: True if successful, False if not
        """
        data: Dict[str, Any] = {}
        for answer_key, answer_value in answers.items():
            if isinstance(answer_value, list):
                data[f"submission[{answer_key}][]"] = answer_value
            elif answer_value == "" or answer_value is None:
                data[f"submission[{answer_key}]"] = ""
            else:
                data[f"submission[{answer_key}]"] = answer_value
        url = f"https://api.jotform.com/submission/{submission_id}"
        response = requests.post(
            url,
            params={"apiKey": self.api_key},
            data=data,
            timeout=self.timeout,
        )
        if response.status_code == 200:
            message = response.json().get("message", "")
            limit_left = response.json().get("limit-left", None)
            self._set_limit_left(limit_left)
            if message.lower() != "success":
                return False
            for answer_key, answer_value in answers.items():
                self.submission_data[str(submission_id)].set_answer(
                    answer_key, answer_value
                )
            return True
        return False

    def update_submission_answer(
        self, submission_id: Union[int, str], field_id: str, answer: AnswerType
    ) -> bool:
        """## This function updates the answer of the submission

        ### Args:
            - `submission_id (Union[int, str])`: _description_
            - `field_id (str)`: _description_
            - `answer (AnswerType)`: _description_

        ### Returns:
            - `bool`: True if successful, False if not
        """
        if isinstance(answer, list):
            data = {f"submission[{field_id}][]": answer}
            response = requests.post(
                f"https://api.jotform.com/submission/{submission_id}",
                params={"apiKey": self.api_key},
                data=data,
                timeout=self.timeout,
            )
        else:
            query = f"submission[{field_id}]={answer}"
            url = f"https://api.jotform.com/submission/{submission_id}"
            url += f"?apiKey={self.api_key}&{query}"
            response = requests.post(url, timeout=self.timeout)
        if response.status_code == 200:
            self.submission_data[str(submission_id)].set_answer(field_id, answer)
            return True
        return False

    def set_url_param(self, key: Union[str, int], value: Union[str, int]) -> None:
        """Sets the URL parameter.

        Available keys:
            - `apiKey:` Your JotForm API key for authentication.
            - `limit:` Specifies the maximum number of results to return.
            - `offset:` Specifies the number of results to skip before starting to return results.
            - `orderby:` Determines the field by which to sort the results.
            - `filter:` Applies a filter to the results based on specified criteria.
            - `search:` Searches for a specific term within the results.
            - `sort:` Specifies the sort order of the results (e.g., ascending or descending).
            - `fields:` Specifies which fields to include in the response.
            - `id:` Filters results by a specific ID.
            - `created_at:` Filters results based on their creation date.
            - `updated_at:` Filters results based on their last updated date.

        Args:
            key (str): The key to set in the URL.
            value (str): The value to set for the specified key.
        """
        value = str(value)
        key_str = str(key)
        base_url, params = self.url.split("?")
        if key_str in params:
            params = params.split("&")
            for i, param in enumerate(params):
                if key_str in param:
                    params[i] = key_str + "=" + value
            self.url = base_url + "?" + "&".join(params)
        else:
            self.url += "&" + key_str + "=" + value

    def sort_submission_data_by_id(self) -> None:
        """## Sorts the submission data by id
        No need to sort since it is already sorted by the API
        unless orderby is changed in the url for descending order
        """
        sorted_tuples = sorted(
            self.submission_data.copy().items(), key=lambda x: x[1].id, reverse=True
        )
        sorted_dict = {k: v for k, v in sorted_tuples}
        self.submission_data = sorted_dict

    def get_missing_submission_id(self) -> Optional[int]:
        """## This function gets the missing submission id

        Returns:
            Optional[int]: return the missing submission id if there is any
        """
        all_submission_ids = set(int(sid) for sid in self.get_submission_ids())
        expected_submission_ids = set(range(1, self.submission_count + 1))
        missing_ids = expected_submission_ids - all_submission_ids
        if missing_ids:
            return missing_ids.pop()

    def _fetch_new_submissions(
        self,
        count: int,
        attempt: int = 0,
        max_attempts: int = 5,
        limit: int = 1000,
    ) -> bool:
        """### It is already newest to oldest so we can request one query, and it should be enough

        #### Args:
            - `count:` Fresh count of the submissions
            - `attempt:` Current number of attempts. Defaults to 0.
            - `max_attempts:` Maximum number of attempts. Defaults to 5.
            - `limit:` Limit for the number of submissions to fetch in one request. Defaults to None.

        #### Returns:
            - `bool:` True if updated, False if not
        """
        if count <= 0:
            return False
        attempt = int(attempt)
        max_attempts = int(max_attempts)
        limit = 1000 if limit > 1000 else limit
        self.set_url_param("limit", limit)
        self.set_url_param("orderby", "id")
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            self.submission_data.update(
                self._set_get_submission_data(data["content"], self.api_key)
            )
            fetched_count = len(data["content"])
            if fetched_count == 0:
                self.set_global_data()
                return True
            remaining_count = max(0, count - fetched_count)
            if fetched_count < limit or remaining_count == 0:
                self.set_global_data()
                return True

            current_offset = int(data["resultSet"].get("offset", 0))
            next_offset = current_offset + fetched_count
            if next_offset <= current_offset:
                self.set_global_data()
                return True

            self.set_url_param("offset", next_offset)
            return self._fetch_new_submissions(
                remaining_count, attempt, max_attempts, limit
            )
        except requests.exceptions.HTTPError as http_err:
            if http_err.response is not None:
                if http_err.response.status_code == 429:  # Too Many Requests
                    self._print(f"Request failed: {http_err}. Retrying with backoff...")
                    if attempt < max_attempts:
                        return self._fetch_new_submissions(
                            count,
                            attempt + 1,
                            max_attempts,
                            limit,
                        )
                elif http_err.response.status_code == 504:  # Gateway timeout
                    self._print(f"Request failed: {http_err}. Retrying with backoff...")
                    if attempt < max_attempts:
                        current_limit = 1000 if count > 1000 else count
                        new_limit = max(1, current_limit // 2)
                        self.set_url_param("limit", new_limit)
                        self._print(
                            f"Unterminated string error: retrying with limit={new_limit}"
                        )
                        if attempt < max_attempts:
                            sleep(0.666)
                            return self._fetch_new_submissions(
                                count, attempt + 1, max_attempts, new_limit
                            )
            self._print(f"Request failed: {http_err}")
        except (RequestException, JSONDecodeError, ValueError) as e:
            if "Unterminated string starting at" in str(e):
                # If this error occurs, retry with half the previous limit (minimum 1)
                current_limit = 1000 if count > 1000 else count
                new_limit = max(1, current_limit // 2)
                self.set_url_param("limit", new_limit)
                self._print(
                    f"Unterminated string error: retrying with limit={new_limit}"
                )
                if attempt < max_attempts:
                    sleep(0.666)
                    return self._fetch_new_submissions(
                        count, attempt + 1, max_attempts, new_limit
                    )
            self._print(f"Request failed: {e}")
            if attempt < max_attempts:
                sleep(0.666)
                return self._fetch_new_submissions(
                    count + self.submission_count, attempt + 1, max_attempts, limit
                )
        except KeyError as e:
            self._print(f"KeyError: {e}")
        return False

    def _fetch_updated_submissions(
        self, attempt: int = 0, max_attempts: int = 5, limit: Union[str, int] = 1000
    ) -> bool:
        """## This function gets the last updated data from the Jotform API.
            Aim of this function is to get last 1000 submissions sorted by updated_at.
            So that network traffic is less and we can get the most recent data.

        Args:
            attempt (_type_, optional): Current number of attempts. Defaults to 0.
            max_attempts (_type_, optional): Maximum number of attempts. Defaults to 5.

        Returns:
            bool: True if updates, False if not
        """
        attempt = int(attempt)
        max_attempts = int(max_attempts)
        self.set_url_param("limit", limit)
        self.set_url_param("orderby", "updated_at")
        self.set_url_param("offset", "0")
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            self.submission_data.update(
                self._set_get_submission_data(data["content"], self.api_key)
            )
            self.set_global_data()
            return True
        except requests.exceptions.HTTPError as http_err:
            if http_err.response is not None:
                if http_err.response.status_code == 429:  # Too Many Requests
                    self._print(f"Request failed: {http_err}. Retrying with backoff...")
                    if attempt < max_attempts:
                        return self._fetch_updated_submissions(
                            attempt + 1, max_attempts
                        )
                elif http_err.response.status_code == 504:  # Gateway timeout
                    self._print(f"Request failed: {http_err}. Retrying with backoff...")
                    if attempt < max_attempts:
                        self.set_url_param("limit", "500")
                        self._print(
                            f"Unterminated string error: retrying with limit=500"
                        )
                        sleep(0.666)
                        return self._fetch_updated_submissions(
                            attempt + 1, max_attempts
                        )
            self._print(f"Request failed: {http_err}")
        except (RequestException, JSONDecodeError, ValueError) as e:
            if "Unterminated string starting at" in str(e):
                # If this error occurs, retry with half the previous limit (minimum 1)
                self.set_url_param("limit", "500")
                self._print(f"Unterminated string error: retrying with limit=500")
                if attempt < max_attempts:
                    sleep(0.666)
                    return self._fetch_updated_submissions(attempt + 1, max_attempts)
            self._print(f"Request failed: {e}")
            if attempt < max_attempts:
                sleep(0.666)
                return self._fetch_updated_submissions(attempt + 1, max_attempts)
        except KeyError as e:
            self._print(f"KeyError: {e}")
        return False

    def set_global_data(self) -> None:
        self._set_submission_ids()
        self._set_submission_count()
        self._reset_url_params()

    def request_submission_by_case_id(self, case_id: str) -> Optional[object]:
        """
        Requests the submission by case id
        this function is used when the submission is not in the submission data
        """
        query = quote(f"""{{"q221:matches:answer":"{case_id}"}}""")
        url = f"https://api.jotform.com/form/{self.form_id}/submissions"
        url += f"?apiKey={self.api_key}&filter={query}"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != 200:
            return None
        _json = response.json()
        return _json

    def set_new_submission(self, submission: SubmissionType) -> None:
        self.submission_data.update(
            self._set_get_submission_data([submission], self.api_key)
        )
        self.set_global_data()

    def get_form(self) -> Optional[JotformFormAPIResponse]:
        """
        Gets form data directly from Jotform so there is no data diffirence on this function.
        It is slow since we are requesting data from Jotform.

        Returns:
            Optional[JotformFormAPIResponse]: object if successful, None if not
        """
        url = f"https://api.jotform.com/form/{self.form_id}?apiKey={self.api_key}"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _fetch_submissions_count(self) -> int:
        form = self.get_form()
        if form:
            content: FormObject = form.get("content", {})
            return int(content.get("count", 0))
        return 1

    def update(self, force: bool = False) -> bool:
        """## This function updates the data from the Jotform API
            It will look for a change in the submission count,
            updates the data accordingly unless force is True

        Args:
            force (bool, optional): If True, it will update all the submissions. Defaults to False.

        Returns:
            bool: True if updates, False if not
        """
        if self.updating_process:
            self._reset_url_params()
            self._print("Update process is already running.")
            return False
        self.updating_process = True
        now = datetime.now().timestamp()
        its_been = now - self.update_timestamp
        try:
            if its_been > 300 or force:
                # been more than 5 minutes so only pull the 100 posibly recently updated submissions
                self.update_timestamp = now
                self._fetch_updated_submissions(limit=100)
                self._fetch_new_submissions(100, limit=100)
                self._print(
                    f"Update process is completed. Last update was {int(its_been / 60)} minutes ago."
                )
            else:
                count = self._fetch_submissions_count() - self.total_submissions
                if count > 0:
                    self._fetch_new_submissions(count, limit=count)
                    self.total_submissions += count
                    self._print(
                        f"Update process is completed. Last update was {int(its_been / 60)} minutes ago.\n{count} new submissions found."
                    )
                else:
                    return False
            return True
        finally:
            # Always release the update lock even if a request is interrupted.
            self.updating_process = False
            self._reset_url_params()

    def _reset_url_params(self) -> None:
        self.set_url_param("offset", "0")
        self.set_url_param("limit", "1000")
        self.set_url_param("orderby", "id")

    def get_user_data_by_email(self, email: str) -> Optional[List[JotFormSubmission]]:
        """
        ## This function gets the user data by email address

        Returns:
            Optional[List[JotFormSubmission]]: List of submissions for the given email, or None if email is not provided.
        """
        if not email:
            return None
        email = email.lower()
        self.update()
        submissions: List[JotFormSubmission] = []
        for _, submission in self.submission_data.copy().items():
            submission_object = self.get_submission(submission.id)
            email_objects = [i.lower() for i in submission_object.emails if i]
            if email in email_objects:
                submissions.append(submission_object)
        return submissions

    @classmethod
    def get_submission_data_by_query(
        cls, filter_param: Union[Dict[str, Any], str], api_key: str, form_id: str
    ) -> Dict[str, JotFormSubmission]:
        """
        Query submissions using JotForm API filter param as JSON string or plain string.
        Accepts either a Dict (converted to JSON string) or a pre-formatted string.
        If Dict: checks key format, adds 'q' if missing, logs about it, or throws error if only a number.
        Example: '{"q3:matches":"Will VanSaders"}' or {"q3:matches": "Will VanSaders"}
        """

        if not filter_param:
            raise ValueError("filter_param must be a non-empty dict or string")

        if isinstance(filter_param, dict):
            new_filter = {}
            for k, v in filter_param.items():
                fixed_key = fix_query_key(k)
                new_filter[fixed_key] = v
            filter_str = json.dumps(new_filter)
        elif isinstance(filter_param, int):
            raise ValueError("filter_param cannot be only a number")
        else:
            try:
                filter_dict = json.loads(filter_param)
                new_filter = {}
                for k, v in filter_dict.items():
                    fixed_key = fix_query_key(k)
                    new_filter[fixed_key] = v
                filter_str = json.dumps(new_filter)
            except Exception:
                # If not JSON, just use as-is
                filter_str = filter_param

        params = {"filter": filter_str}
        # TODO: try raise for exectipns of requests and json decoding, and retry a few times with backoff since this is a user facing function and can be used in critical places

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    cls.build_url(form_id, api_key), params=params, timeout=45
                )
            except RequestException as request_error:
                if attempt < max_attempts - 1:
                    sleep(0.666)
                    continue
                print(f"JotForm request error: {request_error}")
                return {}

            if response.status_code != 200:
                print(f"JotForm API error: {response.status_code} - {response.text}")
                return {}
            data = None
            try:
                data: Union[Dict[str, Any], None] = response.json()
            except (JSONDecodeError, ValueError) as decode_error:
                if attempt < max_attempts - 1:
                    sleep(0.666)
                    continue
                response_preview = response.text[:500].replace("\n", " ")
                print(f"JotForm API returned invalid JSON: {decode_error}")
                if response_preview:
                    print(f"Response preview: {response_preview}")
                return {}

            if not isinstance(data, dict):
                print("JotForm API returned an unexpected response format.")
                return {}

            submissions = data.get("content", [])
            return cls._set_get_submission_data(submissions, api_key)  # type: ignore

        return {}

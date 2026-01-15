# pyright: reportUnknownArgumentType=false, reportUnusedImport=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportTypedDictNotRequiredAccess=false, reportUnknownMemberType=false, reportArgumentType=false, reportPrivateUsage=false
import unittest
from unittest.mock import (
    Mock,
    patch,
    MagicMock,
    call,
)
from datetime import datetime
from crossmark_jotform_api.jotForm import JotForm, JotFormSubmission


class TestJotFormAdvanced(unittest.TestCase):
    """More comprehensive tests for JotForm functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.form_id = "123456"
        self.mock_response_data = {
            "content": [
                {
                    "id": "1001",
                    "form_id": self.form_id,
                    "ip": "192.168.1.1",
                    "created_at": "2024-01-01 12:00:00",
                    "status": "ACTIVE",
                    "new": "1",
                    "flag": "0",
                    "notes": "",
                    "updated_at": "2024-01-01 12:00:00",
                    "answers": {
                        "1": {
                            "name": "fullName",
                            "answer": "John Doe",
                            "text": "Full Name",
                            "type": "control_textbox",
                        }
                    },
                }
            ],
            "resultSet": {"offset": 0, "limit": 1000, "count": 1},
        }

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_set_get_submission_data(self, mock_get):
        """Test the _set_get_submission_data class method"""
        submissions = self.mock_response_data["content"]

        result = JotForm._set_get_submission_data(submissions, self.api_key)

        self.assertEqual(len(result), 1)
        self.assertIn("1001", result)
        self.assertIsInstance(result["1001"], JotFormSubmission)

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_set_get_submission_data_exclude_deleted(self, mock_get):
        """Test excluding deleted submissions"""
        submissions = [
            {
                "id": "1001",
                "form_id": self.form_id,
                "status": "ACTIVE",
                "answers": {},
                "ip": "192.168.1.1",
                "created_at": "2024-01-01 12:00:00",
                "new": "1",
                "flag": "0",
                "notes": "",
                "updated_at": "2024-01-01 12:00:00",
            },
            {
                "id": "1002",
                "form_id": self.form_id,
                "status": "DELETED",
                "answers": {},
                "ip": "192.168.1.1",
                "created_at": "2024-01-01 12:00:00",
                "new": "1",
                "flag": "0",
                "notes": "",
                "updated_at": "2024-01-01 12:00:00",
            },
        ]

        result = JotForm._set_get_submission_data(
            submissions, self.api_key, include_deleted=False
        )

        self.assertEqual(len(result), 1)
        self.assertIn("1001", result)
        self.assertNotIn("1002", result)

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_set_get_submission_data_include_deleted(self, mock_get):
        """Test including deleted submissions"""
        submissions = [
            {
                "id": "1001",
                "form_id": self.form_id,
                "status": "ACTIVE",
                "answers": {},
                "ip": "192.168.1.1",
                "created_at": "2024-01-01 12:00:00",
                "new": "1",
                "flag": "0",
                "notes": "",
                "updated_at": "2024-01-01 12:00:00",
            },
            {
                "id": "1002",
                "form_id": self.form_id,
                "status": "DELETED",
                "answers": {},
                "ip": "192.168.1.1",
                "created_at": "2024-01-01 12:00:00",
                "new": "1",
                "flag": "0",
                "notes": "",
                "updated_at": "2024-01-01 12:00:00",
            },
        ]

        result = JotForm._set_get_submission_data(
            submissions, self.api_key, include_deleted=True
        )

        self.assertEqual(len(result), 2)
        self.assertIn("1001", result)
        self.assertIn("1002", result)

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_get_submission_data_by_query_with_dict(self, mock_get):
        """Test getting submission data by query with dict filter"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        filter_dict = {"3:matches": "Will VanSaders"}

        result = JotForm.get_submission_data_by_query(
            filter_dict, self.api_key, self.form_id
        )

        self.assertEqual(len(result), 1)
        self.assertIn("1001", result)
        mock_get.assert_called_once()

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_get_submission_data_by_query_with_string(self, mock_get):
        """Test getting submission data by query with string filter"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        filter_str = '{"q3:matches": "Will VanSaders"}'

        result = JotForm.get_submission_data_by_query(
            filter_str, self.api_key, self.form_id
        )

        self.assertEqual(len(result), 1)
        self.assertIn("1001", result)
        mock_get.assert_called_once()

    def test_get_submission_data_by_query_invalid_input(self):
        """Test get_submission_data_by_query with invalid input"""
        with self.assertRaises(ValueError):
            JotForm.get_submission_data_by_query("", self.api_key, self.form_id)

        with self.assertRaises(ValueError):
            JotForm.get_submission_data_by_query(None, self.api_key, self.form_id)

        with self.assertRaises(ValueError):
            JotForm.get_submission_data_by_query(123, self.api_key, self.form_id)


class TestJotFormSubmissionAdvanced(unittest.TestCase):
    """More comprehensive tests for JotFormSubmission"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.sample_submission = {
            "id": "123456789",
            "form_id": "987654321",
            "ip": "192.168.1.1",
            "created_at": "2024-01-01 12:00:00",
            "status": "ACTIVE",
            "new": "1",
            "flag": "0",
            "notes": "",
            "updated_at": "2024-01-01 12:00:00",
            "answers": {
                "1": {
                    "name": "fullName",
                    "answer": "John Doe",
                    "text": "Full Name",
                    "type": "control_textbox",
                },
                "2": {
                    "name": "email",
                    "answer": "john@example.com",
                    "text": "Email Address",
                    "type": "control_email",
                },
                "3": {
                    "name": "colors",
                    "answer": ["red", "blue", "green"],
                    "text": "Favorite Colors",
                    "type": "control_checkbox",
                },
                "4": {
                    "name": "singleSelect",
                    "answer": ["option1"],
                    "text": "Single Selection",
                    "type": "control_radio",
                },
            },
        }

    def test_get_answer_by_text_not_found(self):
        """Test getting answer by text when not found"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        with self.assertRaises(ValueError) as context:
            submission.get_answer_by_text("Non-existent Question")

        self.assertIn("not found", str(context.exception))

    def test_get_answer_by_name_not_found(self):
        """Test getting answer by name when not found"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        with self.assertRaises(ValueError) as context:
            submission.get_answer_by_name("nonExistentName")

        self.assertIn("not found", str(context.exception))

    def test_get_answer_by_key_not_found(self):
        """Test getting answer by key when not found"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        with self.assertRaises(ValueError) as context:
            submission.get_answer_by_key("999")

        self.assertIn("not found", str(context.exception))

    def test_get_answer_with_list_single_item(self):
        """Test getting answer that is a list with single item"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        answer = submission.get_answer_by_key("4")  # singleSelect has ["option1"]
        self.assertEqual(answer["answer"], "option1")  # Should extract single item

    def test_get_answer_with_list_multiple_items(self):
        """Test getting answer that is a list with multiple items"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        answer = submission.get_answer_by_key(
            "3"
        )  # colors has ["red", "blue", "green"]
        self.assertEqual(
            answer["answer"], ["red", "blue", "green"]
        )  # Should keep as list

    def test_get_answer_case_insensitive_text(self):
        """Test that get_answer_by_text is case insensitive"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        answer = submission.get_answer_by_text("full name")  # lowercase
        self.assertEqual(answer["answer"], "John Doe")

        answer = submission.get_answer_by_text("FULL NAME")  # uppercase
        self.assertEqual(answer["answer"], "John Doe")

    def test_text_to_html(self):
        """Test text to HTML conversion"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with None
        result = submission.text_to_html(None)
        self.assertIsNone(result)

        # Test with simple text
        result = submission.text_to_html("Hello World")
        self.assertEqual(result, "<p>Hello World</p>")

        # Test with line breaks
        result = submission.text_to_html("Line 1\nLine 2\rLine 3\r\nLine 4")
        self.assertEqual(result, "<p>Line 1<br>Line 2<br>Line 3<br>Line 4</p>")

        # Test with paragraphs
        result = submission.text_to_html("Para 1\n\nPara 2")
        self.assertEqual(result, "<p>Para 1</p><p>Para 2</p>")

    def test_split_domain_from_email_edge_cases(self):
        """Test split_domain_from_email with edge cases"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with None
        result = submission.split_domain_from_email(None)
        self.assertIsNone(result)

        # Test with empty string
        result = submission.split_domain_from_email("")
        self.assertIsNone(result)

        # Test with string without @
        result = submission.split_domain_from_email("noatsign")
        self.assertEqual(result, "noatsign")

    def test_get_value_edge_cases(self):
        """Test get_value with various edge cases"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with None
        result = submission.get_value(None)
        self.assertIsNone(result)

        # Test with string with whitespace
        result = submission.get_value("  test string  ")
        self.assertEqual(result, "test string")

        # Test with dict with answer that's a list
        test_dict = {"answer": ["item1", "item2"]}
        result = submission.get_value(test_dict)
        self.assertEqual(result, "item1")

        # Test with single-item dict
        test_dict = {"single_key": "single_value"}
        result = submission.get_value(test_dict)
        self.assertEqual(result, "single_value")

    def test_make_array_edge_cases(self):
        """Test make_array with edge cases"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with None
        result = submission.make_array(None)
        self.assertEqual(result, [])

        # Test with empty string
        result = submission.make_array("")
        self.assertEqual(result, [])

        # Test with whitespace-only string
        result = submission.make_array("   ")
        self.assertEqual(result, [])

        # Test with dict containing answer
        test_dict = {"answer": "value1, value2"}
        result = submission.make_array(test_dict)
        self.assertEqual(result, ["value1", "value2"])

        # Test with non-string, non-list, non-dict
        result = submission.make_array(123)
        self.assertEqual(result, [123])

    def test_tide_answer_for_list(self):
        """Test tide_answer_for_list method"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with list
        test_list = ["apple", "banana", "cherry"]
        result = submission.tide_answer_for_list(test_list)
        self.assertEqual(result, "Apple, Banana, Cherry")

        # Test with dict
        test_dict = {"1": "apple", "2": "banana", "3": "cherry"}
        result = submission.tide_answer_for_list(test_dict)
        self.assertEqual(result, "Apple, Banana, Cherry")

    def test_answer_for_html(self):
        """Test answer_for_html method"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with list
        test_list = ["apple", "banana"]
        result = submission.answer_for_html(test_list)
        self.assertEqual(result, "*Apple<br>*Banana")

        # Test with dict
        test_dict = {"1": "apple", "2": "banana"}
        result = submission.answer_for_html(test_dict)
        self.assertEqual(result, "*Apple<br>*Banana")

        # Test with string
        result = submission.answer_for_html("apple")
        self.assertEqual(result, "*Apple")

        # Test with None
        result = submission.answer_for_html(None)
        self.assertEqual(result, "*None")

    def test_turn_into_american_datetime_format(self):
        """Test datetime format conversion"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        # Test with string
        result = submission.turn_into_american_datetime_format("2024-01-01 14:30:00")
        self.assertEqual(result, "01/01/2024 02:30 PM")

        # Test with datetime object
        dt = datetime(2024, 1, 1, 14, 30, 0)
        result = submission.turn_into_american_datetime_format(dt)
        self.assertEqual(result, "01/01/2024 02:30 PM")

        # Test with dict
        test_dict = {"answer": "2024-01-01 14:30:00"}
        result = submission.turn_into_american_datetime_format(test_dict)
        self.assertEqual(result, "01/01/2024 02:30 PM")

        # Test with invalid input
        with self.assertRaises(ValueError):
            submission.turn_into_american_datetime_format(123)

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_by_key(self, mock_post):
        """Test setting answer by key"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        submission.set_answer("1", "Jane Doe")

        # Verify the answer was updated in answers_arr
        updated_answer = submission.get_answer_by_key("1")
        self.assertEqual(updated_answer["answer"], "Jane Doe")

        # Verify the answer was updated in answers dict
        self.assertEqual(submission.answers["1"]["answer"], "Jane Doe")

        # Verify update_submission was called (via the post request)
        mock_post.assert_called_once()

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_by_text(self, mock_post):
        """Test setting answer by text"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        submission.set_answer_by_text("Full Name", "Jane Doe")

        # Verify the answer was updated
        updated_answer = submission.get_answer_by_text("Full Name")
        self.assertEqual(updated_answer["answer"], "Jane Doe")

        # Verify update_submission was called
        mock_post.assert_called_once()

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_by_name(self, mock_post):
        """Test setting answer by name"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        submission.set_answer_by_name("fullName", "Jane Doe")

        # Verify the answer was updated
        updated_answer = submission.get_answer_by_name("fullName")
        self.assertEqual(updated_answer["answer"], "Jane Doe")

        # Verify update_submission was called
        mock_post.assert_called_once()

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_with_list_value(self, mock_post):
        """Test setting answer with a list value"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        new_colors = ["yellow", "purple", "orange"]
        submission.set_answer("3", new_colors)

        # Verify the answer was updated
        updated_answer = submission.get_answer_by_key("3")
        self.assertEqual(updated_answer["answer"], new_colors)

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_updates_both_storage_locations(self, mock_post):
        """Test that set_answer updates both answers_arr and answers dict"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        new_value = "test@example.com"
        submission.set_answer("2", new_value)

        # Check answers_arr
        found_in_arr = False
        for answer in submission.answers_arr:
            if answer["key"] == "2":
                self.assertEqual(answer["answer"], new_value)
                found_in_arr = True
                break
        self.assertTrue(found_in_arr, "Answer not found in answers_arr")

        # Check answers dict
        self.assertEqual(submission.answers["2"]["answer"], new_value)

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_by_text_case_insensitive(self, mock_post):
        """Test that set_answer_by_text works with case variations"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        submission.set_answer_by_text("FULL NAME", "Test User")

        # Verify the answer was updated
        updated_answer = submission.get_answer_by_text("full name")
        self.assertEqual(updated_answer["answer"], "Test User")

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_nonexistent_key(self, mock_post):
        """Test setting answer with non-existent key raises error"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with self.assertRaises(KeyError):
            submission.set_answer("999", "test_value")

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_by_text_nonexistent(self, mock_post):
        """Test setting answer by non-existent text raises error"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            submission.set_answer_by_text("Non-existent Field", "test_value")

        self.assertIn("not found", str(context.exception))

    @patch("crossmark_jotform_api.jotForm.requests.post")
    def test_set_answer_by_name_nonexistent(self, mock_post):
        """Test setting answer by non-existent name raises error"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            submission.set_answer_by_name("nonExistentField", "test_value")

        self.assertIn("not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()

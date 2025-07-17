
# JotFormSubmission Library Change Log

- 2025-07-12 v2.4.7:
  - improved error handling for HTTP 429 responses by adding a message: `self._print(f"Request failed: {http_err} (429 Too Many Requests). Retrying with backoff...")`
  - fixed `answer_for_html` function to handle cases where the answer is `None`
- 2025-07-12 v2.4.6:
  - added `update_submission_answers_batch` function to perform batch updates of answers, reducing the number of requests sent to the server
- 2025-07-03 v2.4.5:
  - added `get_answer_by_text` function to get the answer by `text`
  - added `get_answer_by_name` function to get the answer by `name`
  - added `get_answer_by_key` function to get the answer by `key` aka `id`
  - added `tide_answer_for_list` function to tide the answer for list and gives a comma separated string
  - added `answer_for_html` function to tide the answer for html
- 2025-04-18 v2.4.4:
  - added `tide_answer_for_list` function to tide the answer for list and gives a comma separated string
  - added `answer_for_html` function to tide the answer for html
- 2025-04-09 v2.4.3:
  - added `set_answer_by_name` function to set the answer by `name`
  - added `get_answer_by_key` function to get the answer by `key` aka `id`
- 2025-03-10 v2.4.2:
  - added JSONDecodeError catch on `_fetch_updated_submissions` and `_fetch_new_submissions` functions
- 2025-03-10 v2.4.1:
  - fixed bugs on `get_submission_by_name`, and `get_submission_by_key`
  - enhanced the docs for `get_submission_by_text`
- 2025-03-08 v2.4.0:
  - `get_submission_id_by_text` function call is deleted, instead `get_submission_by_text`, `get_submission_by_name`, and `get_submission_by_key` is implemented
  - Better typings are added to the functions
  - `case_id`, `store`, and `client` parameters are deleted from the JotFormSubmission class, now they have to be set via inheretance
  - Docs are updated
- 2025-03-04 v2.3.5:
  - Deleted a duplicated call inside the `_reset_url_params` function
- 2025-03-04 v2.3.4:
  - `get_answer_by_id` method is added to the JotFormSubmission class
- 2025-03-04 v2.3.3:
  - Removed debug parameter from JotForm constructor and improve error handling in answer retrieval methods
- 2025-03-04 v2.3.2:
  - fixed a deadly bug where it keeps fetching new submissions ieven if the content count is less than limit size
  - pylint is run on the code
- 2025-02-04 v2.3.1:
  - fixed an error on `update`
  - pylint indentation error fixed
- 2025-02-02 v2.3.0:
  - enhanced underscore design for the private functions
  - intruduced `get_missing_submission_id`
  - intruduced `_fetch_new_submissions` function to get the submission if there are new submissions available
  - intruduced `_fetch_updated_submissions` function to get the submission if there are updated submissions available `limit is always 1000`
  - wrote some typings for the functions
  - fixed error on `set_url_param` function and enhanced its docs
- 2024-12-10 v2.2.0:
  - added api_key validation on the constructor of JotFormSubmission class
  - added update_submission class method to update the submission of JotFormSubmission class
  - refactored the code for better performance of the JotFormSubmission class
  - peudo tests are added to the JotFormSubmission class
- 2024-12-10 v2.1.6:
  - catching an error where the data returns as none form jotform side, need further investigation on this.
- 2024-09-27 v2.1.5:
  - fixed a bug where iteration throwing runtime error on `get_list_of_questions` function
  - hidden some warnings related to not existing module description
- 2024-07-23 v2.1.4:
  - some typing are added to the functions
  - `ms-python.black-formatter` is used for formatting the code
- 2024-07-23 v2.1.3:
  - `set_data` function is refactored for a more robust solution on a `ChunkedEncodingError`
- 2024-06-11 v2.1.1:
  - `__print` function's name changed into `_print`.
  - `set_data` function is refactored, `time.sleep` is added to avoid the rate limit and 3 tries are added to avoid the connection error.
  - timeouts are set where forgotten on previous patches
  - `set_url_param` function is refactored
  - `_clear_answers` is intruduced to clear the answers of the submission on construction.
  - `set_answer` is refactored

- 2024-06-11 v2.1.0:
  - `get_submission_by_request` is refactored.
  - `get_submission_id_by_text` now has additional parameter `text` to get the submission id by its text.
  - `get_list_of_questions` is inturduced to get the list of questions in the form.
  - `create_submission` is intruduced to create a submission for the form.
  - `create_submission_using_another` is intruduced to create a submission for the form using another submission.
  - `turn_into_american_datetime_format` is refactored and now throwing an error if the input is not a valid datetime, and typing is added.
  - `update_submission_answer` is refactored

- 2024-06-11 v2.0.1:
  - made changes on the `set_answer` function, now it can set the value of the field even if it is a multiselect checkbox.

- 2024-04-09 v2.0.0:
  - Fixed a bug where if the field is a multiselect checbkox, it was not changing the value via api

- 2024-04-04 v1.0.0:
  - Jjotform class is not containing less data on answers arr and dict also better performance, below elements now missing from the answers array:
    - `type`
    - `sublabels`
    - `timeFormat`

- 2023-04-26 v0.3.13:
  - Added `set_new_submission` function, time to time it cannot find the submission, in that cases pulls the data directly from the api and sets as it is.

- 2023-04-01 v0.3.12:
  - Added a logic for get_emails function. and added a TODO there.

- 2023-04-01 v0.3.11:
  - Setted set_answer function.

- 2023-04-10 v0.3.10:
  - Deleted submissions array and enhanced the logic according to it

- 2023-04-16 v0.3.9:
  - Created emails on class initilaization so that one dont need to call get_emails function

- 2023-04-16 v0.3.8:
  - Summary for get_form function, format document, cleared some of the self.update and its fucntionality for faster performance

- 2023-10-20 v0.3.7:
  - Force parameter for update function so that user can call it without depending on the submission count change, This library need an inner check for the highest updated_at value descending order. 

- 2023-11-08, v0.3.6:
  - Unused param selectedFields is omited
  - Added constructer function for answer to smaller parts [maxValue, order, selectedField, cfname, static]

- 2023-12-14, v0.4.0:
  - Added `delete_submission` call for JotForm class
  - From requests.request("TYPE", "url", "timeout") to requests."type"("url", "timeout")
  - pyproject.toml enhanced
  - Class explanation implemented for JotFormSubmission
  - Added following functions for JotFormSubmission class:
    - `turn_into_american_datetime_format`
    - `text_to_html`
    - `split_domain_from_email`
    - `get_value`
  - bin file intruduced for cli usage
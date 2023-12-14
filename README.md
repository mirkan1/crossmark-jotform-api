# Jotform api library for python3
<div style="text-align: center;">
  <img src="https://raw.githubusercontent.com/mirkan1/crossmark-jotform-api/master/logo.png">
</div>

## description
Unofficial Jotform API library for python3.
## updates
- 2023-04-26: Added `set_new_submission` function, time to time it cannot find the submission, in that cases pulls the data directly from the api and sets as it is.
- 2023-05-01: Added a logic for get_emails function. and added a TODO there.
- 2023-05-01: Setted set_answer function.
- 2023-05-10: Deleted submissions array and enhanced the logic according to it
- 2023-05-16: Created emails on class initilaization so that one dont need to call get_emails function
- 2023-05-16: Summary for get_form function, format document, cleared some of the self.update and its fucntionality for faster performance
- 2023-10-20: force parameter for update function so that user can call it without depending on the submission count change, This library need an inner check for the highest updated_at value descending order. 
- 2023-11-08, v0.3.6: 
  * Unused param selectedFields is omited
  * Added constructer function for answer to smaller parts [maxValue, order, selectedField, cfname, static]
- 2023-12-14, v0.4.0: 
  * Added `delete_submission` call for JotForm class
  * From requests.request("TYPE", "url", "timeout") to requests."type"("url", "timeout")
  * pyproject.toml enhanced
  * Class explanation implemented for JotFormSubmission
  * Added following functions for JotFormSubmission class:
    * `turn_into_american_datetime_format`
    * `text_to_html`
    * `split_domain_from_email`
    * `get_value`
  * bin file intruduced for cli usage




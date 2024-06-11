
- 2024-06-11 v2.0.1:
  * made changes on the `set_answer` function, now it can set the value of the field even if it is a multiselect checkbox.
- 2024-04-09 v2.0.0:
  * Fixed a bug where if the field is a multiselect checbkox, it was not changing the value via api
- 2024-04-04 v1.0.0:
    * Jjotform class is not containing less data on answers arr and dict also better performance, below elements now missing from the answers array:
        * `type`
        * `sublabels`
        * `timeFormat`
- 2023-04-26 v0.3.13: 
  * Added `set_new_submission` function, time to time it cannot find the submission, in that cases pulls the data directly from the api and sets as it is.
- 2023-04-01 v0.3.12: 
  * Added a logic for get_emails function. and added a TODO there.
- 2023-04-01 v0.3.11: 
  * Setted set_answer function.
- 2023-04-10 v0.3.10: 
  * Deleted submissions array and enhanced the logic according to it
- 2023-04-16 v0.3.9: 
  * Created emails on class initilaization so that one dont need to call get_emails function
- 2023-04-16 v0.3.8: 
  * Summary for get_form function, format document, cleared some of the self.update and its fucntionality for faster performance
- 2023-10-20 v0.3.7: 
  * Force parameter for update function so that user can call it without depending on the submission count change, This library need an inner check for the highest updated_at value descending order. 
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
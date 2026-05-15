\# A Simple tool for collection of Steam game review data.



Simple data orgnization and AI rating is supported by the tool



The project includes:



\- ▢ Simple config UI based on streamlit;

\- ▢ Convert json into CSV files;

\- ▢ We use AI platform to give the comments a simple rating (only Deepseek platform is supported, "deepseek-reasonner" is the default model)



How to use:



1\. First, you should have an original json, and save it into the "o\\\_json";

2\. You should convert json into csv, and the result would be saved in "o\\\_csv";

3\. Then you can give the csv to AI (You should have an API key first);

4\. The tool will obtain all the comment text contents from the CSV file, send them to the AI for scoring. The default scoring items include 'emotional feedback', 'reply length', 'emotional proportion', and 'tag';

5\. Finally, you can find the result in "data".



This tool would be used to finish the college final exam report. Good Luck awa!



By YGZxingnaoP


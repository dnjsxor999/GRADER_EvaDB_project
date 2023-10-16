# GRADER_EvaDB_project
## CS-4420 EvaDB project
### Name: Wontaek Kim

This app is to grade the answer based on the Rubric that you can provide or automatically generate.
This app is powered by [EvaDB](https://evadb.readthedocs.io/en/latest/index.html)'s Python API and [LLM](https://github.com/simonw/llm) library.


### Setup

Ensure that the local Python version is >= 3.8. Install the required libraries:
```
pip install -r requirements.txt
```
### Usage
Run script:
```
python -m GRADER.py
```
If you don't have an OpenAI key, follow the instructions below:

Login to [OpenAI](https://openai.com/) website and go to the API section.
Click the `Personal` tab on the top right of your screen, and navigate to `View API keys` section.
Click on `Create new secret key button`, give a nickname and copy the API Key that shows up.
Make sure to backup the key somewhere and keep it safe since OpenAI will now show you the complete key again.
Voila! You can now use your very own API key for using OpenAI API's within your applications.

NOTE : Free accounts have a 15$ API limit passing which you will either have to create a new account or take the premium subscription.

### Example

The example questions and answers can be found in `Question and Answers examples.pdf` file in this repository.
Also, you can find the sample rubric for each example question in this repository. (i.e `rubric_example_0`, `rubric_example_1`, and `rubric_example_2`)


```
=================================================================================================
|| 👋 Welcome to GRADER, This app is going to grade your answer based on your/generated rubric ||
||             << You will need the 'Problem' and 'Answer' you want to score >>                ||
=================================================================================================

📖 Provide 'Question' here :: 
Compare "base + offset" and "base + index" addressing modes. Give one example of when we might use "base + offset", and one when we might use "base + index".
🖍 Provide 'Answer' you want to grade here :: 
"Base + offset" calculates addresses using an absolute offset, whereas "base + index" calculates addresses using an offset multiplied by a fixed constant. "Base + offset" can be used to access members of a struct. "Base + index" can be used to access array elements, especially when using a counter to loop through all elements of the array.
📄 Do you have a rubric for this question?, then please give me. 
('yes' for using your rubric / 'no' for using automatic generated rubric) :: 
yes
🔒 Enter your OpenAI key :: [Your OpenAI API key]
📂 Enter the local path to your rubric pdf :: 
[Your local path to rubric pdf, it should be formatted numbering and each section has "[points type] [points value] points: [requirement]"]
⏳ Moving your file into current directory...
✅ Rubric moved successfully from [source path] to [current path]
(✅ Your Rubric is alread in this current directory!) [If your rubric file is in the current directory]

...
(if you do not have a rubric, need to generate the rubric by LLM)
📄 Do you have a rubric for this question?, then please give me. 
('yes' for using your rubric / 'no' for using automatic generated rubric) :: 
no
✔ How many rubrics you need? (only integer) :: 
4
✔ What is the total score is this question? (only integer) :: 
24                     
⏳ Generating Rubric by using LLM (may take a while)...
...

⏳ Loading Rubric into EvaDB Table
✅ Rubric successfully generated!
⏳ Parsing Rubric to make Standard Rubric
✅ Standard Rubric table successfully stored!
⏳ Grading now (may take a while)...
--------------------------------------------------
|| ✅The total score is ::  (score / total score)  ||
--------------------------------------------------
👋 Session ended.
--------------------------------------------------
```

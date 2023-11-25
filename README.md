# GRADER_EvaDB_project
## CS-4420 EvaDB project
### Name: Wontaek Kim

This app is to grade the answer based on the Rubric that you can provide or automatically generate.
This app is powered by [EvaDB](https://evadb.readthedocs.io/en/latest/index.html)'s Python API and [LLM](https://github.com/simonw/llm) library.


### Setup

Ensure that the local Python version is >= 3.8. Install the required libraries:
```
python -m venv evadb-venv
source evadb-venv/bin/activate
pip install -r requirements.txt
```
### Usage
Run script:
```
python GRADER.py
```


**After first running `python GRADER.py`, you should replace the `functions` folder (which contains "LLMFunction.py", "LLMExplanation.py", and "sentence_feature_extractor.py") with generated `functions` folder in `evadb_data` folder.**

If you don't have an OpenAI key, follow the instructions below:

Login to [OpenAI](https://openai.com/) website and go to the API section.
Click the `Personal` tab on the top right of your screen, and navigate to `View API keys` section.
Click on `Create new secret key button`, give a nickname and copy the API Key that shows up.
Make sure to backup the key somewhere and keep it safe since OpenAI will now show you the complete key again.
You can now use your very own API key for using OpenAI API's within your applications.

NOTE : Free accounts have a 15$ API limit passing which you will either have to create a new account or take the premium subscription.

### Example

The example questions and answers can be found in `Question and Answers examples.pdf` file in this repository.
Also, you can find the sample rubric for each example question in this repository. (i.e `rubric_example_0`, `rubric_example_1`, and `rubric_example_2`)

[upadate] you can upload the pdf files (i.e textbooks) in `pdf` folder for generating the reference to help students by giving relevance data.
Here, for example, "Umakishore Ramachandran_ William D. Leahy Jr - Computer Systems_ An Integrated Approach to Architecture and Operating Systems-Pearson (2010).pdf" is pre-uploaded for testing the example questions and answers.


```
=================================================================================================
|| 👋 Welcome to GRADER, This app is going to grade your answer based on your/generated rubric ||
||             << You will need the 'Problem' and 'Answer' you want to score >>                ||
=================================================================================================

🖍 Provide 'Question' here ::
[Paste the question here]
(i.e Compare "base + offset" and "base + index" addressing modes. Give one example of when we might use "base + offset", and one when we might use "base + index".)
🖍 Provide 'Answer' you want to grade here ::
[Paste the answer you want to grade here]
(i.e "Base + offset" calculates addresses using an absolute offset, whereas "base + index" calculates addresses using an offset multiplied by a fixed constant. "Base + offset" can be used to access members of a struct. "Base + index" can be used to access array elements, especially when using a counter to loop through all elements of the array.)
📄 Do you have a rubric for this question?, then please give me. 
('yes' for using your rubric / 'no' for using automatic generated rubric) :: 
yes
📖 Do you have a reference for this question?, and want to generate reference from your textbook pdf? 
                         (If you want, you have to place your pdf in pdf folder in this current path.) :: 
yes
🔒 Enter your OpenAI key :: [Your OpenAI API key]
📂 Enter the local path to your rubric pdf :: 
[Your local path to rubric pdf, it should be formatted numbering and each section has "[points type] [points value] points: [requirement]"]
⏳ Moving your file into current directory...
✅ Rubric moved successfully from [source path] to [current path]
(✅ Your Rubric is already in this current directory!) [If your rubric file is in the current directory]

...
(if you do not have a rubric, need to generate the rubric by LLM)
📄 Do you have a rubric for this question?, then please give me. 
('yes' for using your rubric / 'no' for using automatic generated rubric) :: 
no
✔ How many rubrics you need? (only integer) :: 
4
✔ What is the total score of this question? (only integer) :: 
24                     
⏳ Generating Rubric by using LLM (may take a while)...
...

⏳ Loading Rubric into EvaDB Table
✅ Rubric successfully generated!
⏳ Parsing Rubric to make Standard Rubric
✅ Standard Rubric table successfully stored!
⏳ Grading now (may take a while)...

llm response for rubric no.1 : by  tough  grader,  4 / 6
llm response for rubric no.2 : by  tough  grader,  6 / 6
llm response for rubric no.3 : by  tough  grader,  4 / 6
llm response for rubric no.4 : by  tough  grader,  6 / 6
llm response for rubric no.1 : by  moderate  grader,  5 / 6
llm response for rubric no.2 : by  moderate  grader,  6 / 6
llm response for rubric no.3 : by  moderate  grader,  6 / 6
llm response for rubric no.4 : by  moderate  grader,  6 / 6
llm response for rubric no.1 : by  merciful  grader,  6 / 6
llm response for rubric no.2 : by  merciful  grader,  6 / 6
llm response for rubric no.3 : by  merciful  grader,  6 / 6
llm response for rubric no.4 : by  merciful  grader,  6 / 6
-------------------------------------------
❓Do you want get feedback for student's answer? :: 
yes
+-------------+---------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------------+
|   Rubric no |   total point |   get point | feedback                                                                                                                                       |
|-------------+---------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------------|
|           1 |             6 |     5       | The student's answer accurately explains the difference between "base + offset" and "base + index" and provides examples of when each is used. |
|           2 |             6 |     5.33333 | The student accurately explains the difference between base + offset and base + index and provides examples of when each can be used.          |
|           3 |             6 |     4.66667 | The student's answer accurately defines "base + index" and "base + offset" and provides examples of their usage.                               |
|           4 |             6 |     6       | The student accurately identifies the difference between base + offset and base + index and provides examples of when each is used.            |
+-------------+---------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------------+
--------------------------------------------------
|| ✅The total score is ::  (score / total score)  ||
--------------------------------------------------
textbook ,  Umakishore Ramachandran_ William D. Leahy Jr - Computer Systems_ An Integrated Approach to Architecture and Operating Systems-Pearson (2010).pdf
⏳loading textbook into database...
✅success loading pdf textbook
⏳creating sentence feature extractor function...
✅success create sentence feature extractor function
⏳making vecter database...
✅success make index
⏳searching reference... 

Based on your PDF: 
-------------------------------------------
[page : 280, paragraph : 3 => ...Figure 7.4: Base and Limit Registers The architectural enhancements ......]
[page : 48, paragraph : 2 => ...]
[page : 39, paragraph : 2 => ...]
[page : 70, paragraph : 3 => ...]
[page : 298, paragraph : 9 => ...]
[references print out here]

👋 Session ended.
--------------------------------------------------
```

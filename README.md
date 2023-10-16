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

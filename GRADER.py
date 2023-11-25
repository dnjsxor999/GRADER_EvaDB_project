import os
import shutil
from typing import Dict, List
import pandas as pd
import llm
from tabulate import tabulate


from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain


# from langchain.chat_models import ChatOpenAI
# from langchain.chains import RetrievalQA
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate
# import pinecone

################################################################
# Import the EvaDB package
import evadb
# Connect to EvaDB and get a database cursor for running queries
import warnings
warnings.filterwarnings("ignore")
################################################################

'''
1. get input
-> Problem
-> Student's Answer
-> Rubric
    - from llm by using Problem -> db
    - from pdf -> db
-> parsing and store them into "Grade_standard" db

2. get score 
-> ask llm to grade based on the each rubric section, and 
    make db for storing score for each rubric section like 
    1. | 3/6 | reasons...
    2. | 6/6 | reasons...
    ...
-> merciful, moderate, tough
    get the score from those three scores and get average

-> get report for explaining the reasons why it has this grade
    -> hugface?

-> out
'''


NEW_RUBRIC_PATH = os.path.join("evadb_data", "tmp", "new_rubric.csv")
RUBRIC_NO = 0
BOUND_SCORE = 0
feedback_grid = dict() # key : rubric no, value : feedback for that rubric
Final_score = dict()

def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")

def handle_user_input() -> Dict:
    """
    Receives user input.

    Returns:
        user_input (dict): global configuration
    """

    print(
        "=================================================================================================\n\
|| 👋 Welcome to GRADER, This app is going to grade your answer based on your/generated rubric ||\n\
||             << You will need the 'Problem' and 'Answer' you want to score >>                ||\n\
=================================================================================================\n"
    )

    question_str = str(
        input(
            "🖍 Provide 'Question' here :: \n"
        )
    )

    question_str = question_str.replace("\"", "")

    answer_str = str(
        input(
            "🖍 Provide 'Answer' you want to grade here :: \n"
        )
    )

    answer_str = answer_str.replace("\"", "")


    use_rubric_pdf = None
    while True:
        if use_rubric_pdf in ["y", 'yes']:
            use_rubric = True
            break
        elif use_rubric_pdf in ["n", "no"]:
            use_rubric = False
            break
        else:
            use_rubric_pdf = str(
                input(
                    "📄 Do you have a rubric for this question?, then please give me. \n\
('yes' for using your rubric / 'no' for using automatic generated rubric) :: \n"
                ).lower()
            )

    use_reference_pdf = None
    while True:
        if use_reference_pdf in ["y", 'yes']:
            use_reference = True
            break
        elif use_reference_pdf in ["n", "no"]:
            use_reference = False
            break
        else:
            use_reference_pdf = str(
                input(
                    "📖 Do you have a reference for this question?, and want to generate reference from your textbook pdf? \n\
                         (If you want, you have to place your pdf in pdf folder in this current path.) :: \n"
                ).lower()
            )
    
    user_input = {'question' : question_str,
                  'answer' : answer_str,
                  'use_rubric' : use_rubric,
                  'referecne_pdf' : use_reference} # str, str, bool
    
    return user_input



def get_rubric_pdf():

    current_directory = os.getcwd()
    rubric_pdf_local_path = str(
        input(
            "📂 Enter the local path to your rubric pdf :: \n"
        )
    )
    
    rubric_name = os.path.basename(rubric_pdf_local_path)
    user_input['rubric_pdf_name'] = rubric_name

    check_file_here = os.path.join(current_directory, rubric_name)

    if os.path.exists(check_file_here):
        print("✅ Your Rubric is already in this current directory!")
    else:
        print("⏳ Moving your file into current directory...")
        try:
            shutil.move(rubric_pdf_local_path, current_directory)
            print(f"✅ Rubric moved successfully from '{rubric_pdf_local_path}' to '{current_directory}'")
        except FileNotFoundError:
            print("❓ Source file not found, check your local path again")
        except PermissionError:
            print("❗️ Permission denied. Make sure you have the necessary permissions to move the file.")
        except Exception as e:
            print(f"❗️ An error occurred: {e}")

    # print(user_input)
    print("⏳ Loading Rubric into EvaDB Table")
    cursor.query("DROP TABLE IF EXISTS Rubric_PDF;").df()
    cursor.query("LOAD PDF '{}' INTO Rubric_PDF;".format(user_input['rubric_pdf_name'])).df()
    # print(cursor.query("SELECT * FROM Rubric_PDF").df())
    print("✅ Rubric successfully generated!")
    return

def generate_rubric():
    # llm 이용 promt(..., system="~") -> get rubric -> store them into table
    # -> JSON format
    global RUBRIC_NO
    global BOUND_SCORE

    rubric_no_request = int(
        input(
            "✔ How many rubrics you need? (only integer) :: \n"
        )
    )

    total_score_request = int(
        input(
            "✔ What is the total score is this question? (only integer) :: \n"
        )
    )

    # Generating Prompt => (takes 266 tokens for template) + (question's token) <= ~500
    PROMPT_RUBRIC = '''
                    [no prose]
                    [Output only JSON]
                    Give me {rubrics_no} grading rubrics for total {total_score} points for below question:
                    "{question}"
                    Do not include any explanations, only provide compliant JSON response following this format without deviation:
                    [{{
                        point_type: "+",
                        points: value of point,
                        requirement: in one string sentence
                    }}]
                    '''.format(rubrics_no = rubric_no_request,
                               total_score = total_score_request,
                               question = user_input["question"])
    # print(PROMPT_RUBRIC)
    print("⏳ Generating Rubric by using LLM (may take a while)...")
    response = model.prompt(PROMPT_RUBRIC,
                            system="Answer like you are Teaching Assistant", temperature=0.5)
    

    # json parsing
    try:
        df_json = pd.read_json(str(response))
        RUBRIC_NO = df_json.shape[0]
        BOUND_SCORE = total_score_request
        df_json['rubric_no'] = df_json.index + 1
        df_json.to_csv(NEW_RUBRIC_PATH, index=False)
        print("✅ Rubric successfully generated!")
    except ValueError:
        print("🔁 wrong format of JSON from llm, run again")
    except Exception as e:
        print(f"❗️ An error occurred: {e}")
        exit(0)

def split_string(text):
    parts = text.split(':') # must be formatted by "part1 : part2"
    if len(parts) == 2:
        part1 = parts[0].replace(" ", "")  ###### numbering 1,2,...
        part1 = part1.strip()
        part2 = parts[1].strip()
        return [part1[2], int(part1[3]), part2] ###### numbering, should be less than 10
    return [None, None, None]

def make_standard_rubric():
    global RUBRIC_NO
    global BOUND_SCORE
    
    #parsing -> point_type, point, requirements
    if user_input["use_rubric"]:
        # print(cursor.table("Rubric_PDF").select("data").df())
        data_column = cursor.table("Rubric_PDF").select("data").df()["data"]
        # print(data_column)
        new_data_column = data_column.apply(split_string).apply(pd.Series)
        new_data_column.columns = ['point_type', 'points', 'requirement']
        # print(new_data_column)
        RUBRIC_NO = new_data_column.shape[0]
        BOUND_SCORE = new_data_column["points"].sum()
        new_data_column['rubric_no'] = new_data_column.index + 1
        new_data_column.to_csv(NEW_RUBRIC_PATH)

    print("⏳ Parsing Rubric to make Standard Rubric")
    cursor.query("DROP TABLE IF EXISTS Grade_standard;").df()
    cursor.query(
        '''CREATE TABLE IF NOT EXISTS Grade_standard (point_type TEXT(1), points INTEGER, requirement TEXT(300), rubric_no INTEGER);'''
    ).df()
    cursor.load(NEW_RUBRIC_PATH, "Grade_standard", "csv").execute()

    print("✅ Standard Rubric table successfully stored!")
    return

def grading():
    global Final_score
    print("⏳ Grading now (may take a while)...")

    # create LLM function
    cursor.query("CREATE FUNCTION IF NOT EXISTS LLMFunction IMPL 'evadb_data/functions/LLMFunction.py'").df()

    student_answer =user_input['answer']
    PROMPT_GRADING = f'''
                        "Based on the given criteria score/grade this student's answer: '{student_answer}',
                        Don't include any explanations in your responses, only provide just one single integer that student will get (i.e '3'), and not greater than total score."
                    '''
    query_input = f""" SELECT LLMFunction({PROMPT_GRADING}, requirement, points) FROM Grade_standard;
    """
    get_result = cursor.query(query_input).execute()
    
    grade_grid = {
        0 : 0,
        1 : 0,
        2 : 0
        }
    Final_score = {
        0 : [],
        1 : [],
        2 : [],
        3 : [],
        }
    
    # key : rubric no, value : score of that rubric
    for index, row in get_result.iterrows():
        grade_grid[int(index // RUBRIC_NO)] += int(row['response'])
        Final_score[int(index % RUBRIC_NO)].append(int(row['response']))
    average_score = 0
    for i in range(3):
        average_score += grade_grid[i]
    for i in range(RUBRIC_NO):
        Final_score[i] = [sum(Final_score[i]) / len(Final_score[i])]

    return round(average_score / 3, 2)

def generate_feedback():
    global feedback_grid

    student_answer =user_input['answer']
    PROMPT_EXPLANATION = f'''
                        "Based on the given criteria/requirment for grading this studnet's answer: '{student_answer}',
                        Please provide feedback for this student's answer in one line."
                        '''
    cursor.query("CREATE FUNCTION IF NOT EXISTS LLMExplanation IMPL 'evadb_data/functions/LLMExplanation.py'").df()

    query_input = f""" SELECT LLMExplanation({PROMPT_EXPLANATION}, requirement) FROM Grade_standard;
    """
    get_feedback = cursor.query(query_input).execute()

    
    for index, row in get_feedback.iterrows():
        feedback_grid[index] = [row['response']]
    return

def combine_score_on_rubric():
    give_feedback = None
    while True:
        if give_feedback in ["y", 'yes']:
            feedback_on = True
            break
        elif give_feedback in ["n", "no"]:
            feedback_on = False
            break
        else:
            give_feedback = str(
                input(
                    "❓Do you want get feedback for student's answer? :: \n"
                ).lower()
            )

    rubric_no_it = cursor.query("SELECT rubric_no FROM Grade_standard").df()
    bound_score_each_rubric = cursor.query("SELECT points FROM Grade_standard").df()

    print(bound_score_each_rubric)

    df1 = pd.DataFrame(Final_score)
    if feedback_on:
        generate_feedback()
        df2 = pd.DataFrame(feedback_grid)
        graded = pd.concat([rubric_no_it, bound_score_each_rubric, df1.T, df2.T], axis = 1)
        graded.columns = ['Rubric no','total point','get point','feedback']
    else:
        graded = pd.concat([rubric_no_it, bound_score_each_rubric, df1.T])
        graded.columns = ['Rubric no','total point','get point']
    print(tabulate(graded, headers='keys', tablefmt='psql', showindex=False))
    # print(df1.T)
    # print(df2)
    return


def generate_reference():
    ## project 2 ->> Chroma

    path = "pdf"
    dir_list = os.listdir(path)

    print("textbook , ", dir_list[0])

    full_path = os.path.join(path, dir_list[0])

    #load pdf textbook
    print("⏳loading textbook into database...")
    cursor.query("DROP TABLE IF EXISTS textbook;").df()
    cursor.query("LOAD PDF '{}' INTO textbook;".format(full_path)).df()
    text_book_df = cursor.query("SELECT * FROM textbook;").df()
    text_book_row_no = text_book_df.shape[0]
    print("✅success loading pdf textbook")

    # make vector data table
    # cursor.query("DROP TABLE IF EXISTS textbook_embedded;").df()
    # cursor.query("USE postgres { CREATE TABLE textbook_embedded (data NdArrayType.FLOAT128, num INT) }").df()
    # for i in range(text_book_row_no):
    #     vector = embeddings.embed_query(text_book_df.iloc[i]['data'])
    #     cursor.query(f"USE postgres {{ INSERT INTO textbook_embedded (data, num) VALUES ('{vector}', {i}) }}").df()
    # print("success make vectors in table")

    print("⏳creating sentence feature extractor function...")
    cursor.query("CREATE FUNCTION IF NOT EXISTS SentenceFeatureExtractor IMPL 'evadb_data/functions/sentence_feature_extractor.py'").df()
    print("✅success create sentence feature extractor function")

    # make index
    print("⏳making vecter database...")
    cursor.query("CREATE INDEX reference ON textbook (SentenceFeatureExtractor(data)) USING QDRANT;").df()
    print("✅success make index")

    # search similarity
    print("⏳searching reference... \n")
    response = cursor.query(f"""
                                SELECT * FROM textbook ORDER BY
                                Similarity(
                                SentenceFeatureExtractor('{user_input['question']}'),
                                SentenceFeatureExtractor(data)
                                )
                                LIMIT 5
                            """).df()

    print("Based on your PDF: ")
    print("-------------------------------------------")
    for index, row in response.iterrows():
        print("[page : " + str(row["page"]) + ", " + "paragraph : " + str(row["paragraph"]) + " => " + "..." + str(row["data"]) + "... ] \n")

    return

    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)

    # loader = PyPDFLoader(full_path)
    # try:
    #     data = loader.load()
    #     print (f'You have {len(data)} document(s) in your data')

    # except Exception as e:
    #     print(f"❗️ An error occurred in loading the pdf: {e}")
    

    # texts = text_splitter.split_documents(data)
    # print (f'Now you have {len(texts)} documents')

    # vectorstore = Chroma.from_documents(texts, embeddings)

    # query = user_input["question"]
    # docs = vectorstore.similarity_search(query)

    # chain = load_qa_chain(llm= model, chain_type= "stuff")

    # print("-------------------------------------------")
    # print("Based on your PDF: \n" +        
    #     chain.run(input_documents=docs, question=query) + " \n \n Here are the references from your PDF: \n")
    # ref_no = 1
    # for doc in docs:
    #     print(ref_no + ". " + doc.page_content)
    #     ref_no += 1
    

        

        # batch_num = len(texts)
        # for i in range(batch_num):
        #     batch = texts[i].page_content
        #     ids = "pdf_"+str(count)
        #     embeds = embeddings.embed_query(batch)
        #     # get metadata to store in Pinecone
        #     metadata = texts[i].metadata
        #     metadata["text"] = batch
        #     # add to Pinecone
        #     vectors.append((ids, embeds, metadata))
        #     count += 1
        # # Upsert into Pinecone index
        # try:
        #     print("upserting vector pdf")
        #     index.upsert(vectors=vectors)
        # except Exception as e:
        #     print(f"❗️ An error occurred: {e}")


if __name__ == "__main__":
    
    # cleanup()
    # try_to_import_llm()
    cursor = evadb.connect().cursor()

    # postgres_params = {
    #     "user": "evadb",
    #     "password": "1234",
    #     "host": "127.0.0.1",
    #     "port": "5432",
    #     "database": "testdb",
    # }
    # cursor.query(f"CREATE DATABASE IF NOT EXISTS postgres WITH ENGINE = 'postgres', PARAMETERS = {postgres_params}").df()


    user_input = handle_user_input()

    try:
        # get OpenAI key
        model = llm.get_model("gpt-3.5-turbo")
        try:
            model.key = os.environ['OPENAI_KEY']
        except KeyError:
            model.key = str(input("🔒 Enter your OpenAI key :: "))
            os.environ["OPENAI_KEY"] = model.key
        # print(user_input)

        # test()
        if user_input['use_rubric']:
            get_rubric_pdf()
        else:
            generate_rubric()
        
        make_standard_rubric()

        total_score = grading()

        #combine and make grid
        print("-------------------------------------------")
        combine_score_on_rubric()
        print("-------------------------------------------")
        print("|| ✅The total score is :: ", total_score, "/", BOUND_SCORE , " ||")
        print("-------------------------------------------")

        # generate 
        if user_input['referecne_pdf']:
            embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_KEY"])
            generate_reference()

            # try:
            #     PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
            #     PINECONE_API_ENV = os.environ['PINECONE_API_ENV']
            # except KeyError:
            #     PINECONE_API_KEY = str(input("🔒 Enter your Pinecone API key :: "))
            #     PINECONE_API_ENV = str(input("🔒 Enter your Pinecone API env :: "))

            # pinecone.init(
            #     api_key=PINECONE_API_KEY,  # find at app.pinecone.io
            #     environment=PINECONE_API_ENV  # next to api key in console
            # )
            # index_name = "grader-reference"  # put in the name of your pinecone index here
            # index = pinecone.Index('grader-reference')
            
        print("👋 Session ended.")
        print("-------------------------------------------")
    except KeyboardInterrupt:
        print("❎ You ended session!")
    except Exception as e:
        # cleanup()
        print("❗️ Session ended with an error.")
        print(e)
        print("===========================================")

    exit(0)
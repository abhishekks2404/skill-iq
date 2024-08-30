import os
import openai
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import chardet
import re
import json
import collections


from sales_iq_graph import create_advancement_chart,create_spider_chart, grade_wise_data_for_spider
# Load the .env file
load_dotenv()

if "panel" not in st.session_state:
    st.session_state.panel = False

st.set_page_config(page_title="SalesIQ", layout='wide')
st.markdown("<h1 style='text-align: center; color: grey;'>Sales IQ</h1>", unsafe_allow_html=True)

input_key = st.text_input("Enter your OpenAI API key:", type="password")
button = st.button("Set API Key")
if input_key and button :
    openai.api_key = input_key    
    st.session_state.panel = True

if not st.session_state.panel:
    st.error("Please enter your OpenAI API key.")


# Get the API key from the .env file
# openai_api_key = os.getenv('OPENAI_API_KEY')
# openai.api_key =openai_api_key

def generate_progress_data(json_data):
    # Define the keys we are interested in
    keys = ['Decision Criteria', 'Economic Buyer', 'Metrics', 'Competition', 'Champion', 'Identify Pain', 'Decision Process']
 
    progress_data = {}
    for i, (transcript_key, transcript_values) in enumerate(json_data.items(), start=1):
        progress_key = f'Transcript {i}'
        # Map the values directly from the transcript to the progress data
        progress_data[progress_key] = {key: int(transcript_values[key]) for key in keys}
 
    return progress_data

def get_folders_in_directory():
    '''
    List all the directories in the given directory path
    '''
    directory_path = './Transcripts' 
    folders = [name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]
    return folders

def get_files_in_directory(selected_folder):
    '''
    List all the files in the given directory path
    '''
    directory_path = f'./Transcripts/{selected_folder}'  # Replace with your directory path
    files = [name for name in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, name))]
    return files


def AudioCall_Assessment_Deal_StageLevel(Transcript,Sale_deal_stages_description,skill_levels_description):
    try:
        
        
        json_file = {
            'deal_stage_level': 'Sales level should be mentioned here','deal_stage_explanation' : 'Provide short explanation for the score of deal_stage_level',
            'skill_level': 'Skill levels should be mentioned here',
            'skill_stage_explanation' : 'Provide short explanation for the score of skill_level'
            }
        
        prompt = f'''
                Transcript: {Transcript}
                Sale_deal_stages_description: {Sale_deal_stages_description}
                Skill_levels_description: {skill_levels_description}

                Understand the Sales Deal Stage and Skill Level description properly then proceed ahead.

                The provided transcript is from a sales audio call. The `Sale_deal_stages_description` outlines the various stages of a sales deal, while the `Skill_levels_description` details different levels of skills. Your task is to thoroughly analyze both the deal stages and skill levels descriptions and accurately match the transcript to the most suitable deal stage and skill level.

                Please identify:
                1. The appropriate sales deal stage based on the `Sale_deal_stages_description`.
                2. The appropriate skill level based on the `Skill_levels_description`.
                Output should have only json in it. DO not mention any other text.
                Return the result in a structured JSON format as follows:
                {json_file}

                Ensure that the output is consistent and repeatable for the same transcript.
                '''

        # Making a request to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # or another model version, check OpenAI's API documentation for the latest models
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        # Extracting the text from the response
        result = response.choices[0].message['content'].strip()
        # print("\033[32mResult:", result, "\033[0m")         # print(result)
        # result = result.replace('```json', '').replace('```', '')
        # json_data = json.loads(result)

        match = re.search(r'```json(.*?)```', result, re.DOTALL)

        if match:
            result = match.group(1).strip()
            json_data = json.loads(result)
            print("Fetched Stage Level and Skill Level")
            return json_data

        else:
            result = ""


    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_question_df_from_file(stage_level,skill_level):
    stage_level = stage_level.strip()
    skill_level = skill_level.strip()
    
    # print("Inside the function : ",stage_level,skill_level)
    path_file = "Skill_Framework.xlsx"
    df = pd.read_excel(path_file, sheet_name="Skills Framework")
    filtered_df = df[(df['Stage'] == stage_level) & (df['Skill Level'] == skill_level)]

    questions = []

    for index, row in filtered_df.iterrows():
        meddpic = row["MEDDPIC Component"]

        ai_assessment = row["AI Assessment"]
        question = f"{meddpic} : {ai_assessment}"
        questions.append(question)
    
    return questions

def get_average_metrics(deal_levels):
    fields_to_average = ['Decision Criteria', 'Economic Buyer', 'Metrics', 'Competition', 'Champion', 'Identify Pain', 'Decision Process']
        
    averages = {field: 0 for field in fields_to_average}
    transcript_count = len(deal_levels)

    # Sum up the values for each field across all transcripts
    for transcript in deal_levels.values():
        for field in fields_to_average:
            averages[field] += int(transcript[field])

    # Calculate the average for each field
    for field in averages:
        averages[field] /= transcript_count
    
    return averages

def get_stage_level_description(stage_level):
    stage_level = stage_level.strip()
    path_file = "Skill_Framework.xlsx"
    df = pd.read_excel(path_file, sheet_name="stage level")
    description = df.loc[df['Stage'] == stage_level, 'Stage Description']
    
    if not description.empty:
        description = {stage_level : description.iloc[0]}
        return description
    else:
        return "Stage level not found."
    

def get_skill_level_description(skill_level):
    skill_level = skill_level.strip()
    path_file = "Skill_Framework.xlsx"
    df = pd.read_excel(path_file, sheet_name="Skill Levels")

    description = df.loc[df['Level'] == stage_level, 'Description']

    if not description.empty:
        return description.iloc[0]
    else:
        return "Skill level not found."
    



def AudioCall_Assessment_Skill_Level_Score(Transcript,QuestionSet,skills_list,Skill_level_description,Deal_stage_description):
    try:
        scoring_instructions = """
        - 1: Not Mentioned / No Questions / Not Addressed / Not Confirmed / Not Used / Not Recognized / Incorrectly Differentiated
        - 2: Incorrect / Irrelevant Questions / Vaguely Addressed / Partially Confirmed / Used but Ineffectively / Recognized but Not Recorded
        - 3: Correct but Ineffective / Relevant but Inconclusive / Addressed with Some Understanding / Confirmed with Clarification / Used with Some Effectiveness / Recognized and Partially Recorded / Some Differentiation
        - 4: Effective / Effective Questions / Clearly Addressed / Fully Confirmed / Effectively Used / Fully Recognized and Recorded / Clear Differentiation
        """
        json_file = {
            "Metrics" : "Provide score between 1 to 4",
            "Metrics_explanation" : "Provide short explanation for the score of Metrics",
            "Economic Buyer" : "Provide score between 1 to 4",
            "Economic Buyer_explanation" : "Provide short explanation for the score of Economic Buyer",
            "Decision Criteria" : "Provide score between 1 to 4",
            "Decision Criteria_explanation" : "Provide short explanation for the score of Decision Criteria",
            "Decision Process" : "Provide score between 1 to 4",
            "Decision Process_explanation" : "Provide short explanation for the score of Decision Process",
            "Identify Pain" : "Provide score between 1 to 4",
            "Identify Pain_explanation" : "Provide short explanation for the score of Identify Pain",
            "Champion" : "Provide score between 1 to 4",
            "Champion_explanation" : "Provide short explanation for the score of Champion",
            "Competition" : "Provide score between 1 to 4",
            "Competition_explanation" : "Provide short explanation for the score of Competition",
            "Final_Score" : "Take the Average of all the score and provide me the final score",
            "Demonstrated Skills":"Skills which are present in Transcript",
            "Skills to improve":"Skills which need to be improved",
            "New Skills to learn":"New skills which needs to be learnt"
        }
        prompt = f'''
            Transcript: {Transcript}\n
            scoring_instructions : {scoring_instructions}\n
            Questionset : {QuestionSet}\n
            skills_list : {skills_list }\n
            Skill_level_description : {Skill_level_description}\n
            Deal_stage_description : {Deal_stage_description }\n
            The given Transcript is transcription of Sales audio call, 
            assess the  transcript based on the Scoring_instructions for each question in QuestionSet. Provide a score between 1 and 4 for each question output. This is sensitive so provide it with best accuracy.
            In output give final Average score calculating average of all scores.
            Evaluate the  transcript to identify Demonstrated skills by sales agent from skills_list and identify skills need to improve and identify new skills to learn from skills_list. while evaluation of transcript consider Provided Deal_stage_description skill_level_description and  each question in QuestionSet 
            In output provide demonstrated skill, Skills which needs to improve and new skills needed to learn to perform job well without explaination.

            
            As an output provide me a only json with structure
            {json_file}

        '''
        
        # Making a request to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # or another model version, check OpenAI's API documentation for the latest models
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        # Extracting the text from the response
        result = response.choices[0].message['content'].strip()
        # result = result.replace('```json', '').replace('```', '')
        # json_data = json.loads(result)

        match = re.search(r'```json(.*?)```', result, re.DOTALL)

        if match:
            result = match.group(1).strip()
            json_data = json.loads(result)
            print("Fetched Metrics and Skills.")
            return json_data

        else:
            result = ""

        # print(json_data)
        return json_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


Sale_deal_stages_description = {
    "Excall Scheduled": "At this stage, the sales rep successfully schedules an initial discovery call with the lead. This call is intended to delve deeper into the lead's specific needs, challenges, and goals. The conversation focuses on understanding the lead’s requirements and setting the stage for potential solutions. Advancement criteria include having the call scheduled with the appropriate stakeholders and a clear agenda for the discussion.",
    "Scoping": "During the discovery call, the sales rep identifies a tangible opportunity that aligns with the lead's needs. This stage involves discussing specific use cases, potential solutions, and initial scoping of what the deal could involve. The sales rep gathers detailed information about the lead’s requirements and starts to shape a potential offer. Advancement to the next stage depends on the lead’s clear interest in moving forward and sufficient details being gathered to define the opportunity",
    "Opportunity Identified": "A tangible opportunity is identified in conversations with the prospect/customer and the lead is qualified as an SQL.",
    "Proposal Shared": "The sales rep creates and sends a formal proposal based on the discussions during the scoping stage. The proposal outlines how the solution will meet the lead’s needs, including pricing, timelines, and specific deliverables. This stage focuses on providing the lead with a clear understanding of the offering and setting expectations for the deal. Advancement occurs when the proposal is sent and acknowledged, with the lead indicating they are reviewing it.",
    "Feedback from Client": "The lead provides feedback on the proposal, which might include requests for modifications, clarifications, or additional information. This stage involves fine-tuning the proposal to ensure it aligns with the lead’s expectations and needs. The sales rep works closely with the lead to address any concerns or adjustments needed before finalizing the deal. Advancement to the next stage depends on the client’s continued interest and a clear path towards agreement.",
    "Negotiating": "The sales rep and client engage in detailed negotiations to finalize the deal. This includes discussing pricing, contract terms, implementation timelines, and any other specifics that need to be agreed upon. The goal is to reach a mutual understanding and agreement on all critical aspects of the deal. Advancement from this stage occurs when both parties agree on the terms and are ready to proceed to contract signing.",
    "Contracting": "The finalized contract is sent to the client for review and signature. This stage focuses on ensuring that all agreed-upon terms are documented and that the client is ready to formalize the agreement. The sales rep follows up to confirm receipt and address any final questions before signing. Advancement occurs when the contract is signed by both parties, making the deal official.",
    "Closed (Won)": "The deal is successfully closed, with the client signing the contract and officially becoming a customer. The focus now shifts to onboarding and implementation. The sales rep confirms the contract signing and coordinates with the relevant teams to begin delivering the agreed-upon services. This stage marks the completion of the sales process and the beginning of the client relationship."
}

skill_levels_description = {
    "Rookie": {
        "Metrics": "Understands basic metrics that indicate high-potential opportunities.",
        "Economic Buyer": "Identifies potential economic buyers through initial research and interactions.",
        "Decision Criteria": "Recognizes initial decision criteria through preliminary research.",
        "Decision Process": "Follows basic steps to understand the customer's buying process.",
        "Identify Pain": "Identifies surface-level customer pain points through initial research.",
        "Champion": "Recognizes individuals who might advocate internally based on initial interactions.",
        "Competition": "Identifies competitors through initial research and positions product strengths against them."
    },
    "Navigator": {
        "Metrics": "Utilizes metrics to qualify leads and evaluate opportunity potential.",
        "Economic Buyer": "Engages economic buyers and adapts communication to their interests.",
        "Decision Criteria": "Aligns product offerings with initial decision criteria identified through research.",
        "Decision Process": "Guides customers through the initial steps of the decision process.",
        "Identify Pain": "Articulates how products address specific customer pains identified through research.",
        "Champion": "Develops rapport with potential champions and fosters relationships.",
        "Competition": "Strategically positions products against competitors based on initial research."
    },
    "Specialist": {
        "Metrics": "Analyzes and discusses advanced metrics to drive qualification discussions and forecast outcomes.",
        "Economic Buyer": "Engages economic buyers with strategies that influence their buying decisions.",
        "Decision Criteria": "Integrates complex decision criteria into qualification discussions.",
        "Decision Process": "Manages and steers the decision process to ensure proper qualification.",
        "Identify Pain": "Identifies underlying or unexpressed customer pains through insightful questioning.",
        "Champion": "Develops deep relationships with champions to leverage their influence effectively.",
        "Competition": "Conducts in-depth comparisons and positions products against competitors during qualification discussions."
    },
    "Analyst": {
        "Metrics": "Uses data analysis to refine qualification strategies and improve targeting during calls.",
        "Economic Buyer": "Assesses the impact of economic buyers on the qualification process and tailors approaches accordingly.",
        "Decision Criteria": "Critically evaluates how well sales proposals meet the decision criteria of different stakeholders.",
        "Decision Process": "Analyzes the effectiveness of different sales tactics at various stages of the decision process.",
        "Identify Pain": "Leads team discussions on developing solutions for complex customer pains identified during sales interactions.",
        "Champion": "Strategizes on optimizing champion engagement to accelerate the qualification process.",
        "Competition": "Evaluates competitive landscape and advises team on counter-strategies during qualification calls."
    },
    "Innovator": {
        "Metrics": "Develops new metrics that predict customer behavior more accurately and shares insights.",
        "Economic Buyer": "Creates innovative approaches to influence economic buyers at key accounts.",
        "Decision Criteria": "Designs solutions that uniquely address evolving decision criteria trends.",
        "Decision Process": "Re-engineers sales processes based on detailed analysis of decision flow in key deals.",
        "Identify Pain": "Innovates solutions for market-wide pains, discussing these during industry forums or client presentations.",
        "Champion": "Coaches others on identifying and leveraging champions in complex scenarios.",
        "Competition": "Leads initiatives to gain strategic advantages over competitors, outlining plans in strategic sales meetings."
    },
    "Sales Sage": {
        "Metrics": "Sets organizational standards for metric-driven sales strategies.",
        "Economic Buyer": "Consults on key negotiations with economic buyers, providing expert guidance.",
        "Decision Criteria": "Provides thought leadership on adapting strategies to meet changing decision criteria.",
        "Decision Process": "Oversees the strategic direction of the sales process, ensuring it aligns with broader business goals.",
        "Identify Pain": "Recognized as an industry expert in identifying and solving customer pains.",
        "Champion": "Mentors senior sales staff on building and leveraging champion networks.",
        "Competition": "Guides the company in long-term competitive strategy, including entering new markets and product innovation."
    }
}

skills_list = [
    "Advanced Metrics Analysis",
    "Strategic Influence",
    "Complex Decision Criteria Integration",
    "Decision Process Management",
    "Insightful Questioning",
    "Champion Relationship Development",
    "Competitive Differentiation",
    "Market Research and Scoping",
    "Forecasting and Outcome Prediction",
    "Negotiation Skills",
    "Communication and Presentation Skills",
    "Upsell/Cross-sell Strategy Development",
    "Account Planning",
    "Relationship Management",
    "Problem-Solving Abilities"
]

Skill_level_description= {
    "Specialist": {
        "Metrics": "Analyzes and discusses advanced metrics to drive qualification discussions and forecast outcomes.",
        "Economic Buyer": "Engages economic buyers with strategies that influence their buying decisions.",
        "Decision Criteria": "Integrates complex decision criteria into qualification discussions.",
        "Decision Process": "Manages and steers the decision process to ensure proper qualification.",
        "Identify Pain": "Identifies underlying or unexpressed customer pains through insightful questioning.",
        "Champion": "Develops deep relationships with champions to leverage their influence effectively.",
        "Competition": "Conducts in-depth comparisons and positions products against competitors during qualification discussions."
    }
}

if st.session_state.panel:

    st.success("Key Successfully Entered")
   
    uploaded_files = st.file_uploader("Upload Audio Transcripts", type="txt", accept_multiple_files=True)

    button1 = st.button("Get Insights for transcripts")

    if button1:
        # file_names_list = get_files_in_directory(Audio_call)
        #transcription = transcribe_audio(file_path)

        # st.write(file_names_list)
        content = {}
        deal_levels = {}
        skills_metrics = {}
        with st.spinner('Loading Insights...'):
        
            for index, uploaded_file in enumerate(uploaded_files, start=1):
                try:
                    raw_data = uploaded_file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']

                    uploaded_file.seek(0)  # Reset file pointer to the beginning
                    content_name = uploaded_file.read().decode(encoding)

                    # Debugging print statements
                    print(f"Processing file {index}")

                    deal_level = AudioCall_Assessment_Deal_StageLevel(content_name, Sale_deal_stages_description, skill_levels_description)
                    # print(f"deal level for file {index}: {deal_level}")

                    if not deal_level:
                        st.warning(f"Failed to determine deal level for file {index}. Skipping.")
                        continue

                    deal_stage_level = deal_level['deal_stage_level']
                    single_stage_level_description = get_stage_level_description(deal_stage_level)

                    skill_level = deal_level['skill_level']
                    question_set = get_question_df_from_file(deal_stage_level, skill_level)
                    skill_metrics = AudioCall_Assessment_Skill_Level_Score(content_name, question_set, skills_list, Skill_level_description, single_stage_level_description)
                    
                    key = f'transcript_{index}'
                    deal_levels[key] = deal_level 
                    skills_metrics[key] = skill_metrics

                    for key in deal_levels.keys():
                        if key in skills_metrics:
                            deal_levels[key].update(skills_metrics[key])

                    content[key] = content_name
                except UnicodeDecodeError:
                    st.warning(f"Skipping non-text file: {uploaded_file.name}")


        averages = get_average_metrics(deal_levels)
        
        # Average = json.loads(averages)

        specific_json = generate_progress_data(deal_levels)

        final_averages = {"Transcript" : averages}

        spider = create_spider_chart(specific_json,"Transcript-wise Competency Performance")
        spider2 = create_spider_chart(final_averages,"Competency Performance Over Time")
        spider_grade = create_spider_chart(grade_wise_data_for_spider(deal_levels), "Grade-wise Competency Performance")
        bar_chart = create_advancement_chart(averages)
        st.write("Transcript Data : ",deal_levels)
        st.write("Average Metrics Score : ",averages)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(spider)
            st.plotly_chart(spider2)
        with col2:
            st.plotly_chart(bar_chart)
            st.plotly_chart(spider_grade)



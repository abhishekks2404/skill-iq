import os
import openai
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import chardet
import re
import json


from sales_iq_graph import generate_spider_chart, create_advancement_chart
# Load the .env file
load_dotenv()

# Get the API key from the .env file
openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key =openai_api_key

#def transcription_using_openai(file_path):
    #audio_file=open(file_path,"rb")
    #response = openai.Audio.transcribe("whisper-1",audio_file)
    #Text1 = (response["text"])
    #return Text1

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
            Transcript: {Transcript}\n
            Sale_deal_stages_description: {Sale_deal_stages_description}\n
            Skill_levels_description: {skill_levels_description}\n

            The given Transcript is transcription of Sales audio call. Sale_deal_stages_description is description of various stages of Sales deal. Skill_levels_description is description of various levels of skill.
            Please assess the transcript and identify Sales Deal Stage level based on the deal_stages_description , and identify Skills level based on the Skill_levels_description.
            Just provide me a only json with structure. No other text should be present in the output.

            As an output please provide me a only json with structure
            {json_file}
            '''

        # Making a request to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # or another model version, check OpenAI's API documentation for the latest models
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extracting the text from the response
        result = response.choices[0].message['content'].strip()
        # print(result)
        result = result.replace('```json', '').replace('```', '')
        json_data = json.loads(result)

        return json_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_question_df_from_file(stage_level,skill_level):
    stage_level = stage_level.strip()
    skill_level = skill_level.strip()
    
    print("inside the function : ",stage_level,skill_level)
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
            assess the  transcript based on the Scoring_instructions for each question in QuestionSet. Provide a score between 1 and 4 for each question output.
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
            ]
        )

        # Extracting the text from the response
        result = response.choices[0].message['content'].strip()
        result = result.replace('```json', '').replace('```', '')
        json_data = json.loads(result)

        # print(json_data)
        return json_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def recommended_skills(output4,skills_list1):
    try:
        
        prompt = (
            f"output4: {output4}\n"    
            f"skills_list : {skills_list1 }\n"
            ""
            "The given Transcript is transcription of Sales audio call "
            "Please Evaluate the  transcript to identify Demonstrated skills by sales agent from skills_list and to identify skills need to improve and identify new skills to learn from skills_list. while evaluation of transcript consider Provided Deal_stage_description, skill_level_description and  each question in QuestionSet  "
            "In output please give only  list of demonstrated skill in Transcript without explanation"
            "In output please give only list of recommended Skills which need to improve and new skills needed to learn to perform job well without explaination"
        )
        
        # Making a request to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or another model version, check OpenAI's API documentation for the latest models
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extracting the text from the response
        result = response.choices[0].message['content'].strip()

        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



Sale_deal_stages_description = {
    "Excall Scheduled": "Initial discovery call organized with a lead/MQL to scope out their pain-points/requirements and an opportunity is defined. Sometimes the deal can be qualified at this stage and moves directly to 10% and other times further scoping and qualification is required.",
    "Scoping": "Potential opportunity identified either through research on a high potential lead (New Biz) or through account planning and the identification of new up-sell/cross-sell/expansion opportunities (Partnerships). At this stage, the deal begins to be fully qualified before it can move to the next stage of the funnel.",
    "Opportunity Identified": "A tangible opportunity is identified in conversations with the prospect/customer and the lead is qualified as an SQL.",
    "Proposal Shared": "Opportunity is articulated in more detail in a written proposal shared with the client.",
    "Feedback from Client": "Response from the client on the proposal, and a basis from which to enter into contract negotiations is established.",
    "Negotiating": "Client and company work through details of the deal including pricing and scope.",
    "Contracting": "Contract sent to client for review.",
    "Closed (Won)": "Contract is signed by the client."
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


Deal_stage_description= {
     "Scoping": "Potential opportunity identified either through research on a high potential lead (New Biz) or through account planning and the identification of new up-sell/cross-sell/expansion opportunities (Partnerships). At this stage, the deal begins to be fully qualified before it can move to the next stage of the funnel."
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

skills_list1 = [
    "Data Analysis",
    "Qualification Strategy Refinement",
    "Targeting Optimization",
    "Impact Assessment of Economic Buyers",
    "Tailored Sales Approaches",
    "Stakeholder Decision Criteria Evaluation",
    "Sales Tactics Analysis",
    "Complex Problem-Solving",
    "Team Collaboration and Leadership",
    "Champion Engagement Strategy",
    "Competitive Landscape Evaluation",
    "Counter-Strategy Development",
    "Market Research",
    "Upsell/Cross-sell Identification",
    "Customer Relationship Management"
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


st.set_page_config(page_title="SalesIQ", layout='wide')
st.markdown("<h1 style='text-align: center; color: grey;'>Sales Audio Call Insights</h1>", unsafe_allow_html=True)

# names = get_folders_in_directory()

# Dropdown menu to select Audio Call

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

                deal_level = AudioCall_Assessment_Deal_StageLevel(content_name,Sale_deal_stages_description,skill_levels_description) 
                print("deal level : ",deal_level)
                if deal_level:
                    deal_stage_level = deal_level['deal_stage_level']
                    skill_level = deal_level['skill_level']
                    question_set = get_question_df_from_file(deal_stage_level,skill_level)
                    skill_metrics = AudioCall_Assessment_Skill_Level_Score(content_name,question_set,skills_list,Skill_level_description,Deal_stage_description)
                    # print("deal_stage_level :",deal_stage_level)
                    # print("skill_level :",skill_level)
                    print(skill_metrics)

                key = f'transcript_{index}'
                deal_levels[key] = deal_level 
                skills_metrics[key] = skill_metrics
                # transcript_Num = deal_levels[key]
                # transcript_Num.update(skill_metrics)
                for key in deal_levels.keys():
                    if key in skills_metrics:
                        deal_levels[key].update(skills_metrics[key])

                # print(deal_levels)
                content[key] = content_name
            except UnicodeDecodeError:
                st.warning(f"Skipping non-text file: {file_name}")

    fields_to_average = [
                        "Metrics",
                        "Economic Buyer",
                        "Decision Criteria",
                        "Decision Process",
                        "Identify Pain",
                        "Champion",
                        "Competition"
                        ]
    
    averages = {field: 0 for field in fields_to_average}
    transcript_count = len(deal_levels)

    # Sum up the values for each field across all transcripts
    for transcript in deal_levels.values():
        for field in fields_to_average:
            averages[field] += int(transcript[field])

    # Calculate the average for each field
    for field in averages:
        averages[field] /= transcript_count
    
    # Average = json.loads(averages)

    spider = generate_spider_chart(averages)
    bar_chart = create_advancement_chart(averages)

    
    st.write(deal_levels)
    st.write(averages)

    col1, col2 = st.columns(2)



    with col1:
        st.plotly_chart(spider)
    with col2:
        st.plotly_chart(bar_chart)
    
    # st.write(skills_metrics)
    # print(deal_levels)


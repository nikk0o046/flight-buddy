import os
import re
import time
import logging
logger = logging.getLogger(__name__)

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
# retrieve the OPENAI_API_KEY from environment variable
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def create_destination_params(user_request, selectedCityID, user_id):
    start_time = time.time() #start timer to log it later
    logger.debug("[UserID: %s] Creating destination parameters...", user_id)

    #initialize the openai model
    chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key = OPENAI_API_KEY, openai_organization='org-aaoYoL6D18BG1Z1btni0f4i6')

    #create the prompt templates
    system_template = """INSTRUCTIONS:
    You're an intelligent AI agent, and your job is to identify as many possible destination airports as you can based on information provided about the user preferences. You will first think about the task, and then provide an exhaustive list of IATA airport codes that match the criteria. Always present these codes in a list format like [XXX,YYY,ZZZ]. In most cases, aim for at least 15 to 20 destinations. Including more options will increase the likelihood of finding the best flights for the user."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
    #example 1
    userExample1 = """Origin: Stockholm
    Info: Origin: Stockholm, SE | Destination: southern Europe, by the Mediterranean | Departure: Flexible | Duration: 3 nights | Flights: direct"""
    userExample_prompt1 = HumanMessagePromptTemplate.from_template(userExample1)

    botExample1 = """Thought: The user wants to travel to southern Europe, specifically a location by the Mediterranean Sea. This includes countries like Spain, France, Italy, Malta, Slovenia, Croatia, Bosnia and Herzegovina, Montenegro, Albania, Greece, and Cyprus. I have included as many relevant airports as possible that have direct flights from Stockholm and are located near the Mediterranean Sea.
    Destinations (IATA codes): [BCN,VLC,MRS,NCE,FCO,NAP,ATH,SKG,SPU,DBV,PMO,BOD,TLS,AHO,CAG,CTA,LCA,PFO,TIA,OLB,MLA,GRO]"""
    botExample_prompt1 = AIMessagePromptTemplate.from_template(botExample1)

    #example 2
    userExample2 = """Origin: Barcelona
    Info: Origin: Barcelona, ES | Destination: eastern Europe, smaller city | Departure: Weekend | Duration: 2-3 days | Flights: Any"""
    userExample_prompt2 = HumanMessagePromptTemplate.from_template(userExample2)

    botExample2 = """Thought: The user is interested in traveling to a less populated city in eastern Europe, excluding larger cities like Budapest or Bucharest. Thus, I've included an extensive list of smaller airports in Eastern Europe.
    Destinations (IATA codes): [LWO,KIV,CLJ,GDN,BRQ,TSR,VAR,TAY,RJK,KSC,ODE,POZ,IEV,LVIV,SZZ,SOJ,VNO,KRK,SKP,TGD,SJJ,PRN,BEG]"""
    botExample_prompt2 = AIMessagePromptTemplate.from_template(botExample2)

    #example 3
    userExample3 = """Origin: Munich
    Info: Origin: Munich, DE | Destination: Any | Activity: Nightlife | Departure: May | Duration: 4-5 nights | Flights: Any"""
    userExample_prompt3 = HumanMessagePromptTemplate.from_template(userExample3)

    botExample3 = """Thought: The user is looking for a city renowned for its nightlife. Cities known for their nightclubs and party scenes are numerous. So, I've included a wide range of potential locations.
    Destinations (IATA codes): [IBZ,BCN,AMS,PRG,BUD,LIS,DUB,SPU,KRK,CDG,BER,LON,CPH,ROM,MAD,RIX,TLL,HEL,OSL,SOF,ZAG,BEG]"""
    botExample_prompt3 = AIMessagePromptTemplate.from_template(botExample3)

    #example 4
    userExample4 = """Origin: Paris
    Info: Origin: Paris, FR | Destination: Amsterdam | Departure: Summer | Duration: 1 week | Flights: Any"""
    userExample_prompt4 = HumanMessagePromptTemplate.from_template(userExample4)

    botExample4 = """Thought: The user has a specific destination in mind: Amsterdam. Therefore, the only relevant destination airport code is that of Amsterdam.
    Destinations (IATA codes): [AMS]"""
    botExample_prompt4 = AIMessagePromptTemplate.from_template(botExample4)

    #example 5
    userExample5 = """Origin: Sydney
    Info: Origin: Sydney, AU | Destination: Any | Departure: Flexible | Duration: Flexible | Flights: Any"""
    userExample_prompt5 = HumanMessagePromptTemplate.from_template(userExample5)

    botExample5 = """Thought: The user is looking to travel, but hasn't specified a particular destination. Therefore, I've considered popular and accessible destinations from Sydney. The list includes a diverse range of domestic and international locations to offer the user an extensive array of choices.
    Possible destinations (IATA codes): [MEL,BNE,ADL,PER,CBR,OOL,AKL,CHC,WLG,ZQN,NAN,DPS,SIN,KUL,BKK,HKT,HKG,TPE,NRT,HND,ICN,PEK,PVG,SFO,LAX,YVR,HNL,JFK,LHR,DXB,DOH]"""
    botExample_prompt5 = AIMessagePromptTemplate.from_template(botExample5)

    human_template = """Origin: {selectedCityID}
    Info: {user_request}"""
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt,
        userExample_prompt1,
        botExample_prompt1,
        userExample_prompt2,
        botExample_prompt2,
        userExample_prompt3,
        botExample_prompt3,
        userExample_prompt4,
        botExample_prompt4,
        userExample_prompt5,
        botExample_prompt5,
        human_message_prompt,]
    )


    #request the response from the model
    openai_response = chat(
        chat_prompt.format_prompt(
            selectedCityID=selectedCityID,
            user_request=user_request
        ).to_messages()
    )

    logger.debug("[UserID: %s] Destination parameters response: %s", user_id, openai_response.content)
    #print(openai_response.content) # FOR LOCAL TESTING 

    # Regular expression pattern to match the IATA codes
    pattern = r'\[([A-Za-z,\s]+)\]'

    # Find the matches in the response content
    matches = re.search(pattern, openai_response.content)

    # If a match was found
    if matches:
        # Get the matched string, remove spaces, and split it into a list on the commas
        destination_list = matches.group(1).replace(" ", "").split(',')

        # Create a destination dictionary from the response
        destination_params = {
            'fly_to' : ','.join(destination_list),
        }

    else:
        destination_params = {}

    logger.debug("[UserID: %s] Destination parameters created: %s", user_id, destination_params)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.debug("[UserID: %s] Function execution time: %s seconds", user_id, elapsed_time)

    return destination_params


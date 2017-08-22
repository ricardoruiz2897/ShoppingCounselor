##
#Ricardo Ruiz
#Last Change made:
#6/5/2017
##

from __future__ import print_function

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Shopping Counselor',
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the best shopping counselor. You will be prompted with some questions to determine if you should buy an article or not. Start by saying Start questionnaire."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Start the questionnaire by saying start"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using my shopping counselor. Goodbye "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

#this function handles user input errorsa
def handle_user_errors(intent, session):

    card_title = 'handle wrong response'
    session_attributes = {}
    speech_output = 'I did not understand, please answer yes or no'
    reprompt_text = 'I did not understand, please answer yes or no'
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, 
                                                                       reprompt_text, should_end_session))
                                                 
#this Functions handles the questionaire
def create_var_attributes(question, decision):
    return {"question":question, "decision":decision}

def questionnaire(n_question, intent, session):

    questions = [ 'Do you already have something similar to this?',
                  'Is this an impulsive buy?',
                  'Will it go on sale sometime or will it be cheaper later?',
                  'Will you have to cut something important for this?',
                ]

    #first question, it entered as 'start'
    if n_question == 0:

            #init
            global_question = 1
            global_decision = 40

            session_attributes = create_var_attributes(global_question, global_decision)

            should_end_session = False
            speech_output = questions[0]
            reprompt_text = questions[0]

            return build_response(session_attributes, build_speechlet_response(intent['name'],
                                              speech_output,reprompt_text,should_end_session)) 
    #called as something else
    else:

        global_question = session['attributes']['question']
        global_decision = session['attributes']['decision']

        #check if it is the last question
        if global_question == 4:

            if global_decision <= 40:
                #you should not buy the article
                speech_output = "You should not buy the article according to that logic"
                should_end_session = True
                reprompt_text = None
                session_attributes = {}

    
            else:
                #you should buy the article 
                speech_output = "Go for it, buy the article"
                should_end_session = True
                reprompt_text = None
                session_attributes = {}
    
            return build_response(session_attributes, build_speechlet_response(intent['name'],
                                            speech_output,reprompt_text,should_end_session))  

        #Check answer in slots
        if intent['slots']['Ans']['value'] == 'yes':
            #set for next question
            session_attributes = create_var_attributes(global_question+1, global_decision-10)
            print('yesss')

        elif intent['slots']['Ans']['value'] == 'no':
            #set for next question
            session_attributes = create_var_attributes(global_question+1, global_decision+10)
            print('noo')

        #prompt next question
        should_end_session = False
        speech_output = questions[global_question]
        reprompt_text = questions[global_question]

        return build_response(session_attributes, build_speechlet_response(intent['name'],
                                            speech_output,reprompt_text,should_end_session))  

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "NewQuestionnaire":
        return questionnaire(0, intent, session)
    elif intent_name == "ContinueQuestionnaire":
        return questionnaire(1,intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


#####
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Main handler ------------------
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


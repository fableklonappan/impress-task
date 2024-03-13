
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []
    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session['ended']=False

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if answer not in ["1","2","3","4"] and current_question_id is not None:
        return False, "Select correct option"
    if current_question_id is not None and not session.get('ended'):
        responses = session.get("responses")
        if(responses):
            responses[int(current_question_id)] = answer
            session["responses"] = responses
        else:
            temp = {}
            temp[int(current_question_id)] = answer
            session["responses"] = temp
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        current_question_id=-1
    try:
        question_text = PYTHON_QUESTION_LIST[current_question_id + 1]["question_text"]
        options="<br>".join(map(lambda x: f"{x[0]+1}. {x[1]}",enumerate(PYTHON_QUESTION_LIST[current_question_id + 1]["options"])))
    except:
        return None,current_question_id
    return question_text +'<br>'*2+options ,current_question_id + 1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    if session.get('ended'):
        return "Quiz ended. Reset to try again."
    responses = session["responses"]
    print(responses)
    total_score = 0
    for question_number, user_response in responses.items():
        question = PYTHON_QUESTION_LIST[int(question_number)]
        correct_option_index = int(user_response) - 1
        correct_option = question['options'][correct_option_index]        
        if correct_option == question['answer']:
            total_score += 1
            print(total_score)
    session['ended']=True
    session['responses']={}
    return f"Your total score is {total_score}. Quiz over."
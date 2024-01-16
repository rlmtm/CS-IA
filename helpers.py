import os
import secrets
import string
import re
import json

from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
from os import path
from iso639 import Lang

from cs50 import SQL
from functools import wraps
from flask import redirect, session, request, current_app

import os.path
from sqlite3 import Error


def login_required(f):
    """Decorate routes to require login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:

            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


def before_first_request(f):
    """Decorate routes to execute before first request"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_app.config.get("BEFORE_FIRST_REQUEST"):

            return f(*args, **kwargs)

            current_app.config["BEFORE_FIRST_REQUEST"] = True

    return decorated_function


def run_sql(sql_file):
    """Runs SQL Commands from SQL File"""

    db = SQL("sqlite:///static/sql/database.db")

    try:
        with open('./static/sql/'+sql_file, 'r') as file:
            sql_commands = file.read().split(';')
        for command in sql_commands:
            if command.strip():
                db.execute(command)
    except Error as e:
        print(e)


def check_for_sql(app):
    """Runs SQL files if they have not been run before"""

    db = SQL("sqlite:///static/sql/database.db")

    if not app.config.get("BEFORE_CHECK_EXECUTED"):

        run_sql('schema.sql')

        return

        app.config["BEFORE_CHECK_EXECUTED"] = True


def clear_session(app):
    """Clears Session and redirects to login page"""

    if not app.config.get("BEFORE_REQUEST_EXECUTED"):

        if request.endpoint != 'static' and request.endpoint != 'login':

            session.clear()

            return redirect("/login")

        app.config["BEFORE_REQUEST_EXECUTED"] = True


def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def valid_email(email):
    emailRegex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(emailRegex, email) is not None


def create_folder(convo_id):

    path = './audio_recordings'

    folder_name = 'conversation_'+str(convo_id)

    new_folder_path = os.path.join(path, folder_name)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        print(f"Folder '{new_folder_path}' created successfully.")
    else:
        print(f"Folder '{new_folder_path}' already exists.")

def count_files_with_word(convo_id, word):

    path = './audio_recordings'

    folder_name = 'conversation_'+str(convo_id)

    folder_path = os.path.join(path, folder_name)

    try:

        files = os.listdir(folder_path)

        count = sum(1 for file in files if word in file)

        return count
    except Exception as e:
        print(f"Error counting files: {e}")
        return None

def play_audio(file):

    format = file.split(".")[1]

    if format == "mp3":
        sound = AudioSegment.from_mp3(file)
    elif format == "wav":
        sound = AudioSegment.from_wav(file)

    play(sound)

def openai_cred():

    with open('./static/cred.json', 'r') as file:
        data = json.load(file)['apiKey']

    client = OpenAI(api_key=data)

    return client

def chatGPT_answer(conversation, file_num_sys, convo_id):

    folder_path = 'audio_recordings/conversation_'+str(convo_id)

    file_name = "sys_"+str(file_num_sys)+".mp3"

    file_path = os.path.join(folder_path, file_name)

    client = openai_cred()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    response_speech = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response.choices[0].message.content,
    )

    response_speech.stream_to_file(file_path)

    play_audio(file_path)

    return response.choices[0].message.content

def speech_to_text(path, language):

    client = openai_cred()

    audio_file = open(path, "rb")

    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        language=Lang(language).pt1,
        response_format="text"
    )

    return transcript

def format_duration(seconds):

    minutes, seconds = divmod(seconds, 60)

    return f"{int(minutes):02d}:{int(seconds):02d}"

def audio_duration(folder_path):

    try:
        audio = AudioSegment.from_file(folder_path)
        duration_in_seconds = len(audio) / 1000  # Convert milliseconds to seconds
        return duration_in_seconds
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return None

def total_audio_duration(convo_id):
    
    durations = {}

    directory_path = 'audio_recordings/conversation_'+str(convo_id)

    try:

        files = os.listdir(directory_path)

        audio_files = [file for file in files if file.lower().endswith(('.mp3', '.wav'))]

        total_duration = 0

        for audio_file in audio_files:
            file_path = os.path.join(directory_path, audio_file)
            duration = audio_duration(file_path)
            if duration is not None:
                durations[audio_file] = duration
                total_duration += duration

        return format_duration(round(total_duration))
    except Exception as e:
        print(f"Error getting audio durations in {directory_path}: {e}")
        return None

def merge_audio_files(convo_id):

    directory_path = "./audio_recordings/conversation_"+str(convo_id)+"/"
    output_path = directory_path+"recording.mp3"

    try:

        audio_files = [file for file in os.listdir(directory_path) if file.lower().endswith('.mp3')]

        sorted_files = sorted(audio_files, key=lambda x: (int(x.split('_')[1].split('.')[0]), x))

        combined_audio = AudioSegment.silent()

        for audio_file in sorted_files:
            file_path = os.path.join(directory_path, audio_file)
            segment = AudioSegment.from_mp3(file_path)
            combined_audio += segment


        combined_audio.export(output_path, format="mp3")

        print(f"Audio files merged and saved to {output_path}")
    except Exception as e:
        print(f"Error merging audio files: {e}")

def clear_recordings(convo_id):

    directory_path = "./audio_recordings/conversation_"+str(convo_id)+"/"
    file_name = "recording.mp3"

    try:

        files_to_delete = [file for file in os.listdir(directory_path) if file != file_name]


        for file in files_to_delete:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"Not a file: {file_path}")

        print(f"Kept: {file_name}")
    except Exception as e:
        print(f"Error deleting files: {e}")

def create_transcript(conversation, convo_id):

    directory_path = "./audio_recordings/conversation_"+str(convo_id)+"/"
    file_name = "transcript.txt"
    output_file_path = directory_path+file_name

    with open(output_file_path, 'w', encoding='utf-8') as script_file:
        for segment in conversation[2:]:
            role = segment.get('role', '')
            content = segment.get('content', '')
            
            if role and content:
                if role == "system":
                    script_file.write(f'{role.capitalize()}: {content}\n\n')
                else:
                    script_file.write(f'{role.capitalize()}: {content}\n')

def remove_folder(directory_path):

    if os.path.exists(directory_path):

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    remove_folder(file_path)
            except Exception as e:
                print(f"Failed to remove {file_path}: {e}")

        try:
            os.rmdir(directory_path)
            print(f"Directory {directory_path} removed successfully.")
        except Exception as e:
            print(f"Failed to remove directory {directory_path}: {e}")
    else:
        print(f"Directory {directory_path} does not exist.")

def create_deleted_file(convo_id):
    directory_path = 'audio_recordings/conversation_'+str(convo_id)
    file_path = os.path.join(directory_path, "deleted.txt")

    content = "Transcript has been deleted by the user."

    try:
        with open(file_path, "w") as file:
            file.write(content)

        print(f"File '{file_path}' created successfully.")
    except Exception as e:
        print(f"Failed to create file '{file_path}': {e}")

def transcript_feedback(transcript, convo_id):

    client = openai_cred()

    seperator = "-----------------------------------------------------------------------------------------"

    directory_path = "./audio_recordings/conversation_"+str(convo_id)+"/"
    file_name = "transcript.txt"
    output_file_path = directory_path+file_name

    conversation = [
        {"role": "system", "content": "You are a professional language teacher, who gives clear and concise feedback on writing."},
        {"role": "user", "content": "You will give suggestions and improvements for the following sentences by the user in the specified language. Analyze grammar, word choice, sentence construction, relevance and flow. Only analyse the content with role user but look for context at the text from role system. Only reply with feedback, DO NOT include the transcript in the response. Give specific and general feedback on the user's sentences only." + str(transcript)}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    try:
        with open(output_file_path, 'a') as file:
            file.write(seperator+"\n\nFeedback:\n\n"+response.choices[0].message.content)        
        print("Transcript updated with feedback!")
    except Exception as e:
        print("Failed to give feedback. "+str(e))
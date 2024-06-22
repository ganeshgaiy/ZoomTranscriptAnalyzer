from flask import Flask, render_template, request
from openai import OpenAI
client = OpenAI()

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'transcript' not in request.files:
        return "No file part"
    file = request.files['transcript']
    if file.filename == '':
        return "No selected file"
    if file:
        content = file.read().decode('utf-8')
        proofread_content = proofread_transcript(content)
        return render_template('index.html', proofread=proofread_content)

def proofread_transcript(transcript):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are now an expert proofreader."},
            {"role": "user", "content": f"""I have an audio transcript of non-native English speaker. These transcripts may contain mispronounced words, unclear sentences, and grammatical errors due to language barriers. 
             My goal is to correct these errors and improve the overall clarity and coherence of the transcripts. 
             I would like your assistance in proofreading and editing these transcripts to make them sound natural, 
             grammatically correct, and easy to understand.For each transcript, please:\n 1.Identify and correct any grammatical errors.
            \n2.Correct any mispronounced words.
            \n3.Clarify any sentences that are unclear or awkwardly phrased.
            \n4.Ensure the overall readability and coherence of the text.
            \n5.Maintain the original meaning and context as much as possible.:\n\n{transcript}"""}
        ],
        max_tokens=2048
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)

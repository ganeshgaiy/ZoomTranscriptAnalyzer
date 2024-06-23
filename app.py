from flask import Flask, flash, redirect, render_template, request
from openai import OpenAI
import difflib

client = OpenAI()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'transcript' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['transcript']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        try:
            content = file.read().decode('utf-8')
            proofread_content = proofread_transcript(content)
            diff_proofread_content = generate_inline_diff(content, proofread_content)
            return render_template('index.html', proofread=diff_proofread_content, original=content)
        except Exception as e:
            flash(f'An error occurred while processing the file: {e}')
            return redirect(request.url)


def generate_inline_diff(original, proofread):
    # Split the text into words
    original_words = original.split()
    proofread_words = proofread.split()
    
    # Use SequenceMatcher to compare the word sequences
    matcher = difflib.SequenceMatcher(None, original_words, proofread_words)
    diff_html = ""
    
    for opcode in matcher.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        if tag == 'equal':
            diff_html += ' ' + ' '.join(original_words[i1:i2])
        elif tag == 'replace':
            diff_html += ' ' + ''.join(f"<span class='diff-removed'>{word}</span>" for word in original_words[i1:i2])
            diff_html += ' ' + ''.join(f"<span class='diff-added'>{word}</span>" for word in proofread_words[j1:j2])
        elif tag == 'delete':
            diff_html += ' ' + ''.join(f"<span class='diff-removed'>{word}</span>" for word in original_words[i1:i2])
        elif tag == 'insert':
            diff_html += ' ' + ''.join(f"<span class='diff-added'>{word}</span>" for word in proofread_words[j1:j2])
    
    return diff_html
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

def generate_diff(original, proofread):
    diff = difflib.ndiff(original.splitlines(), proofread.splitlines())
    diff_html = ""
    for line in diff:
        if line.startswith("+ "):
            diff_html += f"<span class='diff-added'>{line[2:]}</span> "
        elif line.startswith("- "):
            # Removed lines will not be shown in the proofread text
            continue
        else:
            diff_html += f"{line[2:]} "
    return diff_html


if __name__ == '__main__':
    app.run(debug=True)

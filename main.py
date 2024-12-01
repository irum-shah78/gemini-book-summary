# import google.generativeai as genai
# import os

# os.environ['GOOGLE_API_KEY'] = "AIzaSyAjwhkFXi0I29jsdGMrsAUkgVcjxZznhOA"
# genai.configure(api_key = os.environ['GOOGLE_API_KEY'])
# model = genai.GenerativeModel('gemini-pro')

# def Query_Gemini(query):
#     response = model.generate_content(query)
#     return response.text

# while True:
#     user = input("User: ")
#     res = Query_Gemini(user)
#     print("Bot",res)


# SIMPLE CODE
# import google.generativeai as genai
# import os
# import json
# import time

# os.environ['GOOGLE_API_KEY'] = "AIzaSyBkq0TLG6cNjX-bi3Akr48RPMt-fQgR4uI"
# genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
# model = genai.GenerativeModel('gemini-pro')

# def query_gemini(query):
#     try:
#         response = model.generate_content(query)
#         return response.text
#     except Exception as e:
#         if "429" in str(e):
#             print("Quota exhausted. Retrying in 60 seconds...")
#             time.sleep(60)
#             return query_gemini(query)
#         else:
#             return f"Error querying Gemini: {e}"

# def summarize_text(input_text):
#     try:
#         prompt = f"""
# Summarize the following text into a structured JSON format using the specified structure below. Ensure that the summary is concise, accurate, and follows the outlined format strictly. Replace placeholders with appropriate values based on the text content.

# Expected JSON structure:
# [
#     {{
#         "type": "INTRODUCTION",
#         "name": "[Title of the introduction]",
#         "content": "[A concise summary of the introduction or opening content of the text]"
#     }},
#     {{
#         "type": "CHAPTER 1",
#         "name": "[Title of Chapter 1]",
#         "content": "[A concise summary of Chapter 1]"
#     }},
#     {{
#         "type": "CHAPTER 2",
#         "name": "[Title of Chapter 2]",
#         "content": "[A concise summary of Chapter 2]"
#     }},
#     {{
#         "type": "CHAPTER 3",
#         "name": "[Title of Chapter 3]",
#         "content": "[A concise summary of Chapter 3]"
#     }},
#     {{
#         "type": "CHAPTER 4",
#         "name": "[Title of Chapter 4]",
#         "content": "[A concise summary of Chapter 4]"
#     }}
#     // Continue the pattern for any additional sections or chapters
# ]

# Text to summarize:
# {input_text}
# """
#         print("Sending text to Gemini for summarization...")
        
#         summary = query_gemini(prompt)
#         print("Summary received.")

#         try:
#             parsed_summary = json.loads(summary)
#         except json.JSONDecodeError:
#             print("Failed to parse the summary as JSON. Saving raw output.")
#             parsed_summary = {"Summary": summary.strip()}

#         output_file = "summarized_output.json"
#         with open(output_file, 'w', encoding='utf-8') as file:
#             json.dump(parsed_summary, file, indent=4, ensure_ascii=False)

#         print(f"Summary saved to {output_file}.")
#         return parsed_summary

#     except Exception as e:
#         return {"Error": str(e)}

# while True:
#     print("\nOptions:")
#     print("1. Summarize text input")
#     print("2. Summarize text file")
#     print("3. Exit")
#     choice = input("Choose an option (1/2/3): ").strip()

#     if choice == '1':
#         user_text = input("Enter the text you want to summarize: ").strip()
#         summary = summarize_text(user_text)
#         print("\n### Summary ###")
#         print(json.dumps(summary, indent=4, ensure_ascii=False))

#     elif choice == '2':
#         file_path = input("Enter the path to the text file: ").strip()
#         try:
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 text_content = file.read()
#             summary = summarize_text(text_content)
#             print("\n### Summary ###")
#             print(json.dumps(summary, indent=4, ensure_ascii=False))
#         except UnicodeDecodeError as e:
#             print(f"Encoding error: {e}. Try opening the file with a different encoding.")
#         except Exception as e:
#             print(f"Error reading file: {e}")

#     elif choice == '3':
#         print("Goodbye!")
#         break

#     else:
#         print("Invalid choice. Please try again.")


import google.generativeai as genai
import os
import json
import time

os.environ['GOOGLE_API_KEY'] = "AIzaSyBkq0TLG6cNjX-bi3Akr48RPMt-fQgR4uI"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-pro')

def split_text_into_chunks(text, chunk_size=500, overlap=50):
    """Splits the input text into chunks with optional overlap."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        print(f"Generated chunk: {chunk}")
        chunks.append(chunk)
    return chunks

def query_gemini_with_backoff(query, retries=5):
    """Queries Gemini with exponential backoff for rate-limiting errors."""
    for attempt in range(retries):
        try:
            response = model.generate_content(query)
            print(f"Response from Gemini (Attempt {attempt+1}): {response.text}")
            return response.text
        except Exception as e:
            if "429" in str(e): 
                wait_time = 60 * (2 ** attempt) 
                print(f"Quota exhausted. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Error querying Gemini: {e}")
    raise Exception("Maximum retries reached. Unable to complete the query.")



def summarize_chunk(chunk, chunk_index, chat_memory=None, is_chunked=False):
    """Generates a summary for a single chunk, optionally including chat memory."""
    prompt = f"""
Summarize the following text into a structured JSON format. Each summary must have:
- A `type` field (e.g., INTRODUCTION, CHAPTER 1, etc.).
- A `name` field describing the section title.
- A `content` field with at least five detailed lines summarizing the section in plain text.

Text to summarize:
{chunk}

Provide the output strictly in JSON format as shown below:
[
    {{
        "type": "INTRODUCTION",
        "name": "Title of the Introduction",
        "content": "A concise summary of the introduction in plain text, at least 5 lines."
    }},
    {{
        "type": "CHAPTER 1",
        "name": "Title of Chapter 1",
        "content": "A concise summary of Chapter 1 in plain text, at least 5 lines."
    }}
]


"""

    if is_chunked and chat_memory:
        prompt = f"""
You are summarizing a lengthy document that has been divided into chunks. Use the provided context from previous chunks to guide your summary. Summarize the following text into a structured JSON format.

Context from previous chunks:
{chat_memory}

Current text to summarize:
{chunk}

Output format:
[
    {{
        "type": "INTRODUCTION",
        "name": "Title of the Introduction",
        "content": "A concise summary of the introduction in plain text, at least 5 lines."
    }},
    {{
        "type": "CHAPTER 1",
        "name": "Title of Chapter 1",
        "content": "A concise summary of Chapter 1 in plain text, at least 5 lines."
    }}
]

Provide the output strictly in this JSON format without any additional text or explanations.

"""

    print(f"Summarizing chunk {chunk_index}...")
    response = query_gemini_with_backoff(prompt)
    return response


def summarize_text(input_text, chunk_size=20000, overlap=100):
    """Summarizes lengthy text by dividing it into chunks and maintaining context."""
    is_chunked = len(input_text.split()) > chunk_size
    chunks = split_text_into_chunks(input_text, chunk_size, overlap) if is_chunked else [input_text]
    print(f"Input text split into {len(chunks)} chunks." if is_chunked else "Input is small, summarizing directly.")

    all_summaries = []
    chat_memory = "" 

    for idx, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {idx}...")
        try:
            summary = summarize_chunk(chunk, idx, chat_memory, is_chunked)
            try:
                parsed_summary = json.loads(summary)
                all_summaries.extend(parsed_summary)
                chat_memory += f"Chunk {idx} Summary: {json.dumps(parsed_summary, ensure_ascii=False)}\n"
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON for chunk {idx}: {e}")
                all_summaries.append({"chunk_index": idx, "error": "Failed to parse summary.", "raw_text": summary})
        except Exception as e:
            print(f"Error summarizing chunk {idx}: {e}")
            all_summaries.append({"chunk_index": idx, "error": str(e)})

    output_file = "summarized_output.json"
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(all_summaries, file, indent=4, ensure_ascii=False)

    print(f"Summary saved to {output_file}.")
    return all_summaries



# Main loop
while True:
    print("\nOptions:")
    print("1. Summarize text input")
    print("2. Summarize text file")
    print("3. Exit")
    choice = input("Choose an option (1/2/3): ").strip()

    if choice == '1':
        user_text = input("Enter the text you want to summarize: ").strip()
        summary = summarize_text(user_text)
        print("\n### Summary ###")
        print(json.dumps(summary, indent=4, ensure_ascii=False))

    elif choice == '2':
        file_path = input("Enter the path to the text file: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
            summary = summarize_text(text_content)
            print("\n### Summary ###")
            print(json.dumps(summary, indent=4, ensure_ascii=False))
        except UnicodeDecodeError as e:
            print(f"Encoding error: {e}. Try opening the file with a different encoding.")
        except Exception as e:
            print(f"Error reading file: {e}")

    elif choice == '3':
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")


def clean_summary_text(summary):
    """Clean summary text by removing unwanted newline characters."""
    return summary.replace("\n", " ").strip()

summary = clean_summary_text(summary)

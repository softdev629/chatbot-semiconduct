import streamlit as st
import openai
from funcs import chatgpt, docqa, googlegpt
import pandas as pd

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI Bot that determines given query requires graph visualization answer. For example, if query asks you to compare companies financial data, it requires graph visualization. Only return 'yes' or 'no' depends on it requires graph.",
            },
            {"role": "user", "content": f"This is query: {prompt}."},
        ],
    )

    message = response["choices"][0]["message"]
    print(message)

    if message.content == "No":
        ans_chatgpt = chatgpt(prompt)
        ans_docqa = docqa(prompt)
        ans_google = googlegpt(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": "You are You are a McKinsey partner who is known for his cutting edge insights. The stakes are high & you are consulting a client who is going to give you a 100 million contract if you are insightful enough. You always give a so-what to the client when providing facts. You never give random answers that have no meaning and you are always focused on nuanced insights combining multiple legitimate sources of information. DON'T mention you are combining several source of information in the answer.",
                    },
                    {
                        "role": "user",
                        "content": f"Question is {prompt}.\nYou have two answers to pick from as sources of insights .\nFirst optional answer is {ans_chatgpt}. \nSecond optional answer is {ans_docqa}.\nThird optional answer is {ans_google}\n\nPlease combine & synthesize all the answers in a way that the context from all the answers is maintained and return the combined insights as the final answer.",
                    },
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.write(full_response + "▌")
            message_placeholder.write(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
    else:
        df = pd.read_excel("./xlsxs/Merged data.xlsx")
        df = df.astype(str)
        xlsx_string = df.to_csv(index=False, sep="\t")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a McKinsey consultant analyzing financial information.",
                    },
                    {
                        "role": "user",
                        "content": f"Following is semiconductor companies financial tabular information.\n\n {xlsx_string} \n\n {prompt}",
                    },
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.write(full_response + "▌")
            message_placeholder.write(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            anaylze = full_response

            print(anaylze)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are a McKinsey consultant analyzing financial information.",
                },
                {
                    "role": "user",
                    "content": f"Following is analyzed financial information.\n\n {anaylze} \n\n Give me python code that visualize above information by using matplotlib library with awesome and beautiful styles, colors and . Only return code.",
                },
            ],
        )

        code = completion["choices"][0]["message"].content

        code = code.replace("python", "")
        code = code.replace("plt.show()", "st.pyplot(plt)")
        if "```" in code:
            extract = code.split("```")[1]
        else:
            extract = code

        print(extract)

        exec(extract)

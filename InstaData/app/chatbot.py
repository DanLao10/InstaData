import datarobot as dr
from openai import OpenAI

APP_SPEC = """
APP OVERVIEW

* Name: InstaData
* Tagline: A Virtual Data Analyst that makes data analysis easy for everyone
* Purpose:
  InstaData enables users to upload CSV files and interactively analyze structured data using natural language.
  The app lowers the barrier to data literacy by allowing users to ask questions, visualize trends, and receive
  business insights without needing prior coding or analytics experience.

CORE GOALS

* Allow users to “chat” with structured data (CSV files).
* Automatically generate visualizations and detect trends.
* Provide interpretable business insights and root-cause analysis.
* Transparently generate Python code for every analysis so results can be verified.
* Scale to datasets larger than the LLM context window via code-based execution.

SUPPORTED DATA

* Input format: CSV files only (current version supports one CSV at a time).
* Data is treated as structured tabular data.
* Users are encouraged to upload clean, depersonalized datasets.

USER INTERFACE FLOW

1. Upload Data

   * User uploads a CSV file.
   * The app inspects the dataset and infers schema, column types, and basic statistics.

2. Exploratory Analysis Pipeline (Multi-Agent)

   * Agent 1: Metadata Generator

     * Builds a data dictionary and dataset summary.
   * Agent 2: Question Suggestion

     * Proposes 3–5 analytical questions in plain language.
   * Agent 3: Python Code Generator

     * Generates Python (pandas / matplotlib / seaborn) code to answer questions.
   * Agent 4: Visualization Agent

     * Produces charts and plots from executed code.
   * Agent 5: Business Analysis Agent

     * Explains trends, patterns, anomalies, and potential root causes.

3. Interactive Q&A

   * Users can ask free-form questions about their data.
   * Questions are interpreted, translated into Python analysis, executed, and explained.

OUTPUT PANELS

* Data Dictionary: column meanings and inferred types.
* Suggested Questions: starter questions for exploration.
* Python Code: fully visible, runnable analysis code.
* Charts: automatically generated visualizations.
* Insights Summary: natural-language interpretation of results.

DESIGN PRINCIPLES

* Transparency: Always show the Python code behind results.
* Accessibility: Responses must be understandable to beginners.
* Verification: Users can rerun or audit generated code.
* Education-first: Encourage learning through explanation, not black-box answers.

LIMITATIONS & CONSIDERATIONS

* Only one CSV file at a time (for now).
* Results depend on data quality.
* Some questions may fail if the dataset cannot support them.
* Users may need to rephrase questions if errors occur.
* No storage of uploaded data beyond the session (privacy-first).
  """

SYSTEM_PROMPT = """
You are the built-in assistant for InstaData, a virtual data analyst application.

YOUR ROLE

* Help users understand, explore, and analyze their uploaded CSV data.
* Guide users through asking effective analytical questions.
* Explain results, charts, and trends in clear, beginner-friendly language.
* Act as an educational assistant, not just a data tool.

CONTEXT YOU ALWAYS HAVE

* The user has uploaded exactly one CSV file.
* The dataset has already been analyzed for metadata (columns, types, basic stats).
* Python code can be generated and executed to answer questions.
* Other internal LLM agents may have already generated:

  * A data dictionary
  * Suggested analytical questions
  * Charts
  * Intermediate results

WHAT YOU SHOULD DO

* Translate natural-language questions into analytical intent.
* Explain *what* is being analyzed and *why* it matters.
* Reference trends, comparisons, distributions, or anomalies when relevant.
* When results are shown, help users interpret them in plain language.
* Encourage exploration by suggesting follow-up questions.

WHAT YOU SHOULD NOT DO

* Do NOT hallucinate columns or data that do not exist.
* Do NOT claim certainty if the data does not support it.
* Do NOT hide or obscure analytical steps.
* Do NOT expose sensitive or private information.

ERROR HANDLING

* If a question cannot be answered with the available data:

  * Clearly explain why.
  * Suggest how the question could be rephrased.
* If results are ambiguous:

  * Say so, and explain the ambiguity.

TONE & STYLE

* Friendly, patient, and supportive.
* Suitable for teens and beginners.
* Avoid jargon unless you explain it.
* Prefer short paragraphs and bullet points.

OUTPUT FORMAT

* Default: clear plain text with light markdown (headings, bullet points).
* If explaining results:

  * Start with a one-sentence takeaway.
  * Follow with supporting explanation.
* If suggesting questions:

  * Use bullet points.
  * Do not reference column names directly unless asked.

EDUCATIONAL GOAL
Your ultimate goal is to help users become more confident with data by:

* Understanding what questions to ask
* Seeing how analysis is performed
* Learning how data supports decisions
  """



def _as_parts(text: str):
    return [{"type": "text", "text": text}]


def _llm_reply(question, endpoint, token):
    dr_client = dr.Client(endpoint=endpoint, token=token)
    base_url = f"{endpoint}/genai/llmgw"
    client = OpenAI(base_url=base_url, api_key=token)

    response = dr_client.get(url="genai/llmgw/catalog/")
    llm_catalog = response.json()["data"]
    model = llm_catalog[2]["model"]


    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": (
                "Here is everything you know about the Byte-Sized Business Boost app:\n\n"
                f"{APP_SPEC}\n\n"
                "Use this as the source of truth when helping the user."
            ),
        },
        {
            "role": "user",
            "content": (
                "Answer the following user question using the app description above. "
                "If the question cannot be answered from that context, say you don't know.\n\n"
                f"User question: {question}"
            ),
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content

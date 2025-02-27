from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.schemas import PodcastTranscript
from langchain import hub


podcast_parser = JsonOutputParser(pydantic_object=PodcastTranscript)

podcast_prompt = PromptTemplate(
    template="""Create a detailed podcast transcript based on the given material consisting of Two Hosts. There is One Male and One Female Host. Do not include other than the text. (NO host1: or host2:)\n
Material: {input}\n
{format_instructions}\n
""",
    input_variables=["input"],
    partial_variables={"format_instructions": podcast_parser.get_format_instructions()},
)

rag_prompt = hub.pull("rlm/rag-prompt")

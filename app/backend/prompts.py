from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.schemas import PodcastTranscript
from langchain import hub


podcast_parser = JsonOutputParser(pydantic_object=PodcastTranscript)

podcast_prompt = PromptTemplate(
    template="""Create a detailed single-host podcast transcript where the host analyzes [SPECIFIC TOPIC/MATERIAL]. The transcript should:
Begin with a compelling introduction that hooks the listener and outlines the episode's focus
Include at least 5,000 words of substantive content
Feature the host providing in-depth analysis, personal insights, relevant examples, and occasional questions to engage the audience
Incorporate clear section breaks with distinct themes or subtopics
Include mentions of relevant sources, experts, or research when appropriate
Feature a natural speaking style with occasional verbal fillers and corrections for authenticity
Conclude with a summary of key points and a teaser for the next episode
Avoid timestamps or time markers
Include [ANY SPECIFIC SEGMENTS you want, such as listener questions, sponsored messages, etc.]

The tone should be [FORMAL/CONVERSATIONAL/EDUCATIONAL/etc.] and the intended audience is [TARGET AUDIENCE].
For authenticity, the host should have these characteristics: [HOST PERSONALITY TRAITS, EXPERTISE LEVEL, SPEAKING STYLE].
Note: All bracketed material should be inferred from the input provided - use context clues from the given material to determine appropriate tone, audience, host characteristics, etc.

Don't Include any extra material except the transcript. Assume It is to be read as is by a TTS Engine.
Material: {input}\n
{format_instructions}\n
""",
    input_variables=["input"],
    partial_variables={"format_instructions": podcast_parser.get_format_instructions()},
)

rag_prompt = hub.pull("rlm/rag-prompt")

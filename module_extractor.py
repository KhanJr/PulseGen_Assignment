from langchain_ollama.chat_models import ChatOllama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


class ModuleExtractor:
    def __init__(self, processed_content, model_name="llama3.1"):
        self.processed_content = processed_content
        self.model_name = model_name

    def extract_modules(self):
        """Extract modules and submodules from processed content."""
        # Initialize Ollama LLM
        llm = ChatOllama(
            model=self.model_name,
            temperature=0,
            # Ollama runs locally, so no API key needed
        )

        # Define output schema
        response_schemas = [
            ResponseSchema(
                name="modules",
                description="List of modules extracted from the documentation",
            ),
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

        # Combine all processed content for context
        combined_content = []
        for url, data in self.processed_content.items():
            site_content = f"Documentation Title: {data['title']}\nURL: {url}\n\n"

            for item in data["structure"]:
                site_content += (
                    f"{'#' * item['level']} {item['title']}\n{item['content']}\n\n"
                )

            combined_content.append(site_content)
        # Create a prompt for module extraction
        prompt_template = """
        You are an AI assistant specialized in analyzing documentation and extracting structured information.
        
        I'll provide you with the content from a documentation website. Your task is to:
        1. Identify the main modules or features described in the documentation
        2. For each module, identify submodules or sub-features
        3. Generate detailed descriptions for each module and submodule based ONLY on the content provided
        
        Documentation content:
        {content}
        
        Return the extracted modules in the following JSON format:
        {{
            "modules": [
                {{
                    "module": "Module Name",
                    "description": "Detailed description of the module",
                    "submodules": [
                        {{
                            "submodule": "Submodule Name",
                            "description": "Detailed description of the submodule"
                        }}
                    ]
                }}
            ]
        }}
        
        Only include modules and submodules that are clearly described in the documentation.
        Be specific and factual in your descriptions, using only information from the provided content.
        {format_instructions}
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["content"],
            partial_variables={
                "format_instructions": output_parser.get_format_instructions()
            },
        )

        # Process content in chunks due to context window limitations
        all_results = []

        for content_chunk in combined_content:
            is_Issue = False
            # Run the LLM chain with the prompt and content
            try:
                chain = LLMChain(llm=llm, prompt=prompt)
                response = chain.run(content=content_chunk)
                parsed_response = output_parser.parse(response)
            except Exception as e:
                print(f"Error processing content: {e}")
                is_Issue = True
                continue
            # Check if the response is empty or not in the expected format
            if not is_Issue:
                all_results.extend(parsed_response.get("modules", []))
                continue

        # Format the output in the required format
        formatted_output = self._format_output(all_results)
        return formatted_output

    def _format_output(self, modules_list):
        """Format the modules into the required JSON structure."""
        result = {}

        for module in modules_list:
            module_name = module["module"]
            module_desc = module["description"]

            submodules_dict = {}
            for submodule in module.get("submodules", []):
                submodules_dict[submodule["submodule"]] = submodule["description"]

            result[module_name] = {
                "Description": module_desc,
                "Submodules": submodules_dict,
            }

        return result

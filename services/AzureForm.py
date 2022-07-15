import os, json
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("AZURE_FORM_KEY")
endpoint = os.getenv("AZURE_FORM_ENDPOINT")

# Create client
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

class AzureFormService:
    @staticmethod
    def analysisForm(model_id, formUrl):
        poller = document_analysis_client.begin_analyze_document_from_url(model_id, formUrl)
        result = poller.result()
        fields = {}
        for key, field in result.documents[0].fields.items():
            fields[key] = field.content
        return fields
    
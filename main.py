import os
import pickle

from google.auth.transport.requests import Request

from google_auth_oauthlib.flow import InstalledAppFlow
from llama_index import GPTVectorStoreIndex, download_loader, MockLLMPredictor, ServiceContext

os.environ['OPENAI_API_KEY'] = 'your-open-api-key-here'
llm_predictor = MockLLMPredictor(max_tokens=256)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

def authorize_gdocs():
    cred = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", 'rb') as token:
            cred = pickle.load(token)
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            print(os.getcwd())
            creds_file_path = os.path.abspath('credentials.json')
            google_oauth2_scopes = [
                "https://www.googleapis.com/auth/documents.readonly"
            ]
            flow = InstalledAppFlow.from_client_secrets_file(creds_file_path, google_oauth2_scopes)
            cred = flow.run_local_server(port=0)
        with open("token.pickle", 'wb') as token:
            pickle.dump(cred, token)


if __name__ == '__main__':

    authorize_gdocs()
    GoogleDocsReader = download_loader('GoogleDocsReader')
    gdoc_ids = ['your-google-doc-id-here']
    loader = GoogleDocsReader()
    documents = loader.load_data(document_ids=gdoc_ids)
    index = GPTVectorStoreIndex.from_documents(documents)
   
    while True:
        prompt = input("Type prompt...")
        query_engine = index.as_query_engine()
        response = query_engine.query(prompt)
        print(response)        
        
        query_engine = index.as_query_engine(
        service_context=service_context
        )
        # get number of tokens used
        print(llm_predictor.last_token_usage)

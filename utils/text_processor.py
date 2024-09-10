import spacy
import logging

logger = logging.getLogger(__name__)

def load_spacy_model():
    try:
        logger.info("Loading Chinese language model")
        return spacy.load("zh_core_web_sm")
    except OSError:
        logger.warning("Chinese language model not found. Downloading...")
        spacy.cli.download("zh_core_web_sm")
        logger.info("Chinese language model downloaded successfully")
        return spacy.load("zh_core_web_sm")

nlp = load_spacy_model()

def preprocess_text(text):
    try:
        logger.info(f"Preprocessing text of length: {len(text)}")
        logger.info(f"Input text: {text[:100]}...")  # Log the first 100 characters of input text

        # Process the text with spaCy
        doc = nlp(text)
        
        # For Chinese, we'll keep all tokens except punctuation and whitespace
        processed_text = " ".join([token.text for token in doc if not token.is_punct and not token.is_space])
        
        logger.info(f"Preprocessed text: {processed_text[:100]}...")  # Log the first 100 characters of preprocessed text
        logger.info(f"Preprocessing completed. Output length: {len(processed_text)}")
        return processed_text
    except Exception as e:
        logger.error(f"Error during text preprocessing: {str(e)}", exc_info=True)
        raise

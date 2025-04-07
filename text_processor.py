import nltk
import re
import streamlit as st
import os

# Make sure NLTK data path is properly set up
nltk_data_dir = '/home/runner/nltk_data'
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download required NLTK data
try:
    nltk.download('vader_lexicon', download_dir=nltk_data_dir, quiet=True)
    nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
except Exception as e:
    st.warning(f"Failed to download NLTK data: {str(e)}")
    
# Verify resources were downloaded
if not nltk.data.find('tokenizers/punkt'):
    st.warning("NLTK punkt tokenizer not available - some functions may be limited.")

# Now import the modules that require the downloaded data
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize

def process_text(text):
    """
    Process text for analysis:
    - Convert to lowercase
    - Remove special characters
    - Tokenize
    
    Parameters:
    - text: Input text to process
    
    Returns:
    - Processed text and tokens
    """
    if not text or not isinstance(text, str):
        return "", []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Try to use NLTK's word_tokenize, but fall back to simple splitting if it fails
    tokens = []
    try:
        # First check if the punkt resource is available
        if nltk.data.find('tokenizers/punkt'):
            tokens = word_tokenize(text)
        else:
            # If punkt is not available, use simple splitting
            tokens = text.split()
    except Exception as e:
        # Simple fallback tokenization
        tokens = text.split()
    
    return text, tokens

def extract_soft_skills(text):
    """
    Extract soft skills mentioned in text
    
    Parameters:
    - text: Input text to analyze
    
    Returns:
    - List of identified soft skills
    """
    if not text or not isinstance(text, str):
        return []
    
    # Common soft skills to look for
    soft_skills_keywords = [
        'communication', 'teamwork', 'leadership', 'problem solving', 'problem-solving',
        'critical thinking', 'time management', 'adaptability', 'flexibility', 'creativity',
        'work ethic', 'interpersonal', 'collaboration', 'decision making', 'decision-making',
        'emotional intelligence', 'conflict resolution', 'negotiation', 'persuasion',
        'public speaking', 'customer service', 'attention to detail', 'organization',
        'planning', 'strategic thinking', 'analytical', 'project management', 'multitasking',
        'resourcefulness', 'active listening', 'empathy', 'patience', 'confidence',
        'self-motivation', 'reliability', 'professionalism', 'integrity', 'ethics',
        'cultural awareness', 'mentoring', 'coaching', 'feedback', 'delegation',
        'resilience', 'positive attitude', 'enthusiasm', 'innovation'
    ]
    
    # Process text
    processed_text, _ = process_text(text)
    
    # Find soft skills in text
    found_skills = []
    for skill in soft_skills_keywords:
        if skill in processed_text:
            found_skills.append(skill)
    
    return found_skills

def analyze_sentiment(text):
    """
    Analyze sentiment of text using NLTK's SentimentIntensityAnalyzer
    
    Parameters:
    - text: Input text to analyze
    
    Returns:
    - Dictionary with sentiment scores
    """
    if not text or not isinstance(text, str):
        return {'pos': 0, 'neg': 0, 'neu': 1, 'compound': 0}
    
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Analyze text
    sentiment_scores = sia.polarity_scores(text)
    
    return sentiment_scores

def extract_key_phrases(text, num_phrases=5):
    """
    Extract key phrases from text based on frequency and positioning
    
    Parameters:
    - text: Input text to analyze
    - num_phrases: Number of key phrases to extract
    
    Returns:
    - List of key phrases
    """
    if not text or not isinstance(text, str):
        return []
    
    # Split into sentences with fallback
    sentences = []
    try:
        # First check if the punkt resource is available
        if nltk.data.find('tokenizers/punkt'):
            sentences = sent_tokenize(text)
        else:
            # If punkt is not available, use simple splitting
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
    except Exception as e:
        # Simple fallback for sentence tokenization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
    
    # Process sentences
    processed_sentences = []
    for sentence in sentences:
        processed_text, tokens = process_text(sentence)
        if tokens:
            processed_sentences.append((processed_text, tokens))
    
    # Count word frequencies
    word_freq = {}
    for _, tokens in processed_sentences:
        for token in tokens:
            if len(token) > 1:  # Filter out single-character tokens
                word_freq[token] = word_freq.get(token, 0) + 1
    
    # Score sentences based on word frequency and position
    sentence_scores = []
    for i, (sentence, tokens) in enumerate(processed_sentences):
        score = 0
        for token in tokens:
            if token in word_freq:
                score += word_freq[token]
        
        # Add position weight (earlier sentences often contain key information)
        position_weight = 1.0 - (0.5 * i / len(processed_sentences))
        score *= position_weight
        
        sentence_scores.append((sentence, score))
    
    # Sort sentences by score
    sorted_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)
    
    # Extract top phrases
    key_phrases = [sentence for sentence, _ in sorted_sentences[:num_phrases]]
    
    return key_phrases

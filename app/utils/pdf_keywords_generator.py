from pypdf import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from rest_framework.exceptions import ValidationError

def generate_pdf_keywords(file):
    if not str(file).endswith('.pdf'):
        raise ValidationError({"message": "Only PDF files are accepted."})

    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
        
    reader = PdfReader(file)
    total_pages = len(reader.pages)
    most_used_words = []
    
    for i in range(0, total_pages):
        print(f"Reading Page #{i+1} of {str(file)}...")
        page = reader.pages[i]
        text = page.extract_text()
    
        words = word_tokenize(text.lower())        
        stop_words = set(stopwords.words('english'))
        
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        pos_tagged_words = pos_tag(filtered_words)
        relevant_words = [word for word, pos in pos_tagged_words if pos.startswith('NN') or pos.startswith('JJ')]
        
        unique_relevant_words = list(set(relevant_words))
        freq_dist = FreqDist(unique_relevant_words)
        most_common_words = freq_dist.most_common(100)

        for word, frequencies in most_common_words:
            most_used_words.append(
                {
                    "frequencies": frequencies,
                    "word": word,
                }
            )
        
    top_100_words = sorted(most_used_words, key=lambda x: x['frequencies'], reverse=True)[:100]
    top_100_words_list = [entry['word'] for entry in top_100_words]
    
    return top_100_words_list
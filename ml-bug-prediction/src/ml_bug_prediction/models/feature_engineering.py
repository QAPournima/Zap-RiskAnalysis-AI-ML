from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def create_text_features(data):
    vectorizer = TfidfVectorizer(max_features=100)
    text_features = vectorizer.fit_transform(data['text']).toarray()
    text_feature_names = vectorizer.get_feature_names_out()
    text_feature_df = pd.DataFrame(text_features, columns=text_feature_names)
    return pd.concat([data.reset_index(drop=True), text_feature_df.reset_index(drop=True)], axis=1)

def create_interaction_features(data):
    data['feature_interaction'] = data['feature1'] * data['feature2']
    return data

def engineer_features(data):
    data = create_text_features(data)
    data = create_interaction_features(data)
    return data
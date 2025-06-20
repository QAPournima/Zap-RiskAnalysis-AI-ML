from sklearn.externals import joblib
import pandas as pd

def load_model(model_path):
    """Load the trained machine learning model from the specified path."""
    model = joblib.load(model_path)
    return model

def make_prediction(model, input_data):
    """Make a prediction using the trained model and input data."""
    prediction = model.predict(input_data)
    return prediction

def predict(input_data, model_path='model.pkl'):
    """Load the model and make a prediction on the input data."""
    model = load_model(model_path)
    prediction = make_prediction(model, input_data)
    return prediction

if __name__ == "__main__":
    # Example usage
    input_data = pd.DataFrame()  # Replace with actual input data
    model_path = 'model.pkl'  # Replace with the actual model path
    prediction = predict(input_data, model_path)
    print(prediction)
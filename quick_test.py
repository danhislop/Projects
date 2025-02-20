from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load

# first time # add comment

def first_time():
    # Train a simple model
    model = RandomForestClassifier()
    model.fit([[1, 2], [3, 4], [5, 6]], [0, 1, 0])

    # Save the model
    dump(model, 'random_forest_model.joblib')

# Load the model
loaded_model = load('random_forest_model.joblib')

# Test it
print(loaded_model.predict([[3, 4]]))  # Output: [1]
print(loaded_model.predict([[1, 2]]))  # Output: [0]
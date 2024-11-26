"""
https://arxiv.org/pdf/1712.01208
https://arxiv.org/pdf/2308.11205
"""
import numpy as np
from sklearn.linear_model import LinearRegression


class LearnedIndex:
    def __init__(self, keys, values):
        """
        Initializes the learned index.
        :param keys: Sorted keys
        :param values: Values corresponding to the keys
        """
        assert len(keys) == len(values), "Keys and values must have the same length"
        assert np.all(np.diff(keys) > 0), "Keys must be sorted in ascending order"

        self.keys = np.array(keys)
        self.values = np.array(values)
        self.model = LinearRegression()

        # Train the model to predict positions in the sorted array
        positions = np.arange(len(keys)).reshape(-1, 1)
        self.model.fit(self.keys.reshape(-1, 1), positions)

    def predict_position(self, key):
        """
        Predicts the approximate position of a key.
        """
        pred_pos = self.model.predict([[key]])
        # Clamp the prediction to be within valid bounds
        pred_pos = max(0, min(len(self.keys) - 1, int(pred_pos[0])))
        return pred_pos

    def search(self, key):
        """
        Searches for the value corresponding to the given key.
        """
        # Predict the approximate position
        pred_pos = self.predict_position(key)

        # Refine the prediction with a local binary search
        start = max(0, pred_pos - 10)  # Search around the predicted position
        end = min(len(self.keys), pred_pos + 10)

        # Perform a binary search in the vicinity
        idx = np.searchsorted(self.keys[start:end], key) + start
        if idx < len(self.keys) and self.keys[idx] == key:
            return self.values[idx]
        return None  # Key not found


# Example Usage
if __name__ == "__main__":
    # Generate sorted data
    keys = np.arange(1, 10001)
    values = np.random.randint(100, 200, size=len(keys))

    # Initialize the learned index
    index = LearnedIndex(keys, values)

    # Search for a key
    search_key = 5678
    result = index.search(search_key)
    print(f"Value for key {search_key}: {result}")

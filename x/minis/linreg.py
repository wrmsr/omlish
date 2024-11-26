import numpy as np


class SimpleLinearRegression:
    def __init__(self):
        self.coef_ = None  # Coefficients (weights)
        self.intercept_ = None  # Intercept (bias)

    def fit(self, X, y):
        """
        Fit a linear regression model using the normal equation.

        Parameters:
        X: numpy array of shape (n_samples, n_features) - Input features
        y: numpy array of shape (n_samples,) - Target values
        """
        # Add a column of ones to X for the intercept term
        X_with_bias = np.hstack([np.ones((X.shape[0], 1)), X])

        # Compute the weights using the normal equation
        # w = (X^T * X)^(-1) * X^T * y
        weights = np.linalg.inv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y

        # Separate the intercept and coefficients
        self.intercept_ = weights[0]
        self.coef_ = weights[1:]

    def predict(self, X):
        """
        Predict target values for given input features.

        Parameters:
        X: numpy array of shape (n_samples, n_features) - Input features

        Returns:
        y_pred: numpy array of shape (n_samples,) - Predicted values
        """
        return X @ self.coef_ + self.intercept_


# Example usage:
if __name__ == "__main__":
    # Example data
    X = np.array([[1], [2], [3]])  # Single feature
    y = np.array([2, 4, 6])  # Target values

    # Fit the model
    model = SimpleLinearRegression()
    model.fit(X, y)

    # Print the parameters
    print("Intercept:", model.intercept_)
    print("Coefficients:", model.coef_)

    # Make predictions
    y_pred = model.predict(X)
    print("Predictions:", y_pred)

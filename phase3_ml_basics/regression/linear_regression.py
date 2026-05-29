import numpy as np

class LinearRegression:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.epochs):
            y_pred = X @ self.weights + self.bias
            dw = (2 / n_samples) * (X.T @ (y_pred - y))
            db = (2 / n_samples) * np.sum(y_pred - y)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db

    def predict(self, X):
        return X @ self.weights + self.bias

if __name__ == "__main__":
    from sklearn.datasets import make_regression
    X, y = make_regression(n_samples=100, n_features=1, noise=10)
    model = LinearRegression()
    model.fit(X, y)
    print("Predictions:", model.predict(X[:5]))

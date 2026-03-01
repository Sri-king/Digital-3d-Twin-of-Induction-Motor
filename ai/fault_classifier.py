import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings

# Suppress sklearn warnings about feature names lacking
warnings.filterwarnings("ignore", module="sklearn")

class AIFaultClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Buffer to compute sliding window features during live simulation
        self.window_size = 5
        self.history = []

    def _extract_features(self, df_window):
        """
        Extracts time-series features from a sliding window of sensor data.
        Features must match the trained model.
        """
        features = {
            'mean_current': df_window['Current'].mean(),
            'peak_current': df_window['Current'].max(),
            'rpm_decay_rate': df_window['RPM'].iloc[-1] - df_window['RPM'].iloc[0],
            'temp_slope': df_window['Temperature'].iloc[-1] - df_window['Temperature'].iloc[0],
            'slip_trend': df_window['Slip'].iloc[-1] - df_window['Slip'].iloc[0],
            'vibration_rms': np.sqrt(np.mean(df_window['Vibration']**2)),
            'load_torque_var': df_window['Load_Torque'].var() if len(df_window) > 1 else 0.0
        }
        return pd.Series(features)

    def train(self, dataset_path):
        """
        Offline pretraining using the bulk synthetic dataset.
        Extracts row-by-row rolling window features.
        """
        print(f"Loading dataset from {dataset_path} for AI Training...")
        try:
            df = pd.read_csv(dataset_path)
            
            # Create rolling window features for the entire dataset
            X_list = []
            y_list = []
            
            print("Extracting time-series features from raw data...")
            for i in range(len(df)):
                # Get up to 'window_size' previous rows
                start_idx = max(0, i - self.window_size + 1)
                window = df.iloc[start_idx:i+1]
                
                features = self._extract_features(window)
                X_list.append(features)
                # Train the AI to predict the RULE ENGINE'S label (or the Ground truth).
                # We will train it on the injected physics cause to verify if it can figure it out.
                y_list.append(df.iloc[i]['Injected_Physics_Cause'])
                
            X = pd.DataFrame(X_list)
            y = np.array(y_list)
            
            # Handle NaNs from variance calculations on 1-row windows
            X.fillna(0, inplace=True)
            
            print("Training Random Forest Classifier...")
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Quick training accuracy
            acc = self.model.score(X_scaled, y)
            print(f"AI Model Trained Successfully! Training Accuracy: {acc*100:.2f}%\n")
            return acc
        except FileNotFoundError:
            print(f"Error: {dataset_path} not found. Cannot train AI.")
            return 0.0

    def predict(self, current_sensor_row):
        """
        Online prediction during live simulation.
        Maintains a rolling buffer to extract features.
        """
        if not self.is_trained:
            return "AI_NOT_TRAINED"
            
        self.history.append(current_sensor_row)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        df_window = pd.DataFrame(self.history)
        features = self._extract_features(df_window)
        
        # Format for sklearn
        X = pd.DataFrame([features]).fillna(0)
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        return prediction

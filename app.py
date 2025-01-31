from flask import Flask,request,render_template
import pandas as pd
import numpy as np
import joblib
from pathlib import Path 
import requests
from flask import jsonify

app = Flask(__name__)

path = Path(__file__).parent
model_path = path / 'model_2801.joblib'

data_path = path / 'data_2801.joblib'

with open(model_path, 'rb') as file:
    model = joblib.load(file)

with open(data_path, 'rb') as file:
    data = joblib.load(file)
    
def predict_data(store, category):
    filtered_data = data[(data['Store_num'] == store) & (data['nacs_category'] == category)]
    last_row = filtered_data.iloc[-1:].copy()
    forecast = []
    for day in range(1, 8):
        # Create lag features dynamically for the forecasted period
        for lag in range(1, 8):
            if lag == day:
                last_row[f'lag_{lag}_QTY'] = forecast[-1] if forecast else last_row['Total_QTY'].values[0]
            else:
             last_row[f'lag_{lag}_QTY'] = last_row[f'lag_{lag}_QTY']

        # Update rolling mean based on forecast
        last_row['rolling_mean_QTY_7'] = last_row[[f'lag_{i}_QTY' for i in range(1, 8)]].mean(axis=1)

         # Predict the quantity for the next day
        next_qty = model.predict(last_row.drop(columns=['Date', 'Total_QTY']))[0]
        forecast.append(next_qty)

        # Update last_row for the next prediction
        last_row['Total_QTY'] = next_qty
    forecast_df = pd.DataFrame({    
    'Forecasted_QTY': forecast
})
    print(forecast_df['Forecasted_QTY'].cumsum().iloc[-1])
    if forecast_df['Forecasted_QTY'].cumsum().iloc[-1] > 10:
     return "Restock needed"
    else:
        return "No restock needed"

    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST', 'GET'])
def predict():    
    if request.method == 'POST':        
        data = request.json
        print(data)
        store_num = int(data['store'])
        category = int(data['category'])
        
        prediction = predict_data(store_num, category)
        return jsonify({"prediction": prediction})
        
    elif request.method == 'GET':            
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1',port=5000)
    

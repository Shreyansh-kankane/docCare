from flask import Flask
from flask import jsonify
from numpy import array
import pickle
#model=pickle.load(open('newmodel.pkl','rb'))
heartmodel=pickle.load(open('heart_pickle.pkl','rb'))
data_dict={0: 'itching', 1: 'skin rash', 2: 'nodal skin eruptions', 3: 'continuous sneezing', 4: 'shivering', 5: 'chills', 6: 'joint pain', 7: 'stomach pain', 8: 'acidity', 9: 'ulcers on tongue', 10: 'muscle wasting', 11: 'vomiting', 12: 'burning micturition', 13: 'spotting  urination', 14: 'fatigue', 15: 'weight gain', 16: 'anxiety', 17: 'cold hands and feets', 18: 'mood swings', 19: 'weight loss', 20: 'restlessness', 21: 'lethargy', 22: 'patches in throat', 23: 'irregular sugar level', 24: 'cough', 25: 'high fever', 26: 'sunken eyes', 27: 'breathlessness', 28: 'sweating', 29: 'dehydration', 30: 'indigestion', 31: 'headache', 32: 'yellowish skin', 33: 'dark urine', 34: 'nausea', 35: 'loss of appetite', 36: 'pain behind the eyes', 37: 'back pain', 38: 'constipation', 39: 'abdominal pain', 40: 'diarrhoea', 41: 'mild fever', 42: 'yellow urine', 43: 'yellowing of eyes', 44: 'acute liver failure', 45: 'fluid overload', 46: 'swelling of stomach', 47: 'swelled lymph nodes', 48: 'malaise', 49: 'blurred and distorted vision', 50: 'phlegm', 51: 'throat irritation', 52: 'redness of eyes', 53: 'sinus pressure', 54: 'runny nose', 55: 'congestion', 56: 'chest pain', 57: 'weakness in limbs', 58: 'fast heart rate', 59: 'pain during bowel movements', 60: 'pain in anal region', 61: 'bloody stool', 62: 'irritation in anus', 63: 'neck pain', 64: 'dizziness', 65: 'cramps', 66: 'bruising', 67: 'obesity', 68: 'swollen legs', 69: 'swollen blood vessels', 70: 'puffy face and eyes', 71: 'enlarged thyroid', 72: 'brittle nails', 73: 'swollen extremeties', 74: 'excessive hunger', 75: 'extra marital contacts', 76: 'drying and tingling lips', 77: 'slurred speech', 78: 'knee pain', 79: 'hip joint pain', 80: 'muscle weakness', 81: 'stiff neck', 82: 'swelling joints', 83: 'movement stiffness', 84: 'spinning movements', 85: 'loss of balance', 86: 'unsteadiness', 87: 'weakness of one body side', 88: 'loss of smell', 89: 'bladder discomfort', 90: 'foul smell of urine', 91: 'continuous feel of urine', 92: 'passage of gases', 93: 'internal itching', 94: 'toxic look (typhos)', 95: 'depression', 96: 'irritability', 97: 'muscle pain', 98: 'altered sensorium', 99: 'red spots over body', 100: 'belly pain', 101: 'abnormal menstruation', 102: 'dischromic  patches', 103: 'watering from eyes', 104: 'increased appetite', 105: 'polyuria', 106: 'family history', 107: 'mucoid sputum', 108: 'rusty sputum', 109: 'lack of concentration', 110: 'visual disturbances', 111: 'receiving blood transfusion', 112: 'receiving unsterile injections', 113: 'coma', 114: 'stomach bleeding', 115: 'distention of abdomen', 116: 'history of alcohol consumption', 117: 'fluid overload.1', 118: 'blood in sputum', 119: 'prominent veins on calf', 120: 'palpitations', 121: 'painful walking', 122: 'pus filled pimples', 123: 'blackheads', 124: 'scurring', 125: 'skin peeling', 126: 'silver like dusting', 127: 'small dents in nails', 128: 'inflammatory nails', 129: 'blister', 130: 'red sore around nose', 131: 'yellow crust ooze', 132: 'prognosis'}
name_maper={'(vertigo) Paroymsal  Positional Vertigo': 0, 'AIDS': 1, 'Acne': 2, 'Alcoholic hepatitis': 3, 'Allergy': 4, 'Arthritis': 5, 'Bronchial Asthma': 6, 
'Cervical spondylosis': 7, 'Chicken pox': 8, 'Chronic cholestasis': 9, 'Common Cold': 10, 'Dengue': 11, 'Diabetes ': 12, 'Dimorphic hemmorhoids(piles)': 13, 'Drug Reaction': 14, 'Fungal infection': 15, 'GERD': 16, 'Gastroenteritis': 17, 'Heart attack': 18, 'Hepatitis B': 19, 'Hepatitis C': 20, 'Hepatitis D': 21, 'Hepatitis E': 22, 'Hypertension ': 23, 'Hyperthyroidism': 24, 'Hypoglycemia': 25, 'Hypothyroidism': 26, 'Impetigo': 27, 'Jaundice': 28, 'Malaria': 29, 'Migraine': 30, 'Osteoarthristis': 31, 'Paralysis (brain hemorrhage)': 32, 'Peptic ulcer diseae': 33, 'Pneumonia': 34, 'Psoriasis': 35, 'Tuberculosis': 36, 'Typhoid': 37, 'Urinary tract infection': 38, 'Varicose veins': 39, 'hepatitis A': 40}
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def welcome():
    return """Hello World! Disease Prediction API model by ZERO <br>
    Put a star on my github<a href="https://github.com/popeyewrener"> GITHUB REPO</a> if you like my project!!<br>
    Access method to access the disease prediction ml model:<br>
    <a href='/predict/'> Click here </a>
    """
@app.route('/predict/')
def predictinit():
    return """ api calling style: <website domain name>/predict/list of disease codes separated each other by"_'"""

@app.route('/predict/<inputs>')
def show_post(inputs):
    inputs=str(inputs)
    inputs=inputs.split('_')
    
    input_data = [0] *( len(data_dict)-1)
    for symptom in inputs:
        index = int(symptom)
        input_data[index] = 1
        
    # reshaping the input data and converting it
    # into suitable format for model predictions
    input_data = array(input_data).reshape(1,-1)
    final_pred=model.predict(input_data)[0]
    return jsonify(code=name_maper[final_pred],
    name=str(final_pred)
    )   

    #use post title to fetch the record from db
@app.route('/numbers/')
def print_list():
    return jsonify(list(range(5)))   

@app.route('/heartdisease/<inputs>')
def heart(inputs):
    inputs=str(inputs)
    inputs=inputs.split('_')
    for i in range(0,len(inputs)):
        inputs[i]=float(inputs[i])

    input_data = array(inputs).reshape(1,-1)
    final_pred=heartmodel.predict(input_data)[0]
    return jsonify(result=final_pred)
     

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
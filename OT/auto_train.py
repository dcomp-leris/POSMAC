import sqlite3, os
import time
from sklearn.tree import DecisionTreeClassifier
import joblib
import pandas as pd
import socket
from sklearn.ensemble import RandomForestClassifier
import yaml
#from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
#from sklearn.model_selection import train_test_split



# Configuration
DATABASE_PATH = '/home/ot/traffic.db'
MODEL_PATH = 'dt_model.joblib'
#MODEL_PATH = '/home/ot/rf_model.joblib'
IS_DT = False


SERVER_IP = '192.168.140.2' # cls server
INTERVAL = 2  # seconds
APPROVALS_THRESHOLD = 1


def load_config(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def fetch_data():
    conn = sqlite3.connect(DATABASE_PATH)
    query = f"SELECT ifi, ipi, fs, ps, class FROM traffic_data WHERE approvals >  {APPROVALS_THRESHOLD}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def check_conditions(df):
    counts = df['class'].value_counts()
    class_group_1 = ['AR'] #['AR_DL', 'AR_UL', 'AR']
    class_group_2 = ['CG']  # ['CG_DL', 'CG_UL', 'CG']
    class_group_3 = ['Other'] # ['Other', 'other']
    count_group_1 = counts.loc[counts.index.isin(class_group_1)].sum()
    count_group_2 = counts.loc[counts.index.isin(class_group_2)].sum()
    count_group_3 = counts.loc[counts.index.isin(class_group_3)].sum()
    if count_group_1 == 0 or count_group_2 == 0 or count_group_3==0:
        return False
    '''lower_bound = min(count_group_1, count_group_2) * 0.8
    upper_bound = max(count_group_1, count_group_2) * 1.2
    if not (lower_bound <= count_group_1 <= upper_bound and lower_bound <= count_group_2 <= upper_bound):
        return False
    if (count_group_1 + count_group_2) < 1:
        return False'''
    return True


def train_model(data, model_path):
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        model = DecisionTreeClassifier(class_weight='balanced')
    X = data[['ifi', 'ipi', 'fs','ps']]
    y = data['class']
    model.fit(X, y)
    return model

def clear_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM traffic_data")
    conn.commit()
    conn.close()

def save_model(model, model_path):
    joblib.dump(model, model_path)

def send_model(host_ip, host_port, file_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_ip, host_port))
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                s.sendall(data)
    finally:
        s.close()


'''def cleanup_zero_approvals():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = f"SELECT ifi, ipi, fs, class FROM traffic_data WHERE approvals = 0" 
    df_e = pd.read_sql_query(query, conn)
    conn.close()
    X_e = df_e[['ifi', 'ipi', 'fs']]
    y_e = df_e['class']
    print(y_e)
    y_c  = ['CG_DL' if x == 'AR_DL' else 'AR_DL' if x == 'CG_DL' else 'CG_UL' if x == 'AR_UL' else 'AR_UL' if x == 'CG_UL' else x for x in y_e]

    print(f"{X_e} {y_c} samples with zero approvals.")
    model = joblib.load(MODEL_PATH)
    model.fit(X_e, y_c)
    print('We trained the model successfully!')
    return model
    #conn.close()'''
    


def combined_training():
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Fetch new training data
    train_query = "SELECT ifi, ipi, fs, ps, class FROM traffic_data WHERE approvals > 0"
    df_train = pd.read_sql_query(train_query, conn)
    
    # Fetch data with zero approvals
    # cleanup_query = "SELECT ifi, ipi, fs, ps, class FROM traffic_data WHERE approvals = 0"
    cleanup_query = "SELECT ifi, ipi, fs, ps, dst_ip FROM traffic_data WHERE approvals = 0"
    df_cleanup = pd.read_sql_query(cleanup_query, conn)
    conn.close()  # Close the database connection

    # Process df_cleanup to change class labels
    '''df_cleanup['class'] = df_cleanup['class'].map({
        'AR_DL': 'CG_DL',
        'CG_DL': 'AR_DL',
        'AR_UL': 'CG_UL',
        'CG_UL': 'AR_UL'

    }).fillna(df_cleanup['class'])'''  # Handles cases where class labels do not match any key in the map
    # Process df_cleanup to change class labels based on destination IP
    df_cleanup['class'] = df_cleanup['dst_ip'].map({
        '120.120.120.1': 'AR',
        '130.130.130.1': 'CG',
        '140.140.140.1': 'Other'
    }).fillna('Other')  # Set to 'Other' if destination IP does not match any key


    # Combine the datasets
    combined_X = pd.concat([df_train[['ifi', 'ipi', 'fs','ps']], df_cleanup[['ifi', 'ipi', 'fs','ps']]], ignore_index=True)
    combined_y = pd.concat([df_train['class'], df_cleanup['class']], ignore_index=True)

    # Load existing model or create a new one
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    elif IS_DT == True:
        model = DecisionTreeClassifier(class_weight='balanced')
        print("No pre-existing model found, training a new model.")
    elif IS_DT == False:
        model = RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42)
    # Train or retrain the model on the combined data
    model.fit(combined_X, combined_y)
    joblib.dump(model, MODEL_PATH)  # Save the retrained model
    print("Model trained and saved successfully with combined data.")

    return model



def main():
    #cleanup_interval = 120  # Interval in seconds to clean up zero approvals

    config = load_config('config.yaml')
    MODEL_PATH = config['ot_config']['model'][config['ot_config']['model']['selection']]
    cls_SERVER_IP = config['ot_config']['cls']['ip']     #'192.168.140.3'
    cls_Port = config['ot_config']['cls']['send']['port']  # 5001
    INTERVAL = config['ot_config']['model']['interval']
    APPROVALS_THRESHOLD = config['ot_config']['model']['threshold']
    DATABASE_PATH = config['ot_config']['db']['name']


    last_cleanup = time.time()

    while True:
        current_time = time.time()

        data = fetch_data()
        if not data.empty:
            if check_conditions(data):
                #model = train_model(data, MODEL_PATH)
                model = combined_training()
                #clear_database()
                save_model(model, MODEL_PATH)
                send_model(cls_SERVER_IP, cls_Port, MODEL_PATH)
            else:
                print("Conditions not met. Waiting to collect more samples.")
        
        # Check if it's time to run the cleanup
        '''if (current_time - last_cleanup) >= INTERVAL:
            model cleanup_zero_approvals()
            last_cleanup = current_time  # Reset the last cleanup time'''

        time.sleep(INTERVAL)



if __name__ == "__main__":
    main()
 

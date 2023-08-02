from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2



app = Flask(__name__)

# PostgreSQL database configuration
db_host = 'localhost'
db_port = '5432'
db_name = 'test'
db_user = 'postgres'
db_password = '4486'

# Create the database connection
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
def create_table():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS your_table_name (
            id SERIAL PRIMARY KEY,
            protocol_type TEXT,
            service TEXT,
            dst_bytes TEXT,
            flag TEXT,
            src_bytes TEXT,
            urgent TEXT,
            wrong_fragment TEXT
        )
        '''
        cursor.execute(create_table_query)
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Error creating table: {error}")


# Call the create_table function to create the table
create_table()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        excel_file = request.files['excel_file']
        df = pd.read_excel(excel_file)

        # Save DataFrame to PostgreSQL database
        df.to_sql('uploaded_data', con=engine, if_exists='replace', index=False)

        # Render the template with a pop-up message
        return render_template('index.html', message='Data uploaded successfully.')

    return render_template('index.html')


# Route for the form page
@app.route('/form')
def form():
    return render_template('form.html')


# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    protocol_type = request.form['protocol_type']
    service = request.form['service']
    dst_bytes = request.form['dst_bytes']
    flag = request.form['flag']
    src_bytes = request.form['src_bytes']
    urgent = request.form['urgent']
    wrong_fragment = request.form['wrong_fragment']

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Insert values into the table
        insert_query = "INSERT INTO your_table_name (protocol_type, service,dst_bytes,flag,src_bytes,urgent,wrong_fragment) VALUES (%s, %s,%s,%s,%s,%s,%s)"
        cursor.execute(insert_query, (protocol_type, service,dst_bytes,flag,src_bytes,urgent,wrong_fragment))
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Render the template with a pop-up message
        return render_template('form.html', message='Data inserted successfully.')

    except (Exception, psycopg2.Error) as error:
        return f"Error: {error}"

@app.route('/compare', methods=['GET'])
def compare():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Execute the query to compare protocol_type and service columns
        query = '''
            SELECT *
            FROM uploaded_data
            WHERE protocol_type IN (
                SELECT protocol_type
                FROM your_table_name
            )
            AND service IN (
                SELECT service
                FROM your_table_name
            )
        '''
        cursor.execute(query)

        # Fetch matching rows from the query result
        matching_rows = cursor.fetchall()

        # Get the count of matching rows for each protocol_type
        protocol_counts = {}
        for row in matching_rows:
            protocol_type = row[1]
            if protocol_type in protocol_counts:
                protocol_counts[protocol_type] += 1
            else:
                protocol_counts[protocol_type] = 1

        # Get the labels and data for the compare graph
        labels = list(protocol_counts.keys())
        data = list(protocol_counts.values())

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Render the template with matching rows and graph data
        return render_template('compare.html', matching_rows=matching_rows, labels=labels, data=data)

    except (Exception, psycopg2.Error) as error:
        return f"Error: {error}"



@app.route('/drop-table', methods=['POST'])
def drop_table():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Drop the table if it exists
        drop_table_query = '''
        DROP TABLE IF EXISTS your_table_name
        '''
        cursor.execute(drop_table_query)
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Render the template with a pop-up message
        return render_template('index.html', message='Reset Successful.')

    except (Exception, psycopg2.Error) as error:
        return f"Error: {error}"


if __name__ == '__main__':
    app.run(debug=True)

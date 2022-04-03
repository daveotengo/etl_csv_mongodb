from etlcsvmongodb import create_app

app = create_app()

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True,port=3000,host='0.0.0.0')
    # Press the green button in the gutter to run the script.

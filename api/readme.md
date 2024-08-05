pip install -r requirements.txt

Goal:

1. Get the communuty using and giving feedback
    1. portfolio performance tab:
        Allow user to add accounts and assets.
        An asset may or many not belong to an account.
        So the user may add an asset like 1. google shares qty 100
                                          2. Car
                                          3. Home
    2. Inside sqlite maintain a table called assets
        ID      name    value   date   ROW_START     ROW_END 
    3. Inside sqlite maintain a table called accounts.
        ID      name    account_number    is_it_active
    4. Allow to type in chat box:
        "I have a car"
            This should make an entry in the assets table for car
        "The value of my car is $2000"    
            This should update the assets table for car with the value 2000
    5. In the UI show all the assets and the accounts.


    5. Do a gitignore for the .env file
    6. Create a new repo and commit the code again. Otherwise from history people can get the api key.
    7. Chat window should be available on all the tabs.
    


Done:
1. July 24th review at 10 PM PST
    1. Launch the website and the app. Make a simple home page.
    2. Download sqlite option from the profile dropdown.
    3. instead of azure use openai
    4. Free users will use the GPT-4o mini model due to 1/20th price
    5. Set your own API key from the profile option if you want to use better model.
    6. Put the API key that we are using by default in the .env variable.

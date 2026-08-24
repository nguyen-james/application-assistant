import keyboard, pyperclip, json



def load_data():
    
    data_path = "data.json"

    with open (data_path, "r") as file:
        data = json.load(file)
        return data

   

def intialize_hotkeys():
    pass



    
    

def main():

    data = load_data()

    print(data)

    
    
        


if __name__ == "__main__":
    main()
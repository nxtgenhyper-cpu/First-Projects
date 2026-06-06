import ollama

while True:
    choice = input("Gib ein (1) Chat, (2) Rechner oder 'exit' zum Beenden: ").strip().lower()

    if choice == "1":
        while True:
            text = input("Gib etwas ein (oder 'exit'): ")

            if text.strip().lower() == "exit":
                break

            result = ollama.generate(model="tinyllama:1.1b", prompt=text)
            print(result["response"])
            print(" ")

    elif choice == "2":
        
        num1 = float(input("Gib deine erste Zahl ein: "))
        operator = input("Gib einen Operator (+,-,*,/) ein: ")
        num2 = float(input("Gib deine zweite Zahl ein: "))
        if operator == "+":
            print(num1 + num2)
        elif operator == "-":
            print(num1 - num2)
        elif operator == "*":
            print(num1 * num2)
        elif operator == "/":
           print(num1 / num2)
        else:
            print("Ungültiger Operator!")

    elif choice == "exit":
        print("Programm beendet ")
        break

    else:
        print("Ungültige Eingabe!")

        

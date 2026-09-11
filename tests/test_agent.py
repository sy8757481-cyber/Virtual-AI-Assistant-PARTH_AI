from brain.agent import Agent

agent = Agent()

while True:

    text = input("You : ")

    if text.lower() == "exit":
        agent.close()
        break

    agent.execute(text)
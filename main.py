from agent.llm import agent_reply

def main():
    print("Restaurant AI Agent (type 'exit' to quit)\n")
    history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        response = agent_reply(user_input, history)
        print("Agent:", response)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
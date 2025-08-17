from agent.aws_agent import AWSAgent

def main():
    agent = AWSAgent(region_name="eu-west-3")
    print("AWS Agent (Available)")

    while True:
        command = input("\n💬 Enter AWS command (or type 'exit'): ")
        if command.lower() == 'exit':
            break

        try:
            result = agent.execute_command(command)
        except Exception as e:
            print("❌❌❌ Error:", str(e))

if __name__ == "__main__":
    main()


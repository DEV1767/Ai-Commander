from src.incident_analyzer.graph import build_graph

if __name__ == "__main__":
    app = build_graph()

    with open("sample_log.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    initial_state = {
        "raw_text": raw_text,
    }

    result = app.invoke(initial_state)

    print(result)
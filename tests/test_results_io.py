from src.results_io import load_json, save_json


def test_save_and_load_json(tmp_path):
    results = [{"bits": 64, "n": 2 ** 64 + 1, "times_s": [0.1, 0.2]}]  # big ints must survive
    path = save_json("demo", {"repeats": 2}, results, tmp_path)
    data = load_json(path)
    assert path.name == "demo.json"
    assert data["experiment"] == "demo"
    assert data["parameters"] == {"repeats": 2}
    assert data["results"] == results
    assert {"date", "os", "processor", "python"} <= set(data["machine"])

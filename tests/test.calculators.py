import messy_project_hakeem.src.calculator as calculator

def test_add():
    assert calculator.Add(2, 3) == 5

def test_sub():
    assert calculator.subTract(5, 3) == 2

import app

def test_completion():
    result_should_be ={'expected': ' It was a dark and stormy night.', 'newEnglish': ' The night was dark and stormy.', 'predictions': [['\xa0', '\xa0It', '\xa0"', '\xa0-', '\xa0*', '\xa0♫', '\xa0it', '\xa0The', '\xa0A', '\xa0This'], ['\xa0night', '\xa0evening', '\xa0day', '\xa0nights', '\xa0darkness', '\xa0dark', '\xa0time', '\xa0whole', '\xa0Night', '\xa0place'], ['\xa0was', '\xa0is', '\xa0had', '\xa0of', ',', '\xa0it', '\xa0came', '\xa0in', '\xa0has', '\xa0I'], ['\xa0dark', '\xa0a', '\xa0black', '\xa0so', '\xa0darkness', '\xa0both', '\xa0night', '\xa0deep', '\xa0', '\xa0long'], ['\xa0and', ',', '.', '...', 'er', '\xa0with', '\xa0or', ';', '\xa0in', 'est'], ['\xa0storm', '\xa0temp', '\xa0thunder', '\xa0a', '\xa0rainy', '\xa0heavy', '\xa0has', '\xa0severe', '\xa0', '\xa0was'], ['y', 'ful', '.', 'ous', 'ily', 'ier', 'ly', 'ing', 'iness', 'some'], ['.', '</s>', ',', '!', ';', '\xa0and', '...', ':', '."', '\xa0'], ['</s>', '\xa0"', '\xa0—', "\xa0'", '\xa0It', '\xa0I', '\xa0-', '\xa0', '.', '...']], 'score': -0.801, 'tokens': ['\xa0The', '\xa0night', '\xa0was', '\xa0dark', '\xa0and', '\xa0storm', 'y', '.', '</s>'], 'translation': ' The night was dark and stormy.'}

    with app.app.test_client() as client:
        response = client.get('/result?english=It+was+a+dark+and+stormy+night.&start=+The+night&skip=true&copy=false')
        print(response.get_json())
        assert response.get_json() == result_should_be
        print("passed")

def test_alternatives():
    result_should_be = {
        "alternatives": [
            " The night was dark and stormy.", 
            " And it was a dark and stormy night.", 
            " A dark and stormy night.", 
            " Dark and stormy night."
        ]}
    with app.app.test_client() as client:
        response = client.get('/rearrange?english=It+was+a+dark+and+stormy+night.&start=&auto=true')
        print(response.get_json())
        assert response.get_json() == result_should_be
        print("passed")

def test_reorder():
    result_should_be = {'expected': ' It was a dark and stormy night.', 'newEnglish': ' The night was dark and stormy.', 'predictions': [['\xa0', '\xa0It', '\xa0"', '\xa0-', '\xa0*', '\xa0♫', '\xa0it', '\xa0The', '\xa0A', '\xa0This'], ['\xa0night', '\xa0evening', '\xa0day', '\xa0nights', '\xa0darkness', '\xa0dark', '\xa0time', '\xa0whole', '\xa0Night', '\xa0place'], ['\xa0was', '\xa0is', '\xa0had', '\xa0of', ',', '\xa0it', '\xa0came', '\xa0in', '\xa0has', '\xa0I'], ['\xa0dark', '\xa0a', '\xa0black', '\xa0so', '\xa0darkness', '\xa0both', '\xa0night', '\xa0deep', '\xa0', '\xa0long'], ['\xa0and', ',', '.', '...', 'er', '\xa0with', '\xa0or', ';', '\xa0in', 'est'], ['\xa0storm', '\xa0temp', '\xa0thunder', '\xa0a', '\xa0rainy', '\xa0heavy', '\xa0has', '\xa0severe', '\xa0', '\xa0was'], ['y', 'ful', '.', 'ous', 'ily', 'ier', 'ly', 'ing', 'iness', 'some'], ['.', '</s>', ',', '!', ';', '\xa0and', '...', ':', '."', '\xa0'], ['</s>', '\xa0"', '\xa0—', "\xa0'", '\xa0It', '\xa0I', '\xa0-', '\xa0', '.', '...']], 'score': -0.801, 'tokens': ['\xa0The', '\xa0night', '\xa0was', '\xa0dark', '\xa0and', '\xa0storm', 'y', '.', '</s>'], 'translation': ' The night was dark and stormy.'}
    
    with app.app.test_client() as client:
        response = client.get('/rearrange?english=+It+was+a+dark+and+stormy+night.&start=%C2%A0night&auto=false')
        print(response.get_json())
        assert response.get_json() == result_should_be
        print("passed")

test_completion()
test_alternatives()
test_reorder()


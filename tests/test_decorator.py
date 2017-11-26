from rampante import decorator


def test_decorator_with_one_function():

    @decorator.subscribe_on("my_event")
    def test():
        pass

    assert 'my_event' in decorator._subscribers
    assert decorator._subscribers['my_event'][0] is test


def test_decorator_more_functions():

    @decorator.subscribe_on("first_event")
    def test_1():
        pass

    @decorator.subscribe_on("first_event", "second_event")
    def test_2():
        pass

    assert 'first_event' in decorator._subscribers
    assert 'second_event' in decorator._subscribers

    assert test_1 in decorator._subscribers['first_event']
    assert test_2 in decorator._subscribers['first_event']

    assert test_1 not in decorator._subscribers['second_event']
    assert test_2 in decorator._subscribers['second_event']

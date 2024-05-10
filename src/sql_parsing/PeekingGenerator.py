class PeekingGenerator:
    __has_cached = False
    __peeked_value = None
    def __init__(self, generator):
        self.__generator = generator;

    def peek(self):
        if not self.__has_cached:
            self.__peeked_value = next(self.__generator)
            self.__has_cached = True

        return self.__peeked_value

    def __next__(self):
        if self.__has_cached:
            self.__has_cached = False
            return self.__peeked_value

        return next(self.__generator)


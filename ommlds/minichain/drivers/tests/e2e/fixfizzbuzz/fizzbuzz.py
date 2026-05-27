def fizzbuzz(n=100):
    for i in range(1, n + 1):
        # Subtle bug: forgot "== 0" on the second check. Because "i % 5" is truthy for non-multiples of 5 and falsy for
        # multiples, this line wrongly prints "FizzBuzz" for multiples of 3 that are NOT multiples of 5, and fails to
        # print "FizzBuzz" for 15, 30, etc.
        if i % 3 == 0 and i % 5:  # BUG: should be "i % 3 == 0 and i % 5 == 0"
            print('FizzBuzz')
        elif i % 3 == 0:
            print('Fizz')
        elif i % 5 == 0:
            print('Buzz')
        else:
            print(i)


if __name__ == '__main__':
    fizzbuzz()

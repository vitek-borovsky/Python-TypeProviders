class A:
    def __del__(self):
        print("destr called")

a = A()
print("some operation")

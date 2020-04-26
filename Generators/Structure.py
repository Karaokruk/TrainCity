class Structure:

    h_min = h_max = x_min = x_max = z_min = z_max = 0

    def __init__(self):
        if type(self) is Structure:
            raise Exception("Structure is an abstract class, instead instantiate a child class.")
        print("Je suis dans Structure")

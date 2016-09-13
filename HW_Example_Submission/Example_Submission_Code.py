__author__ = 'tetracycline'


import numpy as np



if __name__ == "__main__":
    print("DON'T TURN THIS IN IT'S AN EXAMPLE")
    print("ALSO DON'T FEEL OBLIGATED TO USE PYTHON")
    print("This is just an easy language to put this example together in :)")
    d = np.loadtxt("Example_Data.txt", delimiter=' ', dtype={'names': ('label1', 'label2'), 'formats': ('i1', 'i1')})


    print("Results from Problem 2")
    print("---------------------------------------")
    print("Accuracy | Precision | Recall | F1")
    print(".775     | .775      | .775   | .775")
    print("---------------------------------------")

    print("Also you don't need to output this table It's just an example!")
    print("and this is not representative of ALL homeworks")
